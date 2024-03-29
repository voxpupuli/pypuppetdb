import datetime


# A UTC class, see:
# http://docs.python.org/2/library/datetime.html#tzinfo-objects
class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

    def __repr__(self):
        return "<UTC>"

    def __str__(self):
        return "UTC"

    def __unicode__(self):
        return "UTC"


def json_to_datetime(date):
    """Tranforms a JSON datetime string into a timezone aware datetime
    object with a UTC tzinfo object.

    :param date: The datetime representation.
    :type date: :obj:`string`

    :returns: A timezone aware datetime object.
    :rtype: :class:`datetime.datetime`
    """
    return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=UTC()
    )
