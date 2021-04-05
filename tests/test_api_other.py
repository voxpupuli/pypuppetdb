import json

import httpretty
import pytest

import pypuppetdb


def stub_request(url, data=None, method=httpretty.GET, status=200, **kwargs):
    if data is None:
        body = '[]'
    else:
        with open(data, 'r') as d:
            body = json.load(d.read())
    return httpretty.register_uri(method, url, body=body, status=status,
                                  **kwargs)


@pytest.fixture(params=['string', 'QueryBuilder'])
def query(request):
    key = 'certname'
    value = 'node1'
    if request.param == 'string':
        return '["{0}", "=", "{1}"]'.format(key, value)
    elif request.param == 'QueryBuilder':
        return pypuppetdb.QueryBuilder.EqualsOperator(key, value)


class TestCmdAPI(object):

    def test_command(self, api):
        httpretty.enable()
        stub_request(
            'http://localhost:8080/pdb/cmd/v1',
            method=httpretty.POST
        )
        api.command('deactivate node', {'certname': 'testnode'})
        assert httpretty.last_request().path.startswith(
            '/pdb/cmd/v1'
        )
        httpretty.disable()
        httpretty.reset()

    def test_cmd(self, api, query):
        httpretty.reset()
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/cmd/v1',
                     method=httpretty.POST)
        node_name = 'testnode'
        api._cmd('deactivate node', {'certname': node_name})
        last_request = httpretty.last_request()
        assert last_request.querystring == {
            "certname": [node_name],
            "command": ['deactivate node'],
            "version": ['3'],
            "checksum": ['b93d474970e54943aec050ee399dfb85d21e143a']
        }
        assert last_request.headers['Content-Type'] == 'application/json'
        assert last_request.method == 'POST'
        assert last_request.body == json.dumps({'certname': node_name}).encode("latin-1")
        httpretty.disable()
        httpretty.reset()

    def test_cmd_bad_command(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/cmd/v1')
        with pytest.raises(pypuppetdb.errors.APIError):
            api._cmd('incorrect command', {})
        httpretty.disable()
        httpretty.reset()

    def test_cmd_with_token_authorization(self, token_api):
        httpretty.enable()
        stub_request('https://localhost:8080/pdb/cmd/v1',
                     method=httpretty.POST)
        token_api._cmd('deactivate node', {'certname': ''})
        assert httpretty.last_request().path.startswith('/pdb/cmd/v1')
        assert httpretty.last_request().headers['X-Authentication'] == \
            'tokenstring'


class TestStatusAPI(object):

    def test_status(self, api):
        httpretty.enable()
        stub_request(
            'http://localhost:8080/status/v1/services/puppetdb-status'
        )
        api.status()
        assert httpretty.last_request().path == \
            '/status/v1/services/puppetdb-status'
        httpretty.disable()
        httpretty.reset()
