from sieve.sdk import config


class BaseClientSession:
    connection_kwargs = {
        'limit': config.MAX_CONCURRENT_REQUESTS,
        'limit_per_host': config.MAX_CONCURRENT_REQUESTS_PER_HOST
    }
