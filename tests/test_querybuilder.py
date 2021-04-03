import datetime

import pytest

from pypuppetdb.QueryBuilder import (AndOperator, EqualsOperator, ExtractOperator, FromOperator,
                                     FunctionOperator, GreaterEqualOperator, GreaterOperator,
                                     InOperator, LessEqualOperator, LessOperator, NotOperator,
                                     NullOperator, OrOperator, RegexArrayOperator, RegexOperator,
                                     SubqueryOperator)
from pypuppetdb.errors import APIError


class TestBinaryOperator(object):
    """
    Test the BinaryOperator object and all sub-classes.
    """
    def test_equal_operator(self):
        op = EqualsOperator("certname", "test01")
        assert str(op) == '["=", "certname", "test01"]'
        assert repr(op) == 'Query: ["=", "certname", "test01"]'
        assert str(op) == '["=", "certname", "test01"]'
        assert str(EqualsOperator("clientversion", 91))\
            == '["=", "clientversion", 91]'
        assert str(EqualsOperator("start_time", "2016-05-11T23:22:48.709Z"))\
            == '["=", "start_time", "2016-05-11T23:22:48.709Z"]'
        assert str(EqualsOperator("is_virtual", True))\
            == '["=", "is_virtual", true]'
        assert str(EqualsOperator("bios_version", ["6.00", 5.00]))\
            == '["=", "bios_version", ["6.00", 5.0]]'
        assert str(EqualsOperator(['parameter', 'ensure'], "present"))\
            == '["=", ["parameter", "ensure"], "present"]'
        assert str(EqualsOperator(u"latest_report?", True))\
            == '["=", "latest_report?", true]'
        assert str(EqualsOperator("report_timestamp",
                                  datetime.datetime(2016, 6, 11)))\
            == '["=", "report_timestamp", "2016-06-11 00:00:00"]'

    def test_greater_operator(self):
        assert str(GreaterOperator("uptime", 150))\
            == '[">", "uptime", 150]'
        assert str(GreaterOperator("end_time", '2016-05-11T23:22:48.709Z'))\
            == '[">", "end_time", "2016-05-11T23:22:48.709Z"]'
        assert str(GreaterOperator(['parameter', 'version'], 4.0))\
            == '[">", ["parameter", "version"], 4.0]'
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
            == '["<", ["parameter", "version"], 4.0]'
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
            == '[">=", ["parameter", "version"], 4.0]'
        assert str(GreaterEqualOperator("report_timestamp",
                                        datetime.datetime(2016, 6, 11)))\
            == '[">=", "report_timestamp", "2016-06-11 00:00:00"]'

    def test_less_equal_operator(self):
        assert str(LessEqualOperator("kernelmajversion", 4))\
            == '["<=", "kernelmajversion", 4]'
        assert str(LessEqualOperator("end_time", "2016-05-11T23:53:29.962Z"))\
            == '["<=", "end_time", "2016-05-11T23:53:29.962Z"]'
        assert str(LessEqualOperator(['parameter', 'version'], 4.0))\
            == '["<=", ["parameter", "version"], 4.0]'
        assert str(LessEqualOperator("report_timestamp",
                                     datetime.datetime(2016, 6, 11)))\
            == '["<=", "report_timestamp", "2016-06-11 00:00:00"]'

    def test_regex_operator(self):
        assert str(RegexOperator("certname", "www\\d+\\.example\\.com"))\
            == '["~", "certname", "www\\\\d+\\\\.example\\\\.com"]'
        assert str(RegexOperator(['parameter', 'version'], "4\\.\\d+"))\
            == '["~", ["parameter", "version"], "4\\\\.\\\\d+"]'

    def test_regex_array_operator(self):
        assert str(RegexArrayOperator(
            "networking",
            ["interfaces", "eno.*", "netmask"]))\
            == '["~>", "networking", ["interfaces", "eno.*", "netmask"]]'

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

        assert str(op) == '["and", ["=", "operatingsystem", "CentOS"], '\
            '["=", "architecture", "x86_64"], '\
            '[">", "operatingsystemmajrelease", 6]]'
        assert repr(op) == 'Query: ["and", '\
            '["=", "operatingsystem", "CentOS"], '\
            '["=", "architecture", "x86_64"], '\
            '[">", "operatingsystemmajrelease", 6]]'
        assert str(op) == '["and", ["=", "operatingsystem", "CentOS"], ' \
                          '["=", "architecture", "x86_64"], '\
            '[">", "operatingsystemmajrelease", 6]]'

        with pytest.raises(APIError):
            op.add({"query1": '["=", "catalog_environment", "production"]'})

    def test_or_operator(self):
        op = OrOperator()
        op.add(EqualsOperator("operatingsystem", "CentOS"))
        op.add([EqualsOperator("architecture", "x86_64"),
                GreaterOperator("operatingsystemmajrelease", 6)])

        assert str(op) == '["or", ["=", "operatingsystem", "CentOS"], '\
            '["=", "architecture", "x86_64"], '\
            '[">", "operatingsystemmajrelease", 6]]'
        assert repr(op) == 'Query: ["or", '\
            '["=", "operatingsystem", "CentOS"], '\
            '["=", "architecture", "x86_64"], '\
            '[">", "operatingsystemmajrelease", 6]]'
        assert str(op) == '["or", ["=", "operatingsystem", "CentOS"], ' \
                          '["=", "architecture", "x86_64"], '\
            '[">", "operatingsystemmajrelease", 6]]'

        with pytest.raises(APIError):
            op.add({"query1": '["=", "catalog_environment", "production"]'})

    def test_not_operator(self):
        op = NotOperator()
        op.add(EqualsOperator("operatingsystem", "CentOS"))

        assert str(op) == '["not", ["=", "operatingsystem", "CentOS"]]'
        assert repr(op) == 'Query: ["not", ["=", "operatingsystem", "CentOS"]]'
        assert str(op) == '["not", ["=", "operatingsystem", "CentOS"]]'

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
            str(op)

    def test_or_with_no_operations(self):
        op = OrOperator()

        with pytest.raises(APIError):
            repr(op)
        with pytest.raises(APIError):
            str(op)
        with pytest.raises(APIError):
            str(op)

    def test_not_with_no_operations(self):
        op = NotOperator()

        with pytest.raises(APIError):
            repr(op)
        with pytest.raises(APIError):
            str(op)
        with pytest.raises(APIError):
            str(op)

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

        with pytest.raises(APIError):
            repr(op)
        with pytest.raises(APIError):
            str(op)
        with pytest.raises(APIError):
            str(op)

        op.add_field("certname")
        op.add_field(['fact_environment', 'catalog_environment'])

        assert repr(op) == 'Query: ["extract", '\
            '["certname", "fact_environment", "catalog_environment"]]'
        assert str(op) == '["extract", '\
            '["certname", "fact_environment", "catalog_environment"]]'
        assert str(op) == '["extract", ' \
                          '["certname", "fact_environment", "catalog_environment"]]'

        with pytest.raises(APIError):
            op.add_field({'equal': 'operatingsystemrelease'})

    def test_with_add_query(self):
        op = ExtractOperator()

        op.add_field(['certname', 'fact_environment', 'catalog_environment'])

        with pytest.raises(APIError):
            op.add_query({'less': 42, 'greater': 50})

        op.add_query(EqualsOperator('domain', 'example.com'))

        assert repr(op) == 'Query: ["extract", '\
            '["certname", "fact_environment", "catalog_environment"], '\
            '["=", "domain", "example.com"]]'
        assert str(op) == '["extract", '\
            '["certname", "fact_environment", "catalog_environment"], '\
            '["=", "domain", "example.com"]]'
        assert str(op) == '["extract", ' \
                          '["certname", "fact_environment", "catalog_environment"], '\
            '["=", "domain", "example.com"]]'

        with pytest.raises(APIError):
            op.add_query(GreaterOperator("processorcount", 1))

    def test_with_add_group_by(self):
        op = ExtractOperator()

        op.add_field(['certname', 'fact_environment', 'catalog_environment'])
        op.add_query(EqualsOperator('domain', 'example.com'))
        op.add_group_by(["fact_environment", "catalog_environment"])

        with pytest.raises(APIError):
            op.add_group_by({"deactivated": False})

        assert repr(op) == 'Query: ["extract", '\
            '["certname", "fact_environment", "catalog_environment"], '\
            '["=", "domain", "example.com"], '\
            '["group_by", "fact_environment", "catalog_environment"]]'
        assert str(op) == '["extract", '\
            '["certname", "fact_environment", "catalog_environment"], '\
            '["=", "domain", "example.com"], '\
            '["group_by", "fact_environment", "catalog_environment"]]'
        assert str(op) == '["extract", ' \
                          '["certname", "fact_environment", "catalog_environment"], '\
            '["=", "domain", "example.com"], '\
            '["group_by", "fact_environment", "catalog_environment"]]'

    def test_with_add_function_operator(self):
        op = ExtractOperator()

        op.add_field(FunctionOperator('to_string',
                                      'producer_timestamp',
                                      'FMDAY'))
        op.add_field(FunctionOperator('count'))
        op.add_group_by(FunctionOperator('to_string',
                                         'producer_timestamp',
                                         'FMDAY'))

        assert str(op) == '["extract", '\
            '[["function", "to_string", "producer_timestamp", "FMDAY"], '\
            '["function", "count"]], '\
            '["group_by", '\
            '["function", "to_string", "producer_timestamp", "FMDAY"]]]'
        assert repr(op) == 'Query: ["extract", '\
            '[["function", "to_string", "producer_timestamp", "FMDAY"], '\
            '["function", "count"]], '\
            '["group_by", '\
            '["function", "to_string", "producer_timestamp", "FMDAY"]]]'
        assert str(op) == '["extract", ' \
                          '[["function", "to_string", "producer_timestamp", "FMDAY"], '\
            '["function", "count"]], '\
            '["group_by", '\
            '["function", "to_string", "producer_timestamp", "FMDAY"]]]'


