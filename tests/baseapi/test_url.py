import pytest
from pypuppetdb.errors import ExperimentalDisabledError

pytestmark = pytest.mark.unit


def test_url_experimental_raises(api2):
    with pytest.raises(ExperimentalDisabledError):
        api2._url('reports')


def test_url_experimental(api2e):
    url = api2e._url('reports')
    assert url == 'http://localhost:8080/experimental/reports'


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


def test_url_events(api2e):
    url = api2e._url('events')
    assert url == 'http://localhost:8080/experimental/events'


def test_url_reports(api2e):
    url = api2e._url('reports')
    assert url == 'http://localhost:8080/experimental/reports'


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


def test_url_events_path(api2e):
    url = api2e._url('events', path='what_ever')
    assert url == 'http://localhost:8080/experimental/events/what_ever'


def test_url_reports_path(api2e):
    url = api2e._url('reports', path='what_ever')
    assert url == 'http://localhost:8080/experimental/reports/what_ever'
