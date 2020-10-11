import mock

import pypuppetdb


def test_connect_api():
    puppetdb = pypuppetdb.connect()
    assert puppetdb.version == 'v4'


@mock.patch('pypuppetdb.api.requests.Session.close')
def test_connect_with_statement(session_close):
    with pypuppetdb.connect() as puppetdb:
        assert puppetdb.version == 'v4'

    assert session_close.called
