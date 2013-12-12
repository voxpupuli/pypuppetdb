import json
import mock
import httpretty
import pytest
import requests
import pypuppetdb


def stub_request(url, data=None, **kwargs):
    if data is None:
        body = '[]'
    else:
        with open(data, 'r') as d:
            body = json.load(d.read())
    return httpretty.register_uri(httpretty.GET, url, body=body, status=200,
                                  **kwargs)


class TestBaseAPIVersion(object):
    def test_init_v2_defaults(self):
        v2 = pypuppetdb.api.BaseAPI(2)
        assert v2.api_version == 'v2'

    def test_init_v3_defaults(self):
        v3 = pypuppetdb.api.BaseAPI(3)
        assert v3.api_version == 'v3'

    def test_init_invalid_version(self):
        with pytest.raises(pypuppetdb.errors.UnsupportedVersionError):
            vderp = pypuppetdb.api.BaseAPI(10000)


class TestBaseAPIInitOptions(object):
    def test_defaults(self, baseapi):
        assert baseapi.host == 'localhost'
        assert baseapi.port == 8080
        assert baseapi.ssl_verify is True
        assert baseapi.ssl_key is None
        assert baseapi.ssl_cert is None
        assert baseapi.timeout == 10
        assert baseapi.protocol == 'http'

    def test_host(self):
        api = pypuppetdb.api.BaseAPI(3, host='127.0.0.1')
        assert api.host == '127.0.0.1'

    def test_port(self):
        api = pypuppetdb.api.BaseAPI(3, port=8081)
        assert api.port == 8081

    def test_ssl_verify(self):
        api = pypuppetdb.api.BaseAPI(3, ssl_verify=False)
        assert api.ssl_verify is False
        assert api.protocol == 'http'

    def test_ssl_key(self):
        api = pypuppetdb.api.BaseAPI(3, ssl_key='/a/b/c.pem')
        assert api.ssl_key == '/a/b/c.pem'
        assert api.protocol == 'http'

    def test_ssl_cert(self):
        api = pypuppetdb.api.BaseAPI(3, ssl_cert='/d/e/f.pem')
        assert api.ssl_cert == '/d/e/f.pem'
        assert api.protocol == 'http'

    def test_ssl_key_and_cert(self):
        api = pypuppetdb.api.BaseAPI(3, ssl_cert='/d/e/f.pem',
                                     ssl_key='/a/b/c.pem')
        assert api.ssl_key == '/a/b/c.pem'
        assert api.ssl_cert == '/d/e/f.pem'
        assert api.protocol == 'https'

    def test_timeout(self):
        api = pypuppetdb.api.BaseAPI(3, timeout=20)
        assert api.timeout == 20


class TestBaseAPIProperties(object):
    def test_version(self, baseapi):
        assert baseapi.version == 'v3'

    def test_base_url(self, baseapi):
        assert baseapi.base_url == 'http://localhost:8080'

    def test_base_url_ssl(self, baseapi):
        baseapi.protocol = 'https'  # slightly evil
        assert baseapi.base_url == 'https://localhost:8080'

    def test_total(self, baseapi):
        baseapi.last_total = 10  # slightly evil
        assert baseapi.total == 10


class TestBaseAPIURL(object):
    def test_without_path(self, baseapi):
        assert baseapi._url('nodes') == 'http://localhost:8080/v3/nodes'

    def test_with_invalid_endpoint(self, baseapi):
        with pytest.raises(pypuppetdb.errors.APIError):
            baseapi._url('this_will-Never+Ex1s7')

    def test_with_path(self, baseapi):
        url = baseapi._url('nodes', path='node1.example.com')
        assert url == 'http://localhost:8080/v3/nodes/node1.example.com'


class TesteAPIQuery(object):
    @mock.patch.object(requests, 'get')
    def test_timeout(self, get, baseapi):
        get.side_effect = requests.exceptions.Timeout
        with pytest.raises(requests.exceptions.Timeout):
            baseapi._query('nodes')

    @mock.patch.object(requests, 'get')
    def test_connectionerror(self, get, baseapi):
        get.side_effect = requests.exceptions.ConnectionError
        with pytest.raises(requests.exceptions.ConnectionError):
            baseapi._query('nodes')

    @mock.patch.object(requests, 'get')
    def test_httperror(self, get, baseapi):
        get.side_effect = requests.exceptions.HTTPError(
            response=requests.Response())
        with pytest.raises(requests.exceptions.HTTPError):
            baseapi._query('nodes')

    def test_setting_headers(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes')  # need to query some endpoint
        request_headers = dict(httpretty.last_request().headers)
        assert request_headers['accept'] == 'application/json'
        assert request_headers['content-type'] == 'application/json'
        assert request_headers['accept-charset'] == 'utf-8'
        assert request_headers['host'] == 'localhost:8080'
        assert httpretty.last_request().path == '/v3/nodes'
        httpretty.disable()
        httpretty.reset()

    def test_with_path(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes/node1')
        baseapi._query('nodes', path='node1')
        assert httpretty.last_request().path == '/v3/nodes/node1'
        httpretty.disable()
        httpretty.reset()

    def test_with_query(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes', query='["certname", "=", "node1"]')
        assert httpretty.last_request().querystring == {
            'query': ['["certname", "=", "node1"]']}
        httpretty.disable()
        httpretty.reset()

    def test_with_order(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes', order_by='ted')
        assert httpretty.last_request().querystring == {
            'order-by': ['ted']}
        httpretty.disable()
        httpretty.reset()

    def test_with_limit(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes', limit=1)
        assert httpretty.last_request().querystring == {
            'limit': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_include_total(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes', include_total=True)
        assert httpretty.last_request().querystring == {
            'include-total': ['true']}
        httpretty.disable()
        httpretty.reset()

    def test_with_offset(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes', offset=1)
        assert httpretty.last_request().querystring == {
            'offset': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_summarize_by(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes', summarize_by=1)
        assert httpretty.last_request().querystring == {
            'summarize-by': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_count_by(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes', count_by=1)
        assert httpretty.last_request().querystring == {
            'count-by': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_count_filter(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/nodes')
        baseapi._query('nodes', count_filter=1)
        assert httpretty.last_request().querystring == {
            'count-filter': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_response_empty(self, baseapi):
        httpretty.enable()
        httpretty.register_uri(httpretty.GET, 'http://localhost:8080/v3/nodes',
                               body=json.dumps(None))
        with pytest.raises(pypuppetdb.errors.EmptyResponseError):
            baseapi._query('nodes')

    def test_response_x_records(self, baseapi):
        httpretty.enable()
        httpretty.register_uri(httpretty.GET, 'http://localhost:8080/v3/nodes',
                               adding_headers={
                                   'X-Records': 256},
                               body='[]',
                               )
        baseapi._query('nodes', include_total=True)
        assert baseapi.total == 256


class TestAPIMethods(object):
    def test_nodes(self, baseapi):
        with pytest.raises(NotImplementedError):
            baseapi.nodes()

    def test_node(self, baseapi):
        with pytest.raises(NotImplementedError):
            baseapi.node()

    def test_facts(self, baseapi):
        with pytest.raises(NotImplementedError):
            baseapi.facts()

    def test_resources(self, baseapi):
        with pytest.raises(NotImplementedError):
            baseapi.resources()

    def test_metric(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/v3/metrics/mbean/test')
        baseapi.metric('test')
        assert httpretty.last_request().path == '/v3/metrics/mbean/test'
        httpretty.disable()
        httpretty.reset()
