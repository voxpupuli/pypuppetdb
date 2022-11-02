import json

import httpretty

from pypuppetdb.types import Node, Inventory, Fact


class TestPqlAPI:

    def test_pql_casting(self, api):
        pql_query = """
          nodes {
            facts {
              name = "operatingsystem" and
              value = "Debian"
            }
          }
        """
        pql_body = [
            {
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
            },
            {
                "cached_catalog_status": "not_used",
                "catalog_environment": "production",
                "catalog_timestamp": "2016-08-15T11:06:26.275Z",
                "certname": "blueserver.vm",
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
        ]
        pql_url = 'http://localhost:8080/pdb/query/v4'

        httpretty.enable()
        httpretty.register_uri(httpretty.GET, pql_url,
                               body=json.dumps(pql_body))

        nodes = list(api.pql(pql_query))

        assert type(nodes[0]) == Node
        assert nodes[0].name == "greenserver.vm"

        httpretty.disable()
        httpretty.reset()

    def test_pql_no_casting(self, api):
        pql_query = """
          nodes[certname] {
            facts {
              name = "operatingsystem" and
              value = "Debian"
            }
          }
        """
        pql_body = [
            {'certname': 'foo.example.com'},
            {'certname': 'bar.example.com'},
        ]
        pql_url = 'http://localhost:8080/pdb/query/v4'

        httpretty.enable()
        httpretty.register_uri(httpretty.GET, pql_url,
                               body=json.dumps(pql_body))

        elements = list(api.pql(pql_query))

        assert httpretty.last_request().path.startswith('/pdb/query/v4')
        assert elements[0]["certname"] == 'foo.example.com'

        httpretty.disable()
        httpretty.reset()

    def test_get_type_from_query_matching(self, api):
        pql = """
              nodes {
                facts {
                  name = "operatingsystem" and
                  value = "Debian"
                }
              }
            """
        type = api._get_type_from_query(pql)

        assert type == Node

    def test_get_type_from_query_matching_empty_projection(self, api):
        pql = """
              inventory[] {}
            """
        type = api._get_type_from_query(pql)

        assert type == Inventory

    def test_get_type_from_query_matching_no_whitespace(self, api):
        pql = """
              facts{}
            """
        type = api._get_type_from_query(pql)

        assert type == Fact

    def test_get_type_from_query_matching_but_unsupported(self, api):
        pql = """
              producers {}
            """
        type = api._get_type_from_query(pql)

        assert type is None

    def test_get_type_from_query_not_matching_projection(self, api):
        pql = """
              nodes[certname, count()] {}
            """
        type = api._get_type_from_query(pql)

        assert type is None
