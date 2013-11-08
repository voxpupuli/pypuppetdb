import pytest
from pypuppetdb.errors import UnsupportedVersionError
from pypuppetdb import connect

pytestmark = pytest.mark.unit


def test_connect_unknown_api_version():
    with pytest.raises(UnsupportedVersionError):
        connect(api_version=1)


def test_connect_api_v2():
    puppetdb = connect(api_version=2)
    assert puppetdb.version == 'v2'


def test_connect_api_v3():
    puppetdb = connect(api_version=3)
    print puppetdb
    print puppetdb.version
    assert puppetdb.version == 'v3'
