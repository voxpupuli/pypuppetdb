import pytest
import pypuppetdb


# Set up our API objects
@pytest.fixture(scope='session')
def api3():
    """Set up a connection to PuppetDB with API version 3."""
    return pypuppetdb.connect(api_version=3)


@pytest.fixture(scope='session')
def api4():
    """Set up a connection to PuppetDB with API version 4."""
    return pypuppetdb.connect(api_version=4)


@pytest.fixture
def baseapi():
    return pypuppetdb.api.BaseAPI(4)


@pytest.fixture
def utc():
    """Create a UTC object."""
    return pypuppetdb.utils.UTC()
