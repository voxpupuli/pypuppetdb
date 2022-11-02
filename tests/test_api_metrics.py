import json

import httpretty
import pytest

import pypuppetdb


def stub_request(url, data=None, method=httpretty.GET, status=200, **kwargs):
    if data is None:
        body = "[]"
    else:
        with open(data) as d:
            body = json.load(d.read())
    return httpretty.register_uri(method, url, body=body, status=status, **kwargs)


class TestMetricsAPI:
    def test_metric_v1(self, api):
        httpretty.enable()
        httpretty.enable()
        stub_request("http://localhost:8080/metrics/v1/mbeans/test")
        api.metric("test", version="v1")
        assert httpretty.last_request().path == "/metrics/v1/mbeans/test"

    def test_metric_v1_list(self, api):
        httpretty.enable()
        httpretty.enable()
        stub_request("http://localhost:8080/metrics/v1/mbeans")
        api.metric(version="v1")
        assert httpretty.last_request().path == "/metrics/v1/mbeans"

    def test_metric_v1_version_constructor(self):
        api = pypuppetdb.api.API(metric_api_version="v1")
        httpretty.enable()
        httpretty.enable()
        stub_request("http://localhost:8080/metrics/v1/mbeans/test")
        api.metric("test")
        assert httpretty.last_request().path == "/metrics/v1/mbeans/test"

    def test_metric_v2(self, api):
        metrics_body = {
            "request": {"mbean": "test:name=Num", "type": "read"},
            "value": {"Value": 0},
            "timestamp": 0,
            "status": 200,
        }

        httpretty.enable()
        httpretty.register_uri(
            httpretty.GET,
            "http://localhost:8080/metrics/v2/read/test:name=Num",
            body=json.dumps(metrics_body),
        )
        metric = api.metric("test:name=Num")
        assert httpretty.last_request().path == "/metrics/v2/read/test%3Aname%3DNum"
        assert metric["Value"] == 0
        httpretty.disable()
        httpretty.reset()

    def test_metric_v2_version_constructor(self):
        api = pypuppetdb.api.API(metric_api_version="v2")
        metrics_body = {
            "request": {"mbean": "test:name=Num", "type": "read"},
            "value": {"Value": 0},
            "timestamp": 0,
            "status": 200,
        }

        httpretty.enable()
        httpretty.register_uri(
            httpretty.GET,
            "http://localhost:8080/metrics/v2/read/test:name=Num",
            body=json.dumps(metrics_body),
        )
        metric = api.metric("test:name=Num")
        assert httpretty.last_request().path == "/metrics/v2/read/test%3Aname%3DNum"
        assert metric["Value"] == 0
        httpretty.disable()
        httpretty.reset()

    def test_metric_v2_version_string(self, api):
        metrics_body = {
            "request": {"mbean": "test:name=Num", "type": "read"},
            "value": {"Value": 0},
            "timestamp": 0,
            "status": 200,
        }

        httpretty.enable()
        httpretty.register_uri(
            httpretty.GET,
            "http://localhost:8080/metrics/v2/read/test:name=Num",
            body=json.dumps(metrics_body),
        )
        metric = api.metric("test:name=Num", version="v2")
        assert httpretty.last_request().path == "/metrics/v2/read/test%3Aname%3DNum"
        assert metric["Value"] == 0
        httpretty.disable()
        httpretty.reset()

    def test_metric_v2_error(self, api):
        metrics_body = {
            "request": {"mbean": "test:name=Num", "type": "read"},
            "error_type": "javax.management.InstanceNotFoundException",
            "error": "javax.management.InstanceNotFoundException : test:name=Num",
            "status": 404,
        }

        httpretty.enable()
        httpretty.register_uri(
            httpretty.GET,
            "http://localhost:8080/metrics/v2/read/test:name=Num",
            body=json.dumps(metrics_body),
        )
        with pytest.raises(pypuppetdb.errors.APIError):
            api.metric("test:name=Num")
        assert httpretty.last_request().path == "/metrics/v2/read/test%3Aname%3DNum"
        httpretty.disable()
        httpretty.reset()

    def test_metric_v2_escape_special_characters(self, api):
        metrics_body = {
            "request": {"mbean": "test:name=Num", "type": "read"},
            "value": {"Value": 0},
            "timestamp": 0,
            "status": 200,
        }

        httpretty.enable()
        metric_name = 'test:special/chars!metric"name'
        metric_escaped = 'test:special!/chars!!metric!"name'
        metric_escaped_urlencoded = "test%3Aspecial%21/chars%21%21metric%21%22name"
        httpretty.register_uri(
            httpretty.GET,
            ("http://localhost:8080/metrics/v2/read/" + metric_escaped),
            body=json.dumps(metrics_body),
        )
        metric = api.metric(metric_name)
        assert httpretty.last_request().path == (
            "/metrics/v2/read/" + metric_escaped_urlencoded
        )
        assert metric["Value"] == 0
        httpretty.disable()
        httpretty.reset()

    def test_metric_v2_list(self, api):
        # test metric() (no arguments)
        metrics_body = {
            "request": {"type": "list"},
            "value": {
                "java.util.logging": {"type=Logging": {}},
            },
            "timestamp": 0,
            "status": 200,
        }

        httpretty.enable()
        httpretty.register_uri(
            httpretty.GET,
            "http://localhost:8080/metrics/v2/list",
            body=json.dumps(metrics_body),
        )
        metric = api.metric()
        assert httpretty.last_request().path == "/metrics/v2/list"
        assert metric == {"java.util.logging": {"type=Logging": {}}}
        httpretty.disable()
        httpretty.reset()

    def test_metric_bad_version(self, api):
        with pytest.raises(ValueError):
            api.metric("test", version="bad")
