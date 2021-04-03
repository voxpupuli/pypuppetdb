import json

import httpretty


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
