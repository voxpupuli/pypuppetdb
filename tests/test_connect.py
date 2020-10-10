import pypuppetdb


def test_connect_api():
    puppetdb = pypuppetdb.connect()
    assert puppetdb.version == 'v4'


def test_connect_with_statement():
    with pypuppetdb.connect() as puppetdb:
        assert puppetdb.version == 'v4'