class TestFunctionOperator(object):
    """
    Test the FunctionOperator object and all sub-classes.
    """
    def test_count_function(self):
        assert str(FunctionOperator('count')) == \
            '["function", "count"]'
        assert repr(FunctionOperator('count')) == \
            'Query: ["function", "count"]'
        assert str(FunctionOperator('count')) == \
            '["function", "count"]'
        assert str(FunctionOperator('count', 'domain')) == \
            '["function", "count", "domain"]'
        assert repr(FunctionOperator('count', 'domain')) == \
            'Query: ["function", "count", "domain"]'
        assert str(FunctionOperator('count', 'domain')) == \
            '["function", "count", "domain"]'

    def test_avg_function(self):
        assert str(FunctionOperator('avg', 'uptime')) == \
            '["function", "avg", "uptime"]'
        assert repr(FunctionOperator('avg', 'uptime')) == \
            'Query: ["function", "avg", "uptime"]'
        assert str(FunctionOperator('avg', 'uptime')) == \
            '["function", "avg", "uptime"]'

        with pytest.raises(APIError):
            FunctionOperator("avg")

    def test_sum_function(self):
        assert str(FunctionOperator('sum', 'memoryfree_mb')) == \
            '["function", "sum", "memoryfree_mb"]'
        assert repr(FunctionOperator('sum', 'memoryfree_mb')) == \
            'Query: ["function", "sum", "memoryfree_mb"]'
        assert str(FunctionOperator('sum', 'memoryfree_mb')) == \
            '["function", "sum", "memoryfree_mb"]'

        with pytest.raises(APIError):
            FunctionOperator("sum")

    def test_min_function(self):
        assert str(FunctionOperator('min', 'kernelversion')) == \
            '["function", "min", "kernelversion"]'
        assert repr(FunctionOperator('min', 'kernelversion')) == \
            'Query: ["function", "min", "kernelversion"]'
        assert str(FunctionOperator('min', 'kernelversion')) == \
            '["function", "min", "kernelversion"]'

        with pytest.raises(APIError):
            FunctionOperator("min")

    def test_max_function(self):
        assert str(FunctionOperator('max', 'facterversion')) == \
            '["function", "max", "facterversion"]'
        assert repr(FunctionOperator('max', 'facterversion')) == \
            'Query: ["function", "max", "facterversion"]'
        assert str(FunctionOperator('max', 'facterversion')) == \
            '["function", "max", "facterversion"]'

        with pytest.raises(APIError):
            FunctionOperator("max")

    def test_to_string_function(self):
        assert str(FunctionOperator("to_string",
                                    'producer_timestamp',
                                    'FMDAY')) == \
            '["function", "to_string", "producer_timestamp", "FMDAY"]'
        assert repr(FunctionOperator("to_string",
                                     'producer_timestamp',
                                     'FMDAY')) == \
            'Query: ["function", "to_string", "producer_timestamp", "FMDAY"]'
        assert str(FunctionOperator("to_string", 'producer_timestamp', 'FMDAY')) == \
            '["function", "to_string", "producer_timestamp", "FMDAY"]'

        with pytest.raises(APIError):
            FunctionOperator("to_string")
        with pytest.raises(APIError):
            FunctionOperator("to_string", 'receive_time')

    def test_unknown_function(self):
        with pytest.raises(APIError):
            FunctionOperator("std_dev")
        with pytest.raises(APIError):
            FunctionOperator("last")


