import warnings
from functools import partial
from typing import Dict

from aiohttp import ClientSession, ClientRequest
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
from yarl import URL

from sieve.sdk import config


class ProxiedRequest(ProxyClientRequest):
    def __init__(self, method, url, *,
                 proxy=None,
                 proxy_address=None,
                 **kwargs):
        if proxy is None:
            proxy = proxy_address

        super(ProxiedRequest, self).__init__(method,
                                             url,
                                             proxy=URL(proxy),
                                             **kwargs)


class Socks5ProxiedClientSession(ClientSession):
    default_connector_kwargs = {
        'limit': config.MAX_CONCURRENT_REQUESTS,
        'limit_per_host': config.MAX_CONCURRENT_REQUESTS_PER_HOST
    }

    """
    An aiohttp.ClientSession mixin that provides transparent socks5 proxy
    integration
    """

    def __init__(self, *,
                 connector=None,
                 connector_kwargs: Dict=None,
                 request_class: ClientRequest=None,
                 proxy_address: str=None,
                 remote_resolve: bool=None,
                 **kwargs):
        """
        :type proxy_address: str
        :param proxy_address: Address of the proxy to be used.
        Ex.:
            Socks5ProxiedClientSession(proxy_address='socks5://127.0.0.1:8080')
            Socks5ProxiedClientSession(proxy_address='http://127.0.0.1:1080')

        :param remote_resolve: Whether or not to do local domain name resolving
        :type remote_resolve: bool
        """
        if proxy_address is None:
            warnings.warn("Creating a session without explicitly "
                          "calling it with proxy_address. Using default.")
            proxy_address = config.PROXY_ADDRESS
        self.proxy_address = proxy_address

        if remote_resolve is None:
            remote_resolve = config.PROXY_SHOULD_REMOTE_RESOLVE
        self.remote_resolve = remote_resolve

        if connector_kwargs is None:
            connector_kwargs = self.default_connector_kwargs
        if connector is None:
            connector = ProxyConnector(remote_resolve=remote_resolve,
                                       **connector_kwargs)

        if request_class is None:
            request_class = partial(ProxiedRequest,
                                    proxy_address=self.proxy_address)

        super().__init__(connector=connector,
                         request_class=request_class,
                         **kwargs)
