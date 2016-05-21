from __future__ import unicode_literals
from __future__ import absolute_import

import logging

log = logging.getLogger(__name__)


class BinaryOperator(object):
    """
    This is a parent helper class used to create PuppetDB AST queries
    for single key-value pairs for the available operators. See
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
        self.operator = operator

        if type(field) == str:
            self.field = '"' + field + '"'
        else:
            self.field = field

        if type(value) == str:
            self.value = '"' + value + '"'
        else:
            self.value = value

        self.__string = '["{0}", {1}, {2}]'.format(
            self.operator,
            self.field,
            self.value)

    def __repr__(self):
        return str('Query: {0}'.format(self.__string))

    def __str__(self):
        return str('{0}'.format(self.__string))

    def __unicode__(self):
        return self.__string


class BooleanOperator(object):
    """
    This is a parent helper class used to create PuppetDB AST queries
    for available boolean queries. See
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
            raise ValueError("Can only accpet fixed-string queries, arrays " +
                             "or operator objects")

    def __repr__(self):
        return 'Query: ["{0}",{1}]'.format(self.operator,
                                           ",".join(self.operations))

    def __str__(self):
        return str('["{0}",{1}]'.format(self.operator,
                   ",".join(self.operations)))

    def __unicode__(self):
        return '["{0}",{1}]'.format(self.operator,
                                    ",".join(self.operations))


class EqualsOperator(BinaryOperator):
    """
    Builds an equality filter based on the supplied field-value pair.

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
    Builds a greater-than filter based on the supplied field-value pair.

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
    Builds a less-than filter based on the supplied field-value pair.

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
    field-value pair.

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
    field-value pair.

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
    pair.

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
    field-value pair. This query only works on fields with paths.

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
    Builds a null filter based on the field and boolean value pair.
    This filter only works on field that may be null. Value may only
    be True or False

    :param field: The PuppetDB endpoint query field. See endpoint
                  documentation for valid values.
    :type field: any
    :param value: Matches if the field value is null (if True) or\
        not null (if False)
    :type value: :obj:`bool`
    """
    def __init__(self, field, value):
        if type(value) != bool:
            raise ValueError("NullOperator value must be boolean")

        super(NullOperator, self).__init__("null?", field, value)


class AndOperator(BooleanOperator):
    """
    Builds an AND boolean filter. Only results that match ALL
    criteria from the included query strings will be returned
    from PuppetDB.
    """
    def __init__(self):
        super(AndOperator, self).__init__("and")


class OrOperator(BooleanOperator):
    """
    Builds an OR boolean filter. Only results that match ANY
    criteria from the included query strings will be returned
    from PuppetDB.
    """
    def __init__(self):
        super(OrOperator, self).__init__("or")


class NotOperator(BooleanOperator):
    """
    Builds a NOT boolean filter. Only results that DO NOT match
    criteria from the included query strings will be returned
    from PuppetDB.

    Unlike the other Boolean Operator objects this operator only
    accepts a single query string.
    """
    def __init__(self):
        super(NotOperator, self).__init__("not")

    def add(self, query):
        if len(self.operations) > 0:
            raise ValueError("This operator only accept one query string")
        super(NotOperator, self).add(query)
