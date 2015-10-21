import pytest
import pypuppetdb


def test_connect_api():
    puppetdb = pypuppetdb.connect()
    assert puppetdb.version == 'v4'
