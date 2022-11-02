import json

import httpretty
import pytest

import pypuppetdb


def stub_request(url, data=None, method=httpretty.GET, status=200, **kwargs):
    if data is None:
        body = '[]'
    else:
        with open(data) as d:
            body = json.load(d.read())
    return httpretty.register_uri(method, url, body=body, status=status,
                                  **kwargs)


@pytest.fixture(params=['string', 'QueryBuilder'])
def query(request):
    key = 'certname'
    value = 'node1'
    if request.param == 'string':
        return f'["{key}", "=", "{value}"]'
    elif request.param == 'QueryBuilder':
        return pypuppetdb.QueryBuilder.EqualsOperator(key, value)


class TestQueryAPI:

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

    def test_nodes_single(self, api):
        body = {
            "cached_catalog_status": "not_used",
            "catalog_environment": "production",
            "catalog_timestamp": "2016-08-15T11:06:26.275Z",
            "certname": "greenserver.vm",
            "deactivated": None,
            "expired": None,
            "facts_environment": "production",
            "facts_timestamp": "2016-08-15T11:06:26.140Z",
            "latest_report_hash": "4a956674b016d95a7b77c99513ba26e4a744f8d1",
            "latest_report_noop": False,
            "latest_report_noop_pending": None,
            "latest_report_status": "changed",
            "report_environment": "production",
            "report_timestamp": "2016-08-15T11:06:18.393Z"
        }
        url = 'http://localhost:8080/pdb/query/v4/nodes'

        httpretty.enable()
        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(body))

        nodes = list(api.nodes(query='["=","certname","greenserver.vm"'))

        assert len(nodes) == 1
        assert nodes[0].name == "greenserver.vm"

        assert httpretty.last_request().path.startswith('/pdb/query/v4/nodes')

        httpretty.disable()
        httpretty.reset()
