from __future__ import unicode_literals
from __future__ import absolute_import

import datetime
import logging
import sys

from pypuppetdb.errors import *

log = logging.getLogger(__name__)

if sys.version_info >= (3, 0):
    unicode = str


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
        if isinstance(field, (str, unicode)):
            field = '"{0}"'.format(field)
        else:
            field = field

        if isinstance(value, (str, unicode, datetime.datetime)):
            value = '"{0}"'.format(value)
        elif isinstance(value, bool):
            value = 'true' if value else 'false'
        else:
            value = value

        self.__string = '["{0}", {1}, {2}]'.format(
            operator,
            field,
            value)

    def __repr__(self):
        return str('Query: {0}'.format(self.__string))

    def __str__(self):
        return str('{0}'.format(self.__string))

    def __unicode__(self):
        return self.__string


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
        elif (type(query) == str or
                isinstance(query, (BinaryOperator, BooleanOperator))):
            self.operations.append(str(query))
        else:
            raise APIError("Can only accpet fixed-string queries, arrays " +
                           "or operator objects")

    def __repr__(self):
        if len(self.operations) == 0:
            raise APIError("At least one query operation is required")
        return 'Query: ["{0}",{1}]'.format(self.operator,
                                           ",".join(self.operations))

    def __str__(self):
        if len(self.operations) == 0:
            raise APIError("At least one query operation is required")
        return str('["{0}",{1}]'.format(self.operator,
                   ",".join(self.operations)))

    def __unicode__(self):
        if len(self.operations) == 0:
            raise APIError("At least one query operation is required")
        return '["{0}",{1}]'.format(self.operator,
                                    ",".join(self.operations))


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
            self.fields.append('"{0}"'.format(str(field)))
        elif isinstance(field, FunctionOperator):
            self.fields.append(str(field))
        else:
            raise APIError("ExtractOperator.add_field only supports "
                           "lists and strings")

    def add_query(self, query):
        if self.query is not None:
            raise APIError("Only one query is supported by ExtractOperator")
        elif isinstance(query, (str, BinaryOperator, BooleanOperator)):
            self.query = str(query)
        else:
            raise APIError("ExtractOperator.add_query only supports "
                           "strings, BinaryOperator and BooleanOperator"
                           "objects")

    def add_group_by(self, field):
        if isinstance(field, list):
            for i in field:
                self.add_group_by(i)
        elif isinstance(field, str):
            if len(self.group_by) == 0:
                self.group_by.append('"group_by"')
            self.group_by.append('"{0}"'.format(str(field)))
        elif isinstance(field, FunctionOperator):
            if len(self.group_by) == 0:
                self.group_by.append('"group_by"')
            self.group_by.append(str(field))
        else:
            raise APIError("ExtractOperator.add_group_by only supports "
                           "lists and strings")

    def __repr__(self):
        if len(self.fields) == 0:
            raise APIError("ExtractOperator needs at least one field")

        arr = ['"extract"']
        arr.append("[{0}]".format(",".join(self.fields)))

        if self.query is not None:
            arr.append(self.query)
        if len(self.group_by) > 0:
            arr.append("[{0}]".format(",".join(self.group_by)))

        return str('Query: [{0}]'.format(",".join(arr)))

    def __str__(self):
        if len(self.fields) == 0:
            raise APIError("ExtractOperator needs at least one field")

        arr = ['"extract"']
        arr.append("[{0}]".format(",".join(self.fields)))

        if self.query is not None:
            arr.append(self.query)
        if len(self.group_by) > 0:
            arr.append("[{0}]".format(",".join(self.group_by)))

        return str('[{0}]'.format(",".join(arr)))

    def __unicode__(self):
        if len(self.fields) == 0:
            raise APIError("ExtractOperator needs at least one field")

        arr = ['"extract"']
        arr.append("[{0}]".format(",".join(self.fields)))

        if self.query is not None:
            arr.append(self.query)
        if len(self.group_by) > 0:
            arr.append("[{0}]".format(",".join(self.group_by)))

        return str('[{0}]'.format(",".join(arr)))


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
        elif (function != "count" and field is None):
            raise APIError("Function {0} requires a field value".format(
                function))
        elif (function == 'to_string' and fmt is None):
            raise APIError("Function {0} requires an extra 'fmt' parameter")

        self.arr = ['"function"', '"{0}"'.format(function)]

        if field is not None:
            self.arr.append('"{0}"'.format(field))

        if function == 'to_string':
            self.arr.append('"{0}"'.format(fmt))

    def __repr__(self):
        return str('Query: [{0}]'.format(",".join(self.arr)))

    def __str__(self):
        return str('[{0}]'.format(",".join(self.arr)))

    def __unicode__(self):
        return str('[{0}]'.format(",".join(self.arr)))


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
