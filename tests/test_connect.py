from unittest import mock

import pypuppetdb


@mock.patch("pypuppetdb.api.base.requests.Session.close")
def test_connect_api(session_close):
    puppetdb = pypuppetdb.connect()
    assert puppetdb.version == "v4"

    puppetdb.disconnect()
    assert session_close.called


@mock.patch("pypuppetdb.api.base.requests.Session.close")
def test_connect_with_statement(session_close):
    with pypuppetdb.connect() as puppetdb:
        assert puppetdb.version == "v4"

    assert session_close.called
