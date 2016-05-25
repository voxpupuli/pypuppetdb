import pytest
import pypuppetdb
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
        assert str(EqualsOperator(['parameter', 'ensure'], "present"))\
            == '["=", [\'parameter\', \'ensure\'], "present"]'

    def test_greater_operator(self):
        assert str(GreaterOperator("uptime", 150))\
            == '[">", "uptime", 150]'
        assert str(GreaterOperator("end_time", '"2016-05-11T23:22:48.709Z"'))\
            == '[">", "end_time", ""2016-05-11T23:22:48.709Z""]'
        assert str(GreaterOperator(['parameter', 'version'], 4.0))\
            == '[">", [\'parameter\', \'version\'], 4.0]'

    def test_less_operator(self):
        assert str(LessOperator("uptime_seconds", 300))\
            == '["<", "uptime_seconds", 300]'
        assert str(LessOperator(
            "producer_timestamp",
            "2016-05-11T23:53:29.962Z"))\
            == '["<", "producer_timestamp", "2016-05-11T23:53:29.962Z"]'
        assert str(LessOperator(['parameter', 'version'], 4.0))\
            == '["<", [\'parameter\', \'version\'], 4.0]'

    def test_greater_equal_operator(self):
        assert str(GreaterEqualOperator("uptime_days", 3))\
            == '[">=", "uptime_days", 3]'
        assert str(GreaterEqualOperator(
            "start_time",
            "2016-05-11T23:53:29.962Z"))\
            == '[">=", "start_time", "2016-05-11T23:53:29.962Z"]'
        assert str(GreaterEqualOperator(['parameter', 'version'], 4.0))\
            == '[">=", [\'parameter\', \'version\'], 4.0]'

    def test_less_equal_operator(self):
        assert str(LessEqualOperator("kernelmajversion", 4))\
            == '["<=", "kernelmajversion", 4]'
        assert str(LessEqualOperator("end_time", "2016-05-11T23:53:29.962Z"))\
            == '["<=", "end_time", "2016-05-11T23:53:29.962Z"]'
        assert str(LessEqualOperator(['parameter', 'version'], 4.0))\
            == '["<=", [\'parameter\', \'version\'], 4.0]'

    def test_regex_operator(self):
        assert str(RegexOperator("certname", "www\\d+\\.example\\.com"))\
            == '["~", "certname", "www\\d+\\.example\\.com"]'
        assert str(RegexOperator(['parameter', 'version'], "4\\.\\d+"))\
            == '["~", [\'parameter\', \'version\'], "4\\.\\d+"]'

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
    def test_and_operator(self):
        op = AndOperator()
        op.add(EqualsOperator("operatingsystem", "CentOS"))
        op.add([EqualsOperator("architecture", "x86_64"),
                GreaterOperator("operatingsystemmajrelease", 6)])

        assert str(op) == '["and",["=", "operatingsystem", "CentOS"],'\
            '["=", "architecture", "x86_64"],'\
            '[">", "operatingsystemmajrelease", 6]]'
        assert repr(op) == 'Query: ["and",["=", "operatingsystem", "CentOS"],'\
            '["=", "architecture", "x86_64"],'\
            '[">", "operatingsystemmajrelease", 6]]'
        assert unicode(op) == '["and",["=", "operatingsystem", "CentOS"],'\
            '["=", "architecture", "x86_64"],'\
            '[">", "operatingsystemmajrelease", 6]]'

        with pytest.raises(ValueError):
            op.add({"query1": '["=", "catalog_environment", "production"]'})

    def test_or_operator(self):
        op = OrOperator()
        op.add(EqualsOperator("operatingsystem", "CentOS"))
        op.add([EqualsOperator("architecture", "x86_64"),
                GreaterOperator("operatingsystemmajrelease", 6)])

        assert str(op) == '["or",["=", "operatingsystem", "CentOS"],'\
            '["=", "architecture", "x86_64"],'\
            '[">", "operatingsystemmajrelease", 6]]'
        assert repr(op) == 'Query: ["or",["=", "operatingsystem", "CentOS"],'\
            '["=", "architecture", "x86_64"],'\
            '[">", "operatingsystemmajrelease", 6]]'
        assert unicode(op) == '["or",["=", "operatingsystem", "CentOS"],'\
            '["=", "architecture", "x86_64"],'\
            '[">", "operatingsystemmajrelease", 6]]'

        with pytest.raises(ValueError):
            op.add({"query1": '["=", "catalog_environment", "production"]'})

    def test_not_operator(self):
        op = NotOperator()
        op.add(EqualsOperator("operatingsystem", "CentOS"))

        assert str(op) == '["not",["=", "operatingsystem", "CentOS"]]'
        assert repr(op) == 'Query: ["not",["=", "operatingsystem", "CentOS"]]'
        assert unicode(op) == '["not",["=", "operatingsystem", "CentOS"]]'

        with pytest.raises(ValueError):
            op.add(GreaterOperator("operatingsystemmajrelease", 6))
        with pytest.raises(ValueError):
            op.add([EqualsOperator("architecture", "x86_64"),
                    GreaterOperator("operatingsystemmajrelease", 6)])


