import json

import httpretty
import logging

from pypuppetdb.types import Node, Inventory, Fact


class TestApiPQL(object):

    def test_pql(self, api):
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
