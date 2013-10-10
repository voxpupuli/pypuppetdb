import pytest
from pypuppetdb import connect


# Set up our API objects
@pytest.fixture(scope='session')
def api2():
    """Set up a connection to PuppetDB with API version 2."""
    puppetdb = connect(api_version=2)
    return puppetdb


@pytest.fixture(scope='session')
def api3():
    """Set up a connection to PuppetDB with API version 3."""
    puppetdb = connect(api_version=3)
    return puppetdb
