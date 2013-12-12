from __future__ import unicode_literals

import pytest
import pypuppetdb
import datetime


class TestUTC(object):
    """Test the UTC class."""

    def test_utc_offset(self, utc):
        assert datetime.timedelta(0) == utc.utcoffset(300)

    def test_tzname(self, utc):
        assert str('UTC') == utc.tzname(300)

    def test_dst(self, utc):
        assert datetime.timedelta(0) == utc.dst(300)

    def test_magic_str(self, utc):
        assert str('UTC') == str(utc)

    def test_magic_unicode(self, utc):
        assert unicode('UTC') == unicode(utc)

    def test_magic_repr(self, utc):
        assert str('<UTC>') == repr(utc)


class TestJSONToDateTime(object):
    """Test the json_to_datetime function."""

    def test_json_to_datetime(self):
        json_datetime = '2013-08-01T09:57:00.000Z'
        python_datetime = pypuppetdb.utils.json_to_datetime(json_datetime)
        assert python_datetime.dst() == datetime.timedelta(0)
        assert python_datetime.date() == datetime.date(2013, 8, 1)
        assert python_datetime.tzname() == 'UTC'
        assert python_datetime.utcoffset() == datetime.timedelta(0)
        assert python_datetime.dst() == datetime.timedelta(0)

    def test_json_to_datetime_invalid(self):
        with pytest.raises(ValueError):
            pypuppetdb.utils.json_to_datetime('2013-08-0109:57:00.000Z')
