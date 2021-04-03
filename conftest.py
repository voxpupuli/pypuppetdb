import pytest
import pypuppetdb


# Set up our API objects
@pytest.fixture
def api():
    return pypuppetdb.api.API()


@pytest.fixture
def token_api():
    return pypuppetdb.api.API(token='tokenstring')


@pytest.fixture
def utc():
    """Create a UTC object."""
    return pypuppetdb.utils.UTC()
