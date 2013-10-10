import pytest
from pypuppetdb.errors import APIError

pytestmark = pytest.mark.unit


### API v2
def test_url_invalid_endpoint(api2):
    with pytest.raises(APIError):
        api2._url('I-will_never+exist%really')


def test_url_nodes(api2):
    url = api2._url('nodes')
    assert url == 'http://localhost:8080/v2/nodes'


def test_url_facts(api2):
    url = api2._url('facts')
    assert url == 'http://localhost:8080/v2/facts'


def test_url_fact_names(api2):
    url = api2._url('fact-names')
    assert url == 'http://localhost:8080/v2/fact-names'


def test_resources(api2):
    url = api2._url('resources')
    assert url == 'http://localhost:8080/v2/resources'


def test_url_nodes_path(api2):
    url = api2._url('nodes', path='node1.puppet.board')
    assert url == 'http://localhost:8080/v2/nodes/node1.puppet.board'


def test_url_facts_path(api2):
    url = api2._url('facts', path='osfamily/Debian')
    assert url == 'http://localhost:8080/v2/facts/osfamily/Debian'


def test_url_fact_names_path(api2):
    url = api2._url('fact-names', path='what_ever')
    assert url == 'http://localhost:8080/v2/fact-names/what_ever'


def test_resources_path(api2):
    url = api2._url('resources', path='File/foo')
    assert url == 'http://localhost:8080/v2/resources/File/foo'


### API v3
def test_url_invalid_endpoint(api3):
    with pytest.raises(APIError):
        api3._url('I-will_never+exist%really')


def test_url_nodes(api3):
    url = api3._url('nodes')
    assert url == 'http://localhost:8080/v3/nodes'


def test_url_facts(api3):
    url = api3._url('facts')
    assert url == 'http://localhost:8080/v3/facts'


def test_url_fact_names(api3):
    url = api3._url('fact-names')
    assert url == 'http://localhost:8080/v3/fact-names'


def test_resources(api3):
    url = api3._url('resources')
    assert url == 'http://localhost:8080/v3/resources'


def test_url_nodes_path(api3):
    url = api3._url('nodes', path='node1.puppet.board')
    assert url == 'http://localhost:8080/v3/nodes/node1.puppet.board'


def test_url_facts_path(api3):
    url = api3._url('facts', path='osfamily/Debian')
    assert url == 'http://localhost:8080/v3/facts/osfamily/Debian'


def test_url_fact_names_path(api3):
    url = api3._url('fact-names', path='what_ever')
    assert url == 'http://localhost:8080/v3/fact-names/what_ever'


def test_resources_path(api3):
    url = api3._url('resources', path='File/foo')
    assert url == 'http://localhost:8080/v3/resources/File/foo'


def test_url_events(api3):
    url = api3._url('events')
    assert url == 'http://localhost:8080/v3/events'


def test_url_reports(api3):
    url = api3._url('reports')
    assert url == 'http://localhost:8080/v3/reports'
