from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import json
import logging

from pypuppetdb.errors import APIError

log = logging.getLogger(__name__)


class BinaryOperator(object):
    """
    This is a parent helper class used to create PuppetDB AST queries
    for single key-value pairs for the available operators.

    It is possible to directly declare the various types of queries
    from this class. For instance the code
    BinaryOperator('=', 'certname', 'node1.example.com') generates the
    PuppetDB query '["=", "certname", "node1.example.com"]'. It is preferred
    to use the child classes as they may have restrictions specific
    to that operator.

    See
    https://docs.puppet.com/puppetdb/4.0/api/query/v4/ast.html#binary-operators
    for more information.

    :param operator: The binary query operation performed. There is
        no value checking on this field.
    :type operator: :obj:`string`
    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: The values of the field to match, or not match.
    :type value: any
    """

    def __init__(self, operator, field, value):
        if isinstance(value, datetime.datetime):
            value = str(value)
        self.data = [operator, field, value]

    def __repr__(self):
        return 'Query: {0}'.format(self)

    def __str__(self):
        return json.dumps(self.json_data())

    def json_data(self):
        return self.data


class BooleanOperator(object):
    """
    This is a parent helper class used to create PuppetDB AST queries
    for available boolean queries.

    It is possible to directly declare a boolean query from this class.
    For instance the code BooleanOperator("and") will create an empty
    query '["and",]'. An error will be raised if there are no queries
    added via :func:`~pypuppetdb.QueryBuilder.BooleanOperator.add`

    See
    https://docs.puppet.com/puppetdb/4.0/api/query/v4/ast.html#binary-operators
    for more information.

    :param operator: The boolean query operation to perform.
    :type operator: :obj:`string`
    """

    def __init__(self, operator):
        self.operator = operator
        self.operations = []

    def add(self, query):
        if type(query) == list:
            for i in query:
                self.add(i)
        elif type(query) == str:
            self.operations.append(json.loads(query))
        elif isinstance(query, (BinaryOperator, InOperator,
                                BooleanOperator)):
            self.operations.append(query.json_data())
        else:
            raise APIError("Can only accept fixed-string queries, arrays " +
                           "or operator objects")

    def __repr__(self):
        return 'Query: {0}'.format(self)

    def __str__(self):
        return json.dumps(self.json_data())

    def json_data(self):
        if len(self.operations) == 0:
            raise APIError("At least one query operation is required")
        return [self.operator] + self.operations


class ExtractOperator(object):
    """
    Queries that either do not or cannot require all the key-value pairs
    from an endpoint can use the Extract Operator as described in
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#projection-operators.

    The syntax of this operator requires a function and/or a list of fields,
    an optional standard query and an optional group by clause including a
    list of fields.
    """

    def __init__(self):
        self.fields = []
        self.query = None
        self.group_by = []

    def add_field(self, field):
        if isinstance(field, list):
            for i in field:
                self.add_field(i)
        elif isinstance(field, str):
            self.fields.append(field)
        elif isinstance(field, FunctionOperator):
            self.fields.append(field.json_data())
        else:
            raise APIError("ExtractOperator.add_field only supports "
                           "lists and strings")

    def add_query(self, query):
        if self.query is not None:
            raise APIError("Only one query is supported by ExtractOperator")
        elif isinstance(query, str):
            self.query = json.loads(query)
        elif isinstance(query, (BinaryOperator, SubqueryOperator,
                                BooleanOperator)):
            self.query = query.json_data()
        else:
            raise APIError("ExtractOperator.add_query only supports "
                           "strings, BinaryOperator, BooleanOperator "
                           "and SubqueryOperator objects")

    def add_group_by(self, field):
        if isinstance(field, list):
            for i in field:
                self.add_group_by(i)
        elif isinstance(field, str):
            if len(self.group_by) == 0:
                self.group_by.append('group_by')
            self.group_by.append(field)
        elif isinstance(field, FunctionOperator):
            if len(self.group_by) == 0:
                self.group_by.append('group_by')
            self.group_by.append(field.json_data())
        else:
            raise APIError("ExtractOperator.add_group_by only supports "
                           "lists, strings, and FunctionOperator objects")

    def __repr__(self):
        return 'Query: {0}'.format(self)

    def __str__(self):
        return json.dumps(self.json_data())

    def json_data(self):
        if len(self.fields) == 0:
            raise APIError("ExtractOperator needs at least one field")

        arr = ['extract', self.fields]

        if self.query is not None:
            arr.append(self.query)
        if len(self.group_by) > 0:
            arr.append(self.group_by)

        return arr


