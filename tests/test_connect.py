import pytest
import pypuppetdb


def test_connect_unknown_api_version():
    with pytest.raises(pypuppetdb.errors.UnsupportedVersionError):
        pypuppetdb.connect(api_version=1)


def test_connect_api_v3():
    puppetdb = pypuppetdb.connect(api_version=3)
    assert puppetdb.version == 'v3'


def test_connect_api_v4():
    puppetdb = pypuppetdb.connect(api_version=4)
    assert puppetdb.version == 'v4'
