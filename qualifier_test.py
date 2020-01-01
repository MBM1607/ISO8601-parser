import datetime as dt

import pytest

from qualifier import parse_iso8601


def test_dates():
    assert parse_iso8601("20170505") == dt.datetime(2017, 5, 5, 0, 0), "YYYYMMDD"
    assert parse_iso8601("2019-12-16") == dt.datetime(2019, 12, 16, 0, 0), "YYYY-MM-DD"
    assert parse_iso8601("0001-01-01") == dt.datetime(1, 1, 1, 0, 0), "First day of the Common Era"
    assert parse_iso8601("9999-12-31") == dt.datetime(9999, 12, 31, 0, 0), "Last day"


def test_datetimes():
    assert parse_iso8601("2017-01-08T12") == dt.datetime(2017, 1, 8, 12, 0), "YYYY-MM-DDThh"
    assert parse_iso8601("2017-01-08T12") == dt.datetime(2017, 1, 8, 12, 0), "YYYY-MM-DDThh"
    assert parse_iso8601("2010-02-18T16:23:48,444") == dt.datetime(2010, 2, 18, 16, 23, 48, 444000), "YYYY-MM-DDThh:mm:ss,sss"
    assert parse_iso8601("2010-02-18T16:23:48.444") == dt.datetime(2010, 2, 18, 16, 23, 48, 444000), "YYYY-MM-DDThh:mm:ss.sss"
    assert parse_iso8601("1890-06-06T05:09:45.123456") == dt.datetime(1890, 6, 6, 5, 9, 45, 123456), "YYYY-MM-DDThh:mm:ss.ssssss"
    assert parse_iso8601("1890-06-06T05:09:45,123456") == dt.datetime(1890, 6, 6, 5, 9, 45, 123456), "YYYY-MM-DDThh:mm:ss,ssssss"


def test_timezones():
    assert parse_iso8601("2017-05-05T12:00:00Z") == dt.datetime(2017, 5, 5, 12, 0, 0, 0, dt.timezone.utc), "YYYY-MM-DDThh:mm:ssZ"
    assert parse_iso8601("1992-10-27T12+05:30") == dt.datetime(1992, 10, 27, 12, 0, 0, 0, dt.timezone(dt.timedelta(hours=5, minutes=30))), "YYYY-MM-DDThh+hh:mm"
    assert parse_iso8601("1994-04-22T12:30-11") == dt.datetime(1994, 4, 22, 12, 30, 0, 0, dt.timezone(dt.timedelta(hours=-11))), "YYYY-MM-DDThh:mm-hh"


def test_ordinal_dates():
    assert parse_iso8601("2019-253") == dt.datetime(2019, 9, 10), "YYYY-DDD"
    assert parse_iso8601("2019031") == dt.datetime(2019, 1, 31), "YYYYDDD"
    assert parse_iso8601("2019001") == dt.datetime(2019, 1, 1), "First ordinal day"
    assert parse_iso8601("2019-365") == dt.datetime(2019, 12, 31), "Last ordinal day"
    assert parse_iso8601("1956-366") == dt.datetime(1956, 12, 31), "Leap Year last ordinal day"


def test_week_dates():
    assert parse_iso8601("2019-W52-2") == dt.datetime(2019, 12, 24), "YYYY-Www-D"
    assert parse_iso8601("2019W521") == dt.datetime(2019, 12, 23), "YYYYWwwD"
    assert parse_iso8601("2009-W01-1") == dt.datetime(2008, 12, 29), "YYYY-Www-D Week 1 edge case"
    assert parse_iso8601("2009W537") == dt.datetime(2010, 1, 3), "YYYYWwwD Week 53 Sun"
    assert parse_iso8601("2004-W53-6") == dt.datetime(2005, 1, 1), "YYYY-Www-D Week 53 Sat"


def test_invalids():
    tst_value_errors("2000-10-16T09:23:61", "second must be in 0..59")
    tst_value_errors("2000-10-16Z", "Invalid ISO-8601 format for date")
    tst_value_errors("2000-10-16T09:23:59+25", "Invalid hour value for utcoffset")
    tst_value_errors("2000-10-16T09:23:06.666-00:60", "Invalid minutes value for utcoffset")
    tst_value_errors("2001-13-16T09:23:06.666-00:30", "month must be in 1..12")
    tst_value_errors("2001-12-32T09:23:06.666-00:30", "day is out of range for month")
    tst_value_errors("2019-W52-8", "Invalid weekday")
    tst_value_errors("1909-W01-0", "Invalid weekday")
    tst_value_errors("2019-W54-7", "Invalid week")
    tst_value_errors("2019-W00-7", "Invalid week")
    tst_value_errors("2001-366", "Invalid ordinal day")
    tst_value_errors("2004-000", "Invalid ordinal day")
    tst_value_errors("2001-12-31T09:23:06.63-00:30", "Invalid ISO-8601 format for time")
    tst_value_errors("2001-07-16T09.12:23:06-00:30", "Invalid ISO-8601 format for time")
    tst_value_errors("2001-07-16T09:23.23:06-00:30", "Invalid ISO-8601 format for time")
    tst_value_errors("20010716T09:24:25Z", "Cannot mix extended and basic format")
    tst_value_errors("1999-04-05T092459", "Cannot mix extended and basic format")


def tst_value_errors(value, error):
    with pytest.raises(ValueError) as excinfo:
        parse_iso8601(value)
    assert str(excinfo.value) == error
