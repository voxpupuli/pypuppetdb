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


class TestAPIVersion(object):
    def test_init_defaults(self):
        v4 = pypuppetdb.api.API()
        assert v4.api_version == 'v4'


class TestAPIInitOptions(object):
    def test_defaults(self, api):
        assert api.host == 'localhost'
        assert api.port == 8080
        assert api.ssl_verify is True
        assert api.ssl_key is None
        assert api.ssl_cert is None
        assert api.timeout == 10
        assert api.token is None
        assert api.protocol == 'http'
        assert api.url_path == ''
        assert api.session.auth is None
        assert api.metric_api_version is 'v2'

    def test_host(self):
        api = pypuppetdb.api.API(host='127.0.0.1')
        assert api.host == '127.0.0.1'

    def test_port(self):
        api = pypuppetdb.api.API(port=8081)
        assert api.port == 8081

    def test_ssl_verify(self):
        api = pypuppetdb.api.API(ssl_verify=False)
        assert api.ssl_verify is False
        assert api.protocol == 'http'

    def test_token(self):
        test_token = 'tokenstring'  # nosec
        api = pypuppetdb.api.API(token=test_token)
        assert api.token == test_token
        assert api.protocol == 'https'

    def test_ssl_key(self):
        api = pypuppetdb.api.API(ssl_key='/a/b/c.pem')
        assert api.ssl_key == '/a/b/c.pem'
        assert api.protocol == 'http'

    def test_ssl_cert(self):
        api = pypuppetdb.api.API(ssl_cert='/d/e/f.pem')
        assert api.ssl_cert == '/d/e/f.pem'
        assert api.protocol == 'http'

    def test_ssl_key_and_cert(self):
        api = pypuppetdb.api.API(ssl_cert='/d/e/f.pem',
                                 ssl_key='/a/b/c.pem')
        assert api.ssl_key == '/a/b/c.pem'
        assert api.ssl_cert == '/d/e/f.pem'
        assert api.protocol == 'https'

    def test_timeout(self):
        api = pypuppetdb.api.API(timeout=20)
        assert api.timeout == 20

    def test_protocol(self):
        api = pypuppetdb.api.API(protocol='https')
        assert api.protocol == 'https'

    def test_uppercase_protocol(self):
        api = pypuppetdb.api.API(protocol='HTTP')
        assert api.protocol == 'http'

    def test_override_protocol(self):
        api = pypuppetdb.api.API(protocol='http',
                                 ssl_cert='/d/e/f.pem',
                                 ssl_key='/a/b/c.pem')
        assert api.protocol == 'http'

    def test_invalid_protocol(self):
        with pytest.raises(ValueError):
            api = pypuppetdb.api.API(protocol='ftp')

    def test_url_path(self):
        api = pypuppetdb.api.API(url_path='puppetdb')
        assert api.url_path == '/puppetdb'

    def test_url_path_leading_slash(self):
        api = pypuppetdb.api.API(url_path='/puppetdb')
        assert api.url_path == '/puppetdb'

    def test_url_path_trailing_slash(self):
        api = pypuppetdb.api.API(url_path='puppetdb/')
        assert api.url_path == '/puppetdb'

    def test_url_path_longer_with_both_slashes(self):
        api = pypuppetdb.api.API(url_path='/puppet/db/')
        assert api.url_path == '/puppet/db'

    def test_username(self):
        api = pypuppetdb.api.API(username='puppetdb')
        assert api.session.auth is None

    def test_password(self):
        api = pypuppetdb.api.API(password='password123')  # nosec
        assert api.session.auth is None

    def test_username_and_password(self):
        api = pypuppetdb.api.API(username='puppetdb',  # nosec
                                 password='password123')
        assert api.session.auth == ('puppetdb', 'password123')

    def test_metric_api_version_v1(self):
        api = pypuppetdb.api.API(metric_api_version='v1')
        assert api.metric_api_version == 'v1'

    def test_metric_api_version_v2(self):
        api = pypuppetdb.api.API(metric_api_version='v2')
        assert api.metric_api_version == 'v2'

    def test_metric_api_version_invalid_raises(self):
        with pytest.raises(ValueError):
            pypuppetdb.api.API(metric_api_version='bad')


class TestAPIProperties(object):
    def test_version(self, api):
        assert api.version == 'v4'

    def test_base_url(self, api):
        assert api.base_url == 'http://localhost:8080'

    def test_base_url_ssl(self, api):
        api.protocol = 'https'  # slightly evil
        assert api.base_url == 'https://localhost:8080'

    def test_total(self, api):
        api.last_total = 10  # slightly evil
        assert api.total == 10


class TestAPIMethods(object):

    def test_facts(self, api):
        facts_body = [{
            'certname': 'test_certname',
            'name': 'test_name',
            'value': 'test_value',
            'environment': 'test_environment',
        }]
        facts_url = 'http://localhost:8080/pdb/query/v4/facts'

        httpretty.enable()
        httpretty.register_uri(httpretty.GET, facts_url,
                               body=json.dumps(facts_body))

        for fact in api.facts():
            pass

        assert httpretty.last_request().path == '/pdb/query/v4/facts'

        httpretty.disable()
        httpretty.reset()

    def test_fact_names(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/fact-names')
        api.fact_names()
        assert httpretty.last_request().path == '/pdb/query/v4/fact-names'
        httpretty.disable()
        httpretty.reset()

    def test_normalize_resource_type(self, api):
        assert api._normalize_resource_type('sysctl::value') == \
               'Sysctl::Value'
        assert api._normalize_resource_type('user') == 'User'

    def test_environments(self, api):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/environments')
        api.environments()
        assert httpretty.last_request().path == '/pdb/query/v4/environments'
        httpretty.disable()
        httpretty.reset()

    def test_inventory(self, api):
        inventory_body = [{
            'certname': 'test_certname',
            'timestamp': '2017-06-05T20:18:23.374Z',
            'environment': 'test_environment',
            'facts': 'test_facts',
            'trusted': 'test_trusted'
        }]
        inventory_url = 'http://localhost:8080/pdb/query/v4/inventory'

        httpretty.enable()
        httpretty.register_uri(httpretty.GET, inventory_url,
                               body=json.dumps(inventory_body))
        for inv in api.inventory():
            pass

        assert httpretty.last_request().path == '/pdb/query/v4/inventory'

        httpretty.disable()
        httpretty.reset()
