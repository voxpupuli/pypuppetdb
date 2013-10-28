import pytest
import requests
from pypuppetdb.errors import (UnsupportedVersionError,
                               ImproperlyConfiguredError,
                               APIError, EmptyResponseError)
from pypuppetdb.api import BaseAPI, ENDPOINTS

pytestmark = pytest.mark.unit


def test_defaults():
    api = BaseAPI(2)
    assert api.host == 'localhost'
    assert api.port == 8080
    assert api.ssl is False
    assert api.ssl_key is None
    assert api.ssl_cert is None
    assert api.timeout == 10
    assert api.protocol == 'http'


def test_invalid_api_version():
    with pytest.raises(UnsupportedVersionError):
        api = BaseAPI(1)


def test_api2_endpoints():
    api = BaseAPI(2)
    assert api.version == 'v2'
    assert api.endpoints == ENDPOINTS[2]


def test_api3_endpoints():
    api = BaseAPI(3)
    assert api.version == 'v3'
    assert api.endpoints == ENDPOINTS[3]


def test_with_valid_ssl_config():
    api = BaseAPI(3, ssl=True, ssl_key='ssl.key', ssl_cert='ssl.cert')
    assert api.ssl is True
    assert api.ssl_key == 'ssl.key'
    assert api.ssl_cert == 'ssl.cert'
    assert api.protocol == 'https'


def test_with_invalid_ssl_config():
    with pytest.raises(ImproperlyConfiguredError):
        api = BaseAPI(3, ssl=True, ssl_cert='ssl.cert')


def test_build_url():
    api = BaseAPI(2)
    assert api.base_url == 'http://localhost:8080'


def test_url_with_endpoint():
    api = BaseAPI(2)
    assert api._url('fact-names') == 'http://localhost:8080/v2/fact-names'


def test_url_with_unknown_endpoint():
    api = BaseAPI(2)
    with pytest.raises(APIError):
        api._url('bananas')


def test_url_with_endpoint_with_path():
    api = BaseAPI(2)
    assert api._url('facts', path='osfamily') == ('http://localhost:8080/'
                                                  'v2/facts/osfamily')


def test_query_endpoint(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes', body='[]')
    response = api._query('nodes')
    assert response == []


def test_query_with_query(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes?query=""', body='[]')
    response = api._query('nodes', query="")
    assert response == []


def test_query_with_order_by(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes?order-by=""', body='[]')
    response = api._query('nodes', order_by="")
    assert response == []


def test_query_with_limit(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes?limit=""', body='[]')
    response = api._query('nodes', limit="")
    assert response == []


def test_query_with_include_total(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes?include-total=""', body='[]')
    response = api._query('nodes', include_total="")
    assert response == []


def test_query_with_offset(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes?offset=""', body='[]')
    response = api._query('nodes', offset="")
    assert response == []


def test_query_with_summarize_by(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes?summarize-by=""', body='[]')
    response = api._query('nodes', summarize_by="")
    assert response == []


def test_query_with_count_by(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes?count-by=""', body='[]')
    response = api._query('nodes', count_by="")
    assert response == []


def test_query_with_count_filter(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes?count-filter=""', body='[]')
    response = api._query('nodes', count_filter="")
    assert response == []


def test_query_empty_body(stub_get):
    api = BaseAPI(2)
    stub_get('http://localhost:8080/v2/nodes', body='null')
    with pytest.raises(EmptyResponseError):
        api._query('nodes')


def test_query_timeout(stub_get):
    # No idea how to check for a timeout just yet
    pass


def test_query_connection():
    api = BaseAPI(2)
    with pytest.raises(requests.exceptions.ConnectionError):
        api._query('nodes')


def test_nodes():
    api = BaseAPI(2)
    with pytest.raises(NotImplementedError):
        api.nodes()


def test_node():
    api = BaseAPI(2)
    with pytest.raises(NotImplementedError):
        api.node()


def test_facts():
    api = BaseAPI(2)
    with pytest.raises(NotImplementedError):
        api.facts()


def test_resources():
    api = BaseAPI(2)
    with pytest.raises(NotImplementedError):
        api.resources()
