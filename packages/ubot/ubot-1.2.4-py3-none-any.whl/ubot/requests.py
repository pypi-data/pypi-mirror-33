import certifi

import urllib3


def get_pool_manager() -> urllib3.PoolManager:
    return urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )
