import pytest

import pypuppetdb


class TestBaseAPIURL:
    def test_without_path(self, api):
        assert api._url("nodes") == "http://localhost:8080/pdb/query/v4/nodes"

    def test_with_invalid_endpoint(self, api):
        with pytest.raises(pypuppetdb.errors.APIError):
            api._url("this_will-Never+Ex1s7")

    def test_with_path(self, api):
        url = api._url("nodes", path="node1.example.com")
        assert url == "http://localhost:8080/pdb/query/v4/nodes/node1.example.com"

    def test_quote(self, api):
        url = api._url("facts", path="macaddress/02:42:ec:94:80:f0")
        assert (
            url == "http://localhost:8080/pdb/query/v4/"
            "facts/macaddress/02%3A42%3Aec%3A94%3A80%3Af0"
        )