class FunctionOperator(object):
    """
    Performs an aggregate function on the result of a subquery, full
    documentation is available at
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#function.
    This object can only be used in the field list or group by list of
    an ExtractOperator object.

    :param function: The name of the function to perform.
    :type function: :obj:`str`
    :param field: The name of the field to perform the function on. All
        functions with the exception of count require this value.
    :type field: :obj:`str`
    """

    def __init__(self, function, field=None, fmt=None):
        if function not in ['count', 'avg', 'sum', 'min', 'max', 'to_string']:
            raise APIError("Unsupport function: {0}".format(function))
        elif function != "count" and field is None:
            raise APIError("Function {0} requires a field value".format(
                function))
        elif function == 'to_string' and fmt is None:
            raise APIError("Function {0} requires an extra 'fmt' parameter")

        self.arr = ['function', function]

        if field is not None:
            self.arr.append(field)

        if function == 'to_string':
            self.arr.append(fmt)

    def __repr__(self):
        return 'Query: {0}'.format(self)

    def __str__(self):
        return json.dumps(self.json_data())

    def json_data(self):
        return self.arr


class SubqueryOperator(object):
    """
    Performs a subquery to another puppetDB object, full
    documentation is available at
    https://docs.puppet.com/puppetdb/3.2/api/query/v4/operators.html#subquery-operators
    This object must be used in combination with the InOperator according
    to documentation.

    :param endpoint: The name of the subquery object
    :type function: :obj:`str`
    """

    def __init__(self, endpoint):
        if endpoint not in ['catalogs', 'edges', 'environments', 'events',
                            'facts', 'fact_contents', 'fact_paths', 'nodes',
                            'reports', 'resources']:
            raise APIError("Unsupported endpoint: {0}".format(endpoint))

        self.query = None
        self.arr = ['select_{0}'.format(endpoint)]

    def add_query(self, query):
        if self.query is not None:
            raise APIError("Only one query is supported by ExtractOperator")
        else:
            self.query = True
            self.arr.append(query.json_data())

    def __repr__(self):
        return 'Query: {0}'.format(self)

    def __str__(self):
        return json.dumps(self.json_data())

    def json_data(self):
        return self.arr


class InOperator(object):
    """
    Performs boolean compare between a field a subquery result
    https://docs.puppet.com/puppetdb/3.2/api/query/v4/operators.html#subquery-operators
    This object must be used in combination with the SubqueryOperator according
    to documentation.

    :param field: The name of the subquery object
    :type function: :obj:`str`
    """

    def __init__(self, field):
        self.query = None
        self.arr = ['in', field]

    def add_query(self, query):
        if self.query is not None:
            raise APIError("Only one query is supported by ExtractOperator")
        elif isinstance(query, str):
            self.query = True
            self.arr.append(json.loads(query))
        elif isinstance(query, (ExtractOperator, FromOperator)):
            self.query = True
            self.arr.append(query.json_data())
        else:
            raise APIError("InOperator.add_query only supports "
                           "strings, ExtractOperator, and"
                           "FromOperator objects")

    def add_array(self, values):
        if self.query is not None:
            raise APIError("Only one array is supported by the InOperator")
        elif isinstance(values, list):
            def depth(l):
                return (isinstance(l, list) and len(l) != 0) \
                       and max(map(depth, l)) + 1

            if depth(values) == 1:
                self.query = True
                self.arr.append(['array', values])
            else:
                raise APIError("InOperator.add_array: cannot pass in "
                               "nested arrays (or empty arrays)")
        else:
            raise APIError("InOperator.add_array: Ill-formatted array, "
                           "must be of the format: "
                           "['array', [<array values>]]")

    def __repr__(self):
        return 'Query: {0}'.format(self)

    def __str__(self):
        return json.dumps(self.json_data())

    def json_data(self):
        return self.arr


