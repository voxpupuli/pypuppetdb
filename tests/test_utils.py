from __future__ import unicode_literals

import sys

import pytest
import pypuppetdb
import datetime

if sys.version_info >= (3, 0):
    unicode = str


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
        assert 'UTC' == unicode(utc)

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


class TestVersionCmp(object):
    """Test the versioncmp function using different criteria."""

    def test_versioncmp(self):
        assert pypuppetdb.utils.versioncmp('1', '1') == 0
        assert pypuppetdb.utils.versioncmp('2.1', '2.2') < 0
        assert pypuppetdb.utils.versioncmp('3.0.4.10', '3.0.4.2') > 0
        assert pypuppetdb.utils.versioncmp('4.08', '4.08.1') < 0
        assert pypuppetdb.utils.versioncmp('3.2.1.9.8144', '3.2') > 0
        assert pypuppetdb.utils.versioncmp('3.2', '3.2.1.9.8144') < 0
        assert pypuppetdb.utils.versioncmp('1.2', '2.1') < 0
        assert pypuppetdb.utils.versioncmp('2.1', '1.2') > 0
        assert pypuppetdb.utils.versioncmp('5.6.7', '5.6.7') == 0
        assert pypuppetdb.utils.versioncmp('1.01.1', '1.1.1') == 0
        assert pypuppetdb.utils.versioncmp('1.1.1', '1.01.1') == 0
        assert pypuppetdb.utils.versioncmp('1', '1.0') == 0
        assert pypuppetdb.utils.versioncmp('1.0', '1') == 0
        assert pypuppetdb.utils.versioncmp('1.0', '1.0.1') < 0
        assert pypuppetdb.utils.versioncmp('1.0.1', '1.0') > 0
        assert pypuppetdb.utils.versioncmp('1.0.2.0', '1.0.2') == 0
