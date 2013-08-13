import pytest
from pypuppetdb.errors import UnsupportedVersionError
from pypuppetdb import connect

pytestmark = pytest.mark.unit


def test_connect_unknown_api_version():
    with pytest.raises(UnsupportedVersionError):
        connect(api_version=1)
