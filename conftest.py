import pytest
from pypuppetdb import connect


# Set up our API objects
@pytest.fixture(scope='session')
def api2():
    """Set up a connection to PuppetDB with API version 2."""
    puppetdb = connect()
    return puppetdb


@pytest.fixture(scope='session')
def api2e():
    """Set up a connection to PuppetDB with API version 2 and experimental
    features enabled."""
    puppetdb = connect(experimental=True)
    return puppetdb
