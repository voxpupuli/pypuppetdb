import base64
import json

import httpretty
import pytest
import requests

from unittest import mock

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


class TestBaseAPIQuery(object):
    @mock.patch.object(requests.Session, 'request')
    def test_timeout(self, get, api):
        get.side_effect = requests.exceptions.Timeout
        with pytest.raises(requests.exceptions.Timeout):
            api._query('nodes')
        with pytest.raises(requests.exceptions.Timeout):
            api._cmd('deactivate node', {'certname': ''})

    @mock.patch.object(requests.Session, 'request')
    def test_connectionerror(self, get, api):
        get.side_effect = requests.exceptions.ConnectionError
        with pytest.raises(requests.exceptions.ConnectionError):
            api._query('nodes')
        with pytest.raises(requests.exceptions.ConnectionError):
            api._cmd('deactivate node', {'certname': ''})

    @mock.patch.object(requests.Session, 'request')
    def test_httperror(self, get, api):
        get.side_effect = requests.exceptions.HTTPError(
            response=requests.Response())
        with pytest.raises(requests.exceptions.HTTPError):
            api._query('nodes')
        with pytest.raises(requests.exceptions.HTTPError):
            api._cmd('deactivate node', {'certname': ''})

    def test_setting_headers_without_token(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes')  # need to query some endpoint
        request_headers = dict(httpretty.last_request().headers)
        assert request_headers['accept'] == 'application/json'
        assert request_headers['content-type'] == 'application/json'
        assert request_headers['accept-charset'] == 'utf-8'
        host_val = request_headers.get('host', request_headers.get('Host'))
        assert host_val == 'localhost:8080'
        assert httpretty.last_request().path == '/pdb/query/v4/nodes'
        httpretty.disable()
        httpretty.reset()

    def test_setting_headers_with_token(self, token_api):
        httpretty.enable()
        stub_request('https://localhost:8080/pdb/query/v4/nodes')
        token_api._query('nodes')  # need to query some endpoint
        request_headers = dict(httpretty.last_request().headers)
        print(request_headers)
        assert request_headers['accept'] == 'application/json'
        assert request_headers['content-type'] == 'application/json'
        assert request_headers['accept-charset'] == 'utf-8'
        host_val = request_headers.get('host', request_headers.get('Host'))
        assert host_val == 'localhost:8080'
        x_val = request_headers.get('X-Authentication',
                                    request_headers.get('x-authentication'))
        assert x_val == 'tokenstring'
        assert httpretty.last_request().path == '/pdb/query/v4/nodes'
        httpretty.disable()
        httpretty.reset()

    def test_with_path(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes/node1')
        api._query('nodes', path='node1')
        assert httpretty.last_request().path == '/pdb/query/v4/nodes/node1'
        httpretty.disable()
        httpretty.reset()

    def test_with_url_path(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/puppetdb/pdb/query/v4/nodes')
        api.url_path = '/puppetdb'
        api._query('nodes')
        assert httpretty.last_request().path == '/puppetdb/pdb/query/v4/nodes'
        httpretty.disable()
        httpretty.reset()

    def test_with_password_authorization(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api.session.auth = ('puppetdb', 'password123')
        api._query('nodes')
        assert httpretty.last_request().path == '/pdb/query/v4/nodes'
        encoded_cred = 'puppetdb:password123'.encode('utf-8')
        bs_authheader = base64.b64encode(encoded_cred).decode('utf-8')
        assert httpretty.last_request().headers['Authorization'] == \
            'Basic {0}'.format(bs_authheader)
        httpretty.disable()
        httpretty.reset()

    def test_with_token_authorization(self, token_api):
        httpretty.enable()
        stub_request('https://localhost:8080/pdb/query/v4/nodes')
        token_api._query('nodes')
        assert httpretty.last_request().path == '/pdb/query/v4/nodes'
        assert httpretty.last_request().headers['X-Authentication'] == \
            'tokenstring'

    def test_with_query(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes', query='["certname", "=", "node1"]')
        assert httpretty.last_request().querystring == {
            'query': ['["certname", "=", "node1"]']}
        httpretty.disable()
        httpretty.reset()

    def test_with_order(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes', order_by='ted')
        assert httpretty.last_request().querystring == {
            'order_by': ['ted']}
        httpretty.disable()
        httpretty.reset()

    def test_with_limit(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes', limit=1)
        assert httpretty.last_request().querystring == {
            'limit': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_include_total(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes', include_total=True)
        assert httpretty.last_request().querystring == {
            'include_total': ['true']}
        httpretty.disable()
        httpretty.reset()

    def test_with_offset(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes', offset=1)
        assert httpretty.last_request().querystring == {
            'offset': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_summarize_by(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes', summarize_by=1)
        assert httpretty.last_request().querystring == {
            'summarize_by': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_count_by(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes', count_by=1)
        assert httpretty.last_request().querystring == {
            'count_by': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_count_filter(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes', count_filter=1)
        assert httpretty.last_request().querystring == {
            'counts_filter': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_payload_get(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        api._query('nodes',
                   payload={'foo': 'bar'},
                   count_by=1)
        assert httpretty.last_request().querystring == {
            'foo': ['bar'],
            'count_by': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_payload_post(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes',
                     method=httpretty.POST)
        api._query('nodes',
                   payload={'foo': 'bar'},
                   count_by=1,
                   request_method='POST')
        assert httpretty.last_request().body == json.dumps({'foo': 'bar',
                                                            'count_by': 1}).encode("latin-1")
        httpretty.disable()
        httpretty.reset()

    def test_response_empty(self, api):
        httpretty.enable()
        httpretty.register_uri(httpretty.GET,
                               'http://localhost:8080/pdb/query/v4/nodes',
                               body=json.dumps(None))
        with pytest.raises(pypuppetdb.errors.EmptyResponseError):
            api._query('nodes')

    def test_response_x_records(self, api):
        httpretty.enable()
        httpretty.register_uri(httpretty.GET,
                               'http://localhost:8080/pdb/query/v4/nodes',
                               adding_headers={
                                   'X-Records': 256},
                               body='[]',
                               )
        api._query('nodes', include_total=True)
        assert api.total == 256

    def test_query_bad_request_type(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        with pytest.raises(pypuppetdb.errors.APIError):
            api._query('nodes',
                       query='["certname", "=", "node1"]',
                       request_method='DELETE')
        httpretty.disable()
        httpretty.reset()

    def test_query_with_post(self, api, query):
        httpretty.reset()
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes',
                     method=httpretty.POST)
        api._query('nodes',
                   query=query,
                   count_by=1,
                   request_method='POST')
        last_request = httpretty.last_request()
        assert last_request.querystring == {}
        assert last_request.headers['Content-Type'] == 'application/json'
        assert last_request.method == 'POST'
        assert last_request.body == json.dumps({'query': str(query),
                                                'count_by': 1}).encode("latin-1")
        httpretty.disable()
        httpretty.reset()
