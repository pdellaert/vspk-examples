import pytest
import sys
from vspk import v6 as vsdk

@pytest.fixture(scope="session")
def nuage_connection():
    api_url = 'https://localhost:443'
    username = 'csproot'
    password = 'csproot'
    enterprise = 'csp'

    nuage_connection = vsdk.NUVSDSession(api_url=api_url, username=username, password=password, enterprise=enterprise)
    nuage_connection.start()
    return nuage_connection

@pytest.fixture(scope="session")
def async_arg():
    if sys.version_info >= (3,7):
        async_arg = { 'as_async': True }
    else: 
        async_arg = { 'async': True }
    return async_arg

