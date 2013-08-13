import datetime

import pytest

from pypuppetdb.utils import UTC, json_to_datetime

pytestmark = pytest.mark.unit

def test_utc():
    utc = UTC()
    assert utc.tzname(None) == 'UTC'
    assert utc.utcoffset(None) == datetime.timedelta(0)
    assert utc.dst(None) == datetime.timedelta(0)

def test_json_to_datetime():
    json_datetime = '2013-08-01T09:57:00.000Z'
    python_datetime = json_to_datetime(json_datetime)
    assert python_datetime.dst() == datetime.timedelta(0)
    assert python_datetime.date() == datetime.date(2013, 8, 1)
    assert python_datetime.tzname() == 'UTC'
    assert python_datetime.utcoffset() == datetime.timedelta(0)
    assert python_datetime.dst() == datetime.timedelta(0)


def test_json_to_datetime_invalid():
    with pytest.raises(ValueError):
        json_to_datetime('2013-08-0109:57:00.000Z')