class FromOperator(object):
    """
    From contextual operator that allows for queries on the root endpoint
    or subqueries into other entities:
    https://puppet.com/docs/puppetdb/5.1/api/query/v4/ast.html#from

    Ex.)
    fr = FromOperator("facts")
    fr.add_query(EqualsOperator("foo", "bar"))
    fr.add_order_by(["certname"])
    fr.add_limit(10)

    note: only supports single entity From operations
    """

    def __init__(self, endpoint):
        valid_entities = ["aggregate_event_counts", "catalogs", "edges",
                          "environments", "event_counts", "events", "facts",
                          "fact_contents", "fact_names", "fact_paths", "nodes",
                          "producers", "reports", "resources"]

        if endpoint in valid_entities:
            self.endpoint = endpoint
        else:
            raise APIError("Endpoint is invalid. Must be "
                           "one of the following : %s"
                           % valid_entities)

        self.query = None
        self.order_by = []
        self.limit = None
        self.offset = None

    def add_query(self, query):
        if self.query is not None:
            raise APIError("Only one main query is supported by FromOperator")
        elif isinstance(query, (InOperator, ExtractOperator,
                                BinaryOperator, BooleanOperator,
                                FunctionOperator)):
            self.query = query.json_data()
        else:
            raise APIError("FromOperator.add_field only supports "
                           "Operator Objects")

    def add_order_by(self, fields):
        def depth(l):
            return isinstance(l, list) and max(map(depth, l)) + 1

        fields_depth = depth(fields)

        if isinstance(fields, list):
            if fields_depth == 1 or fields_depth == 2:
                self.order_by = fields
            else:
                raise APIError("ExtractOperator.add_order_by only "
                               "supports lists of fields of depth "
                               "one or two: [value, <desc/asc>] or "
                               "[value]")
        else:
            raise APIError("ExtractOperator.add_group_by only supports "
                           "lists of one or more fields")

    def add_limit(self, lim):
        if isinstance(lim, int):
            self.limit = lim
        else:
            raise APIError("ExtractOperator.add_limit only supports ints")

    def add_offset(self, off):
        if isinstance(off, int):
            self.offset = off
        else:
            raise APIError("ExtractOperator.add_offset only supports ints")

    def __repr__(self):
        return 'Query: {0}'.format(self)

    def __str__(self):
        return json.dumps(self.json_data())

    def json_data(self):
        if self.query is None:
            raise APIError("FromOperator needs one main query")

        arr = ['from', self.endpoint, self.query]

        if len(self.order_by) > 0:
            arr.append(['order_by', self.order_by])
        if self.limit is not None:
            arr.append(['limit', self.limit])
        if self.offset is not None:
            arr.append(['offset', self.offset])

        return arr


class EqualsOperator(BinaryOperator):
    """
    Builds an equality filter based on the supplied field-value pair as
    described
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#equality.

    In order to create the following query:

    ["=", "environment", "production"]

    The following code can be used.

    EqualsOperator('environment', 'production')

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: The value of the field to match, or not match.
    :type value: any
    """

    def __init__(self, field, value):
        super(EqualsOperator, self).__init__("=", field, value)


class GreaterOperator(BinaryOperator):
    """
    Builds a greater-than filter based on the supplied field-value pair as
    described
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#greater-than.

    In order to create the following query:

    [">", "catalog_timestamp", "2016-06-01 00:00:00"]

    The following code can be used.

    GreaterOperator('catalog_timestamp', datetime.datetime(2016, 06, 01))

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: Matches if the field is greater than this value.
    :type value: Number, timestamp or array
    """

    def __init__(self, field, value):
        super(GreaterOperator, self).__init__(">", field, value)


class LessOperator(BinaryOperator):
    """
    Builds a less-than filter based on the supplied field-value pair as
    described
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#less-than.

    In order to create the following query:

    ["<", "catalog_timestamp", "2016-06-01 00:00:00"]

    The following code can be used.

    LessOperator('catalog_timestamp', datetime.datetime(2016, 06, 01))

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: Matches if the field is less than this value.
    :type value: Number, timestamp or array
    """

    def __init__(self, field, value):
        super(LessOperator, self).__init__("<", field, value)


class GreaterEqualOperator(BinaryOperator):
    """
    Builds a greater-than or equal-to filter based on the supplied
    field-value pair as described
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#greater-than-or-equal-to.

    In order to create the following query:

    [">=", "facts_timestamp", "2016-06-01 00:00:00"]

    The following code can be used.

    GreaterEqualOperator('facts_timestamp', datetime.datetime(2016, 06, 01))

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: Matches if the field is greater than or equal to\
        this value.
    :type value: Number, timestamp or array
    """

    def __init__(self, field, value):
        super(GreaterEqualOperator, self).__init__(">=", field, value)


