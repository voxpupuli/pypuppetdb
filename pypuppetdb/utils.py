from __future__ import unicode_literals
from __future__ import absolute_import

import warnings
import datetime
from functools import wraps

from pypuppetdb.errors import ExperimentalDisabledError


# A UTC class, see:
# http://docs.python.org/2/library/datetime.html#tzinfo-objects
class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'

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


def experimental(func):
    """This decorator checks if the experimental features of the API are
    enabled. If so it will execute the function and return it's result, if
    not it raises.

    :param func: The function to decorate.
    :type func: :obj:`function`

    :raises: :class:`~pypuppetdb.errors.ExperimentalDisabledError`

    :returns: The result of the decorated function.
    """
    @wraps(func)
    def _experimental(self, *args, **kwargs):
        if self.experimental:
            warnings.warn('This is an experimental feature. Therefor the '
                          'function signature will change when the API '
                          'is finalised.', PendingDeprecationWarning,
                          stacklevel=3)
            return func(self, *args, **kwargs)
        else:
            raise ExperimentalDisabledError
    return _experimental
