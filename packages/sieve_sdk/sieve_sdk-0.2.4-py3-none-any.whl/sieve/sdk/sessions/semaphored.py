import asyncio
from typing import Dict

from aiohttp import ClientSession, TCPConnector
from sieve.sdk import config


class SemaphoredClientSession(ClientSession):
    default_connector_kwargs = {
        'limit': config.MAX_CONCURRENT_REQUESTS,
        'limit_per_host': config.MAX_CONCURRENT_REQUESTS_PER_HOST
    }

    def __init__(self, *,
                 connector=None,
                 connector_kwargs: Dict=None,
                 **kwargs):
        """
        A subclass of aiohttp's ClientSession which provides the possibility of
        limiting concurrent requests to some urls, based on a definition of an
        url prefix and a value to be limit concurrent requests.

        :param semaphores: An iterable of tuples (URL prefix, Semaphore value)
        to be be used by the session.
        :type semaphores: Iterable[Tuple[str, int]]
        :param connector_kwargs: A dict of keyword arguments to be passed to
        the ClientSession TCPConnector. By default, aiohttp creates a
        connector that limits concurrent connections to `100`. That limitation
        can also be overwritten by setting a new integer value to the
        environment variable `SIEVE_SDK_MAX_CONCURRENT_REQUESTS`.
        :type connector_kwargs: dict
        """
        semaphores = kwargs.pop('semaphores', [])

        if connector_kwargs is None:
            connector_kwargs = self.default_connector_kwargs
        if connector is None:
            connector = TCPConnector(**connector_kwargs)

        super().__init__(connector=connector, **kwargs)

        semaphore_value = config.MAX_CONCURRENT_REQUESTS
        self._default_semaphore = asyncio.Semaphore(semaphore_value)

        self._semaphores = tuple(
            (url_prefix, asyncio.Semaphore(value))
            for url_prefix, value in semaphores
        )

    async def _request(self, method, url, *args, **kwargs):
        semaphore = self.get_semaphore(url)
        async with semaphore:
            return await super()._request(method, url, *args, **kwargs)

    def get_semaphore(self, url: str) -> asyncio.Semaphore:
        for url_prefix, semaphore in self._semaphores:
            if url.startswith(url_prefix):
                return semaphore
        return self._default_semaphore
