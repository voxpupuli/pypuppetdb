import datetime
import pytest
import pypuppetdb
import sys

from pypuppetdb.QueryBuilder import *

if sys.version_info >= (3, 0):
    unicode = str


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
            == '["=", "is_virtual", true]'
        assert str(EqualsOperator("bios_version", ["6.00", 5.00]))\
            == '["=", "bios_version", [\'6.00\', 5.0]]'
        assert str(EqualsOperator(['parameter', 'ensure'], "present"))\
            == '["=", [\'parameter\', \'ensure\'], "present"]'
        assert str(EqualsOperator(u"latest_report?", True))\
            == '["=", "latest_report?", true]'
        assert str(EqualsOperator("report_timestamp",
                                  datetime.datetime(2016, 6, 11)))\
            == '["=", "report_timestamp", "2016-06-11 00:00:00"]'

    def test_greater_operator(self):
        assert str(GreaterOperator("uptime", 150))\
            == '[">", "uptime", 150]'
        assert str(GreaterOperator("end_time", '"2016-05-11T23:22:48.709Z"'))\
            == '[">", "end_time", ""2016-05-11T23:22:48.709Z""]'
        assert str(GreaterOperator(['parameter', 'version'], 4.0))\
            == '[">", [\'parameter\', \'version\'], 4.0]'
        assert str(GreaterOperator("report_timestamp",
                                   datetime.datetime(2016, 6, 11)))\
            == '[">", "report_timestamp", "2016-06-11 00:00:00"]'

    def test_less_operator(self):
        assert str(LessOperator("uptime_seconds", 300))\
            == '["<", "uptime_seconds", 300]'
        assert str(LessOperator(
            "producer_timestamp",
            "2016-05-11T23:53:29.962Z"))\
            == '["<", "producer_timestamp", "2016-05-11T23:53:29.962Z"]'
        assert str(LessOperator(['parameter', 'version'], 4.0))\
            == '["<", [\'parameter\', \'version\'], 4.0]'
        assert str(LessOperator("report_timestamp",
                                datetime.datetime(2016, 6, 11)))\
            == '["<", "report_timestamp", "2016-06-11 00:00:00"]'

    def test_greater_equal_operator(self):
        assert str(GreaterEqualOperator("uptime_days", 3))\
            == '[">=", "uptime_days", 3]'
        assert str(GreaterEqualOperator(
            "start_time",
            "2016-05-11T23:53:29.962Z"))\
            == '[">=", "start_time", "2016-05-11T23:53:29.962Z"]'
        assert str(GreaterEqualOperator(['parameter', 'version'], 4.0))\
            == '[">=", [\'parameter\', \'version\'], 4.0]'
        assert str(GreaterEqualOperator("report_timestamp",
                                        datetime.datetime(2016, 6, 11)))\
            == '[">=", "report_timestamp", "2016-06-11 00:00:00"]'

    def test_less_equal_operator(self):
        assert str(LessEqualOperator("kernelmajversion", 4))\
            == '["<=", "kernelmajversion", 4]'
        assert str(LessEqualOperator("end_time", "2016-05-11T23:53:29.962Z"))\
            == '["<=", "end_time", "2016-05-11T23:53:29.962Z"]'
        assert str(LessEqualOperator(['parameter', 'version'], 4.0))\
            == '["<=", [\'parameter\', \'version\'], 4.0]'
        assert str(LessEqualOperator("report_timestamp",
                                     datetime.datetime(2016, 6, 11)))\
            == '["<=", "report_timestamp", "2016-06-11 00:00:00"]'

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
            == '["null?", "expired", true]'
        assert str(NullOperator("report_environment", False))\
            == '["null?", "report_environment", false]'
        with pytest.raises(APIError):
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

        with pytest.raises(APIError):
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

        with pytest.raises(APIError):
            op.add({"query1": '["=", "catalog_environment", "production"]'})

    def test_not_operator(self):
        op = NotOperator()
        op.add(EqualsOperator("operatingsystem", "CentOS"))

        assert str(op) == '["not",["=", "operatingsystem", "CentOS"]]'
        assert repr(op) == 'Query: ["not",["=", "operatingsystem", "CentOS"]]'
        assert unicode(op) == '["not",["=", "operatingsystem", "CentOS"]]'

        with pytest.raises(APIError):
            op.add(GreaterOperator("operatingsystemmajrelease", 6))
        with pytest.raises(APIError):
            op.add([EqualsOperator("architecture", "x86_64"),
                    GreaterOperator("operatingsystemmajrelease", 6)])

    def test_and_with_no_operations(self):
        op = AndOperator()

        with pytest.raises(APIError):
            repr(op)
        with pytest.raises(APIError):
            str(op)
        with pytest.raises(APIError):
            unicode(op)

    def test_or_with_no_operations(self):
        op = OrOperator()

        with pytest.raises(APIError):
            repr(op)
        with pytest.raises(APIError):
            str(op)
        with pytest.raises(APIError):
            unicode(op)

    def test_not_with_no_operations(self):
        op = NotOperator()

        with pytest.raises(APIError):
            repr(op)
        with pytest.raises(APIError):
            str(op)
        with pytest.raises(APIError):
            unicode(op)

    def test_not_with_list(self):
        op = NotOperator()

        with pytest.raises(APIError):
            str(op.add([EqualsOperator('clientversion', '4.5.1'),
                        EqualsOperator('facterversion', '3.2.0')]))


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

    def test_with_add_function_operator(self):
        op = ExtractOperator()

        op.add_field(FunctionOperator('to_string',
                                      'producer_timestamp',
                                      'FMDAY'))
        op.add_field(FunctionOperator('count'))
        op.add_group_by(FunctionOperator('to_string',
                                         'producer_timestamp',
                                         'FMDAY'))

        assert str(op) == '["extract",'\
            '[["function","to_string","producer_timestamp","FMDAY"],'\
            '["function","count"]],'\
            '["group_by",'\
            '["function","to_string","producer_timestamp","FMDAY"]]]'
        assert repr(op) == 'Query: ["extract",'\
            '[["function","to_string","producer_timestamp","FMDAY"],'\
            '["function","count"]],'\
            '["group_by",'\
            '["function","to_string","producer_timestamp","FMDAY"]]]'
        assert unicode(op) == '["extract",'\
            '[["function","to_string","producer_timestamp","FMDAY"],'\
            '["function","count"]],'\
            '["group_by",'\
            '["function","to_string","producer_timestamp","FMDAY"]]]'