class TestExtractOperator(object):
    """
    Test the ExtractOperator object and all sub-classes.
    """
    def test_with_add_field(self):
        op = ExtractOperator()

        with pytest.raises(pypuppetdb.errors.APIError):
            repr(op)
        with pytest.raises(pypuppetdb.errors.APIError):
            str(op)
        with pytest.raises(pypuppetdb.errors.APIError):
            unicode(op)

        op.add_field("certname")
        op.add_field(['fact_environment', 'catalog_environment'])

        assert repr(op) == 'Query: ["extract",'\
            '["certname","fact_environment","catalog_environment"]]'
        assert str(op) == '["extract",'\
            '["certname","fact_environment","catalog_environment"]]'
        assert unicode(op) == '["extract",'\
            '["certname","fact_environment","catalog_environment"]]'

        with pytest.raises(pypuppetdb.errors.APIError):
            op.add_field({'equal': 'operatingsystemrelease'})

    def test_with_add_query(self):
        op = ExtractOperator()

        op.add_field(['certname', 'fact_environment', 'catalog_environment'])

        with pytest.raises(pypuppetdb.errors.APIError):
            op.add_query({'less': 42, 'greater': 50})

        op.add_query(EqualsOperator('domain', 'example.com'))

        assert repr(op) == 'Query: ["extract",'\
            '["certname","fact_environment","catalog_environment"],'\
            '["=", "domain", "example.com"]]'
        assert str(op) == '["extract",'\
            '["certname","fact_environment","catalog_environment"],'\
            '["=", "domain", "example.com"]]'
        assert unicode(op) == '["extract",'\
            '["certname","fact_environment","catalog_environment"],'\
            '["=", "domain", "example.com"]]'

        with pytest.raises(pypuppetdb.errors.APIError):
            op.add_query(GreaterOperator("processorcount", 1))

    def test_with_add_group_by(self):
        op = ExtractOperator()

        op.add_field(['certname', 'fact_environment', 'catalog_environment'])
        op.add_query(EqualsOperator('domain', 'example.com'))
        op.add_group_by(["fact_environment", "catalog_environment"])

        with pytest.raises(pypuppetdb.errors.APIError):
            op.add_group_by({"deactivated": False})

        assert repr(op) == 'Query: ["extract",'\
            '["certname","fact_environment","catalog_environment"],'\
            '["=", "domain", "example.com"],'\
            '["group_by","fact_environment","catalog_environment"]]'
        assert str(op) == '["extract",'\
            '["certname","fact_environment","catalog_environment"],'\
            '["=", "domain", "example.com"],'\
            '["group_by","fact_environment","catalog_environment"]]'
        assert unicode(op) == '["extract",'\
            '["certname","fact_environment","catalog_environment"],'\
            '["=", "domain", "example.com"],'\
            '["group_by","fact_environment","catalog_environment"]]'
