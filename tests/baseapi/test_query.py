import pytest
from pypuppetdb.errors import APIError


pytestmark = pytest.mark.unit


### API v2
def test_query_endpoint(api2, stub_get):
    stub_get('http://localhost:8080/v2/nodes', body='[]')
    response = api2._query('nodes')
    assert response == []


def test_query_endpoint_path(api2, stub_get):
    stub_get('http://localhost:8080/v2/nodes/host1', body='[]')
    response = api2._query('nodes', path='host1')
    assert response == []


def test_query_endpoint_empty_query(api2, stub_get):
    stub_get('http://localhost:8080/v2/nodes?query=', body='[]')
    response = api2._query('nodes', query='')
    assert response == []


def test_query_endpoint_query(api2, stub_get):
    url = ('http://localhost:8080/v2/nodes?query=%5B%22%3D%22%2C'
           '+%22name%22%2C+%22host1%22%5D')
    stub_get('{0}'.format(url), body='[]')
    response = api2._query('nodes', query='["=", "name", "host1"]')
    assert response == []


def test_query_endpoint_path_empty_query(api2, stub_get):
    stub_get('http://localhost:8080/v2/nodes/host1?query=', body='[]')
    response = api2._query('nodes', path='host1', query='')
    assert response == []


def test_query_endpoint_path_query(api2, stub_get):
    url = ('http://localhost:8080/v2/nodes/host1?query=%5B%22%3D%22%2C'
           '+%22name%22%2C+%22host1%22%5D')
    stub_get('{0}'.format(url), body='[]')
    response = api2._query('nodes', path='host1',
                           query='["=", "name", "host1"]')
    assert response == []


### API v3
def test_query_endpoint(api3, stub_get):
    stub_get('http://localhost:8080/v3/nodes', body='[]')
    response = api3._query('nodes')
    assert response == []


def test_query_endpoint_path(api3, stub_get):
    stub_get('http://localhost:8080/v3/nodes/host1', body='[]')
    response = api3._query('nodes', path='host1')
    assert response == []


def test_query_endpoint_empty_query(api3, stub_get):
    stub_get('http://localhost:8080/v3/nodes?query=', body='[]')
    response = api3._query('nodes', query='')
    assert response == []


def test_query_endpoint_query(api3, stub_get):
    url = ('http://localhost:8080/v3/nodes?query=%5B%22%3D%22%2C'
           '+%22name%22%2C+%22host1%22%5D')
    stub_get('{0}'.format(url), body='[]')
    response = api3._query('nodes', query='["=", "name", "host1"]')
    assert response == []


def test_query_endpoint_path_empty_query(api3, stub_get):
    stub_get('http://localhost:8080/v3/nodes/host1?query=', body='[]')
    response = api3._query('nodes', path='host1', query='')
    assert response == []


def test_query_endpoint_path_query(api3, stub_get):
    url = ('http://localhost:8080/v3/nodes/host1?query=%5B%22%3D%22%2C'
           '+%22name%22%2C+%22host1%22%5D')
    stub_get('{0}'.format(url), body='[]')
    response = api3._query('nodes', path='host1',
                           query='["=", "name", "host1"]')
    assert response == []

def test_query_endpoint_query(api3, stub_get):
    url = ('http://localhost:8080/v3/nodes?query=%5B%22%3D%22%2C'
           '+%22name%22%2C+%22host1%22%5D')
    stub_get('{0}'.format(url), body='[]')
    response = api3._query('nodes', query='["=", "name", "host1"]')
    assert response == []

def test_query_endpoint_query(api3, stub_get):
    url = ('http://localhost:8080/v3/nodes?query=%5B%22%3D%22%2C'
           '+%22name%22%2C+%22host1%22%5D')
    stub_get('{0}'.format(url), body='[]')
    response = api3._query('nodes', query='["=", "name", "host1"]')
    assert response == []