class TestSubqueryOperator(object):
    """
    Test the SubqueryOperator object
    """
    def test_events_endpoint(self):
        assert str(SubqueryOperator('events')) == \
            '["select_events"]'

        op = SubqueryOperator('events')
        op.add_query(EqualsOperator('status', 'noop'))

        assert repr(op) == 'Query: ["select_events", '\
            '["=", "status", "noop"]]'

    def test_multiple_add_query(self):
        with pytest.raises(APIError):
            op = SubqueryOperator('events')
            op.add_query(EqualsOperator('status', 'noop'))
            op.add_query(EqualsOperator('status', 'changed'))

    def test_unknown_endpoint(self):
        with pytest.raises(APIError):
            SubqueryOperator('cats')


class TestInOperator(object):
    """
    Test the InOperator object
    """
    def test_events_endpoint(self):
        assert str(InOperator('certname')) == \
            '["in", "certname"]'

        op = InOperator('certname')
        ex = ExtractOperator()
        ex.add_field("certname")
        op.add_query(ex)

        assert repr(op) == 'Query: ["in", "certname", ' \
            '["extract", ["certname"]]]'

    def test_multiple_add_query(self):
        with pytest.raises(APIError):
            op = InOperator('certname')
            op.add_query(ExtractOperator())
            op.add_query(ExtractOperator())

    def test_add_array(self):
        arr = [1, "2", 3]
        op = InOperator('certname')
        op.add_array(arr)

        assert repr(op) == 'Query: ["in", "certname", ' \
            '["array", [1, "2", 3]]]'

    def test_invalid_add_array(self):
        arr = [1, 2, 3]
        inv1 = [1, [2, 3]]
        inv2 = []

        with pytest.raises(APIError):
            op = InOperator('certname')
            op.add_array(inv1)

        with pytest.raises(APIError):
            op = InOperator('certname')
            op.add_array(inv2)

        with pytest.raises(APIError):
            op = InOperator('certname')
            op.add_array(arr)
            op.add_array(arr)

        with pytest.raises(APIError):
            op = InOperator('certname')

            op.add_array(arr)
            ex = ExtractOperator()
            ex.add_field("certname")
            op.add_query(ex)

    def test_fromoperator(self):
        op = InOperator('certname')
        ex = ExtractOperator()
        ex.add_field(["certname", "facts"])
        fr = FromOperator("facts")
        fr.add_query(ex)
        fr.add_offset(10)
        op.add_query(fr)

        assert repr(op) == 'Query: ["in", "certname", ' \
            '["from", "facts", ["extract", ' \
            '["certname", "facts"]], ["offset", 10]]]'

        # last example on page
        # https://puppet.com/docs/puppetdb/5.1/api/query/v4/ast.html

        op = InOperator('certname')
        ex = ExtractOperator()
        ex.add_field('certname')
        fr = FromOperator('fact_contents')
        nd = AndOperator()
        nd.add(EqualsOperator("path",
                              ["networking", "eth0", "macaddresses", 0]))
        nd.add(EqualsOperator("value", "aa:bb:cc:dd:ee:00"))
        ex.add_query(nd)
        fr.add_query(ex)
        op.add_query(fr)

        assert str(op) == '["in", "certname", ' \
                          '["from", "fact_contents", ' \
            '["extract", ["certname"], ["and", ["=", "path", ' \
            '["networking", "eth0", "macaddresses", 0]], ' \
            '["=", "value", "aa:bb:cc:dd:ee:00"]]]]]'


