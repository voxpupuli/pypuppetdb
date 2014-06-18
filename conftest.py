import pytest
import pypuppetdb


# Set up our API objects
@pytest.fixture(scope='session')
def api2():
    """Set up a connection to PuppetDB with API version 2."""
    return pypuppetdb.connect(api_version=2)


@pytest.fixture(scope='session')
def api3():
    """Set up a connection to PuppetDB with API version 3."""
    return pypuppetdb.connect(api_version=3)


class TestAPI(pypuppetdb.api.BaseAPI):
    api_version = 3


@pytest.fixture
def baseapi():
    return TestAPI()


@pytest.fixture
def utc():
    """Create a UTC object."""
    return pypuppetdb.utils.UTC()
