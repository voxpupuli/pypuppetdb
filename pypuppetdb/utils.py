from __future__ import unicode_literals
from __future__ import absolute_import

import warnings
import datetime
import re


# A UTC class, see:
# http://docs.python.org/2/library/datetime.html#tzinfo-objects
class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return str('UTC')

    def dst(self, dt):
        return datetime.timedelta(0)

    def __repr__(self):
        return str('<UTC>')

    def __str__(self):
        return str('UTC')

    def __unicode__(self):
        return 'UTC'


def json_to_datetime(date):
    """Tranforms a JSON datetime string into a timezone aware datetime
    object with a UTC tzinfo object.

    :param date: The datetime representation.
    :type date: :obj:`string`

    :returns: A timezone aware datetime object.
    :rtype: :class:`datetime.datetime`
    """
    return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').replace(
        tzinfo=UTC())


def versioncmp(v1, v2):
    """Compares two objects, x and y, and returns an integer according to the
    outcome. The return value is negative if x < y, zero if x == y and
    positive if x > y.

    :param v1: The first object to compare.
    :param v2: The second object to compare.

    :returns: -1, 0 or 1.
    :rtype: :obj:`int`
    """
    def normalize(v):
        """Removes leading zeroes from right of a decimal point from v and
        returns an array of values separated by '.'

        :param v: The data to normalize.

        :returns: An list representation separated by '.' with all leading
            zeroes stripped.
        :rtype: :obj:`list`
        """
        return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]
    try:
        return cmp(normalize(v1), normalize(v2))
    except NameError:
        return (normalize(v1) > normalize(v2)) - (
            normalize(v1) < normalize(v2))