class TestFromOperator(object):
    """
    Test the FromOperator object
    """

    def test_init_from(self):
        fr = FromOperator("facts")

        with pytest.raises(APIError):
            str(fr) == "unimportant_no_query"

        with pytest.raises(APIError):
            fr2 = FromOperator('invalid_entity')

    def test_add_query(self):
        fr = FromOperator("facts")
        op = EqualsOperator("certname", "test01")
        fr.add_query(op)

        assert str(fr) == '["from", "facts", ["=", "certname", "test01"]]'

        fr2 = FromOperator("facts")
        op2 = "test, test, test"
        with pytest.raises(APIError):
            fr2.add_query(op2)
        fr2.add_query(op)
        with pytest.raises(APIError):
            fr2.add_query(op)

        fr3 = FromOperator("facts")
        op3 = ExtractOperator()
        op3.add_field(['certname', 'fact_environment', 'catalog_environment'])
        fr3.add_query(op3)

        assert str(fr3) == \
            '["from", "facts", ["extract", '\
            '["certname", "fact_environment", "catalog_environment"]]]'

    def test_limit_offset(self):
        fr = FromOperator("facts")
        op = EqualsOperator("certname", "test01")
        fr.add_query(op)

        fr.add_offset(10)
        assert str(fr) == \
            '["from", "facts", ["=", "certname", "test01"], ["offset", 10]]'

        fr.add_limit(5)
        assert str(fr) == \
            '["from", "facts", ["=", "certname",' \
            ' "test01"], ["limit", 5], ["offset", 10]]'

        fr.add_limit(15)
        assert str(fr) == \
            '["from", "facts", ["=", "certname",' \
            ' "test01"], ["limit", 15], ["offset", 10]]'

        assert repr(fr) == \
            'Query: ["from", "facts", ["=", "certname",' \
            ' "test01"], ["limit", 15], ["offset", 10]]'

        with pytest.raises(APIError):
            fr.add_offset("invalid")

        with pytest.raises(APIError):
            fr.add_limit(["invalid"])

    def test_order_by(self):
        fr = FromOperator("facts")
        op = EqualsOperator("certname", "test01")
        fr.add_query(op)

        o1 = ["certname"]
        o2 = ["certname", ["timestamp", "desc"], "facts"]
        o3inv = ['certname', ['timestamp', 'desc', ['oops']]]

        fr.add_order_by(o1)
        assert str(fr) == \
            '["from", "facts", ["=", "certname", ' \
            '"test01"], ["order_by", ["certname"]]]'

        fr.add_order_by(o2)
        assert repr(fr) == \
            'Query: ["from", "facts", ' \
            '["=", "certname", "test01"], ' \
            '["order_by", ["certname", ' \
            '["timestamp", "desc"], "facts"]]]'

        assert str(fr) == \
            '["from", "facts", ' \
            '["=", "certname", "test01"], ' \
            '["order_by", ["certname", ' \
            '["timestamp", "desc"], "facts"]]]'

        assert str(fr) == \
            '["from", "facts", ' \
            '["=", "certname", "test01"], ' \
            '["order_by", ["certname", ' \
            '["timestamp", "desc"], "facts"]]]'

        with pytest.raises(APIError):
            fr.add_order_by(o3inv)