class LessEqualOperator(BinaryOperator):
    """
    Builds a less-than or equal-to filter based on the supplied
    field-value pair as described
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#less-than-or-equal-to.

    In order to create the following query:

    ["<=", "facts_timestamp", "2016-06-01 00:00:00"]

    The following code can be used.

    LessEqualOperator('facts_timestamp', datetime.datetime(2016, 06, 01))

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: Matches if the field is less than or equal to\
        this value.
    :type value: Number, timestamp or array
    """

    def __init__(self, field, value):
        super(LessEqualOperator, self).__init__("<=", field, value)


class RegexOperator(BinaryOperator):
    """
    Builds a regular expression filter based on the supplied field-value
    pair as described
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#regexp-match.

    In order to create the following query:

    ["~", "certname", "www\\d+\\.example\\.com"]

    The following code can be used.

    RegexOperator('certname', 'www\\d+\\.example\\.com')

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: Matches if the field matches this regular expression.
    :type value: :obj:`string`
    """

    def __init__(self, field, value):
        super(RegexOperator, self).__init__("~", field, value)


class RegexArrayOperator(BinaryOperator):
    """
    Builds a regular expression array filter based on the supplied
    field-value pair. This query only works on fields with paths as
    described
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#regexp-array-match.

    In order to create the following query:

    ["~", "path", ["networking", "eth.*", "macaddress"]]

    The following code can be used.

    RegexArrayOperator('path', ["networking", "eth.*", "macaddress"])

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: Matches if the field matches this regular expression.
    :type value: :obj:`list`
    """

    def __init__(self, field, value):
        super(RegexArrayOperator, self).__init__("~>", field, value)


class NullOperator(BinaryOperator):
    """
    Builds a null filter based on the field and boolean value pair as
    described
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#null-is-null.
    This filter only works on field that may be null. Value may only
    be True or False.

    In order to create the following query:

    ["null?", "deactivated", true]

    The following code can be used.

    NullOperator('deactivated', True)

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: Matches if the field value is null (if True) or\
        not null (if False)
    :type value: :obj:`bool`
    """

    def __init__(self, field, value):
        if type(value) != bool:
            raise APIError("NullOperator value must be boolean")

        super(NullOperator, self).__init__("null?", field, value)


class AndOperator(BooleanOperator):
    """
    Builds an AND boolean filter. Only results that match ALL
    criteria from the included query strings will be returned
    from PuppetDB. Full documentation is available
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#and

    In order to create the following query:

    ["and",
      ["=", "catalog_environment", "production"],
      ["=", "facts_environment", "production"]]

    The following code can be used:

    op = AndOperator()
    op.add(EqualsOperator("catalog_environment", "production"))
    op.add(EqualsOperator("facts_environment", "production"))
    """

    def __init__(self):
        super(AndOperator, self).__init__("and")


class OrOperator(BooleanOperator):
    """
    Builds an OR boolean filter. Only results that match ANY
    criteria from the included query strings will be returned
    from PuppetDB. Full documentation is available
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#or.

    In order to create the following query:

    ["or", ["=", "name", "hostname"], ["=", "name", "architecture"]]

    The following code can be used:

    op = OrOperator()
    op.add(EqualsOperator("name", "hostname"))
    op.add(EqualsOperator("name", "architecture"))
    """

    def __init__(self):
        super(OrOperator, self).__init__("or")


class NotOperator(BooleanOperator):
    """
    Builds a NOT boolean filter. Only results that DO NOT match
    criteria from the included query strings will be returned
    from PuppetDB. Full documentation is available
    https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html#not

    Unlike the other Boolean Operator objects this operator only
    accepts a single query string.

    In order to create the following query:

    ["not", ["=", "osfamily", "RedHat"]]

    The following code can be used.

    op = NotOperator()
    op.add(EqualsOperator("osfamily", "RedHat"))
    """

    def __init__(self):
        super(NotOperator, self).__init__("not")

    def add(self, query):
        if len(self.operations) > 0:
            raise APIError("This operator only accept one query string")
        elif isinstance(query, list) and len(query) > 1:
            raise APIError("This operator only accept one query string")
        super(NotOperator, self).add(query)
