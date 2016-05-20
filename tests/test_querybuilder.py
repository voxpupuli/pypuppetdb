import pytest
import sys

from pypuppetdb.QueryBuilder import *


class TestBinaryOperator(object):
    """
    Test the BinaryOperator object and all sub-classes.
    """
    def test_equal_operator(self):
        op = EqualsOperator("certname", "test01")
        assert str(op) == '["=", "certname", "test01"]'
        assert repr(op) == 'Query: ["=", "certname", "test01"]'
        assert unicode(op) == '["=", "certname", "test01"]'
        assert str(EqualsOperator("clientversion", 91))\
            == '["=", "clientversion", 91]'
        assert str(EqualsOperator("start_time", "2016-05-11T23:22:48.709Z"))\
            == '["=", "start_time", "2016-05-11T23:22:48.709Z"]'
        assert str(EqualsOperator("is_virtual", True))\
            == '["=", "is_virtual", True]'
        assert str(EqualsOperator("bios_version", ["6.00", 5.00]))\
            == '["=", "bios_version", [\'6.00\', 5.0]]'

    def test_greater_operator(self):
        assert str(GreaterOperator("uptime", 150))\
            == '[">", "uptime", 150]'
        assert str(GreaterOperator("end_time", '"2016-05-11T23:22:48.709Z"'))\
            == '[">", "end_time", ""2016-05-11T23:22:48.709Z""]'

    def test_less_operator(self):
        assert str(LessOperator("uptime_seconds", 300))\
            == '["<", "uptime_seconds", 300]'
        assert str(LessOperator(
            "producer_timestamp",
            "2016-05-11T23:53:29.962Z"))\
            == '["<", "producer_timestamp", "2016-05-11T23:53:29.962Z"]'

    def test_greater_equal_operator(self):
        assert str(GreaterEqualOperator("uptime_days", 3))\
            == '[">=", "uptime_days", 3]'
        assert str(GreaterEqualOperator(
            "start_time",
            "2016-05-11T23:53:29.962Z"))\
            == '[">=", "start_time", "2016-05-11T23:53:29.962Z"]'

    def test_less_equal_operator(self):
        assert str(LessEqualOperator("kernelmajversion", 4))\
            == '["<=", "kernelmajversion", 4]'
        assert str(LessEqualOperator("end_time", "2016-05-11T23:53:29.962Z"))\
            == '["<=", "end_time", "2016-05-11T23:53:29.962Z"]'

    def test_regex_operator(self):
        assert str(RegexOperator("certname", "www\\d+\\.example\\.com"))\
            == '["~", "certname", "www\\d+\\.example\\.com"]'

    def test_regex_array_operator(self):
        assert str(RegexArrayOperator(
            "networking",
            ["interfaces", "eno.*", "netmask"]))\
            == '["~>", "networking", [\'interfaces\', \'eno.*\', \'netmask\']]'

    def test_null_operator(self):
        assert str(NullOperator("expired", True))\
            == '["null?", "expired", True]'
        assert str(NullOperator("report_environment", False))\
            == '["null?", "report_environment", False]'
        with pytest.raises(ValueError):
            NullOperator("environment", "test")


class TestBooleanOperator(object):
    """
    Test the BooleanOperator object and all sub-classes.
    """