class TestFunctionOperator(object):
    """
    Test the FunctionOperator object and all sub-classes.
    """
    def test_count_function(self):
        assert str(FunctionOperator('count')) == \
            '["function","count"]'
        assert repr(FunctionOperator('count')) == \
            'Query: ["function","count"]'
        assert unicode(FunctionOperator('count')) == \
            '["function","count"]'
        assert str(FunctionOperator('count', 'domain')) == \
            '["function","count","domain"]'
        assert repr(FunctionOperator('count', 'domain')) == \
            'Query: ["function","count","domain"]'
        assert unicode(FunctionOperator('count', 'domain')) == \
            '["function","count","domain"]'

    def test_avg_function(self):
        assert str(FunctionOperator('avg', 'uptime')) == \
            '["function","avg","uptime"]'
        assert repr(FunctionOperator('avg', 'uptime')) == \
            'Query: ["function","avg","uptime"]'
        assert unicode(FunctionOperator('avg', 'uptime')) == \
            '["function","avg","uptime"]'

        with pytest.raises(pypuppetdb.errors.APIError):
            FunctionOperator("avg")

    def test_sum_function(self):
        assert str(FunctionOperator('sum', 'memoryfree_mb')) == \
            '["function","sum","memoryfree_mb"]'
        assert repr(FunctionOperator('sum', 'memoryfree_mb')) == \
            'Query: ["function","sum","memoryfree_mb"]'
        assert unicode(FunctionOperator('sum', 'memoryfree_mb')) == \
            '["function","sum","memoryfree_mb"]'

        with pytest.raises(pypuppetdb.errors.APIError):
            FunctionOperator("sum")

    def test_min_function(self):
        assert str(FunctionOperator('min', 'kernelversion')) == \
            '["function","min","kernelversion"]'
        assert repr(FunctionOperator('min', 'kernelversion')) == \
            'Query: ["function","min","kernelversion"]'
        assert unicode(FunctionOperator('min', 'kernelversion')) == \
            '["function","min","kernelversion"]'

        with pytest.raises(pypuppetdb.errors.APIError):
            FunctionOperator("min")

    def test_max_function(self):
        assert str(FunctionOperator('max', 'facterversion')) == \
            '["function","max","facterversion"]'
        assert repr(FunctionOperator('max', 'facterversion')) == \
            'Query: ["function","max","facterversion"]'
        assert unicode(FunctionOperator('max', 'facterversion')) == \
            '["function","max","facterversion"]'

        with pytest.raises(pypuppetdb.errors.APIError):
            FunctionOperator("max")

    def test_to_string_function(self):
        assert str(FunctionOperator("to_string",
                                    'producer_timestamp',
                                    'FMDAY')) == \
            '["function","to_string","producer_timestamp","FMDAY"]'
        assert repr(FunctionOperator("to_string",
                                     'producer_timestamp',
                                     'FMDAY')) == \
            'Query: ["function","to_string","producer_timestamp","FMDAY"]'
        assert unicode(FunctionOperator("to_string",
                                        'producer_timestamp',
                                        'FMDAY')) == \
            '["function","to_string","producer_timestamp","FMDAY"]'

        with pytest.raises(pypuppetdb.errors.APIError):
            FunctionOperator("to_string")
        with pytest.raises(pypuppetdb.errors.APIError):
            FunctionOperator("to_string", 'receive_time')

    def test_unknown_function(self):
        with pytest.raises(pypuppetdb.errors.APIError):
            FunctionOperator("std_dev")
        with pytest.raises(pypuppetdb.errors.APIError):
            FunctionOperator("last")
