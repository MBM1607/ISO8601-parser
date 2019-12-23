import datetime


def parse_iso8601_date(date: str) -> datetime.date:
    """Parse ISO-8601 formatted date"""
    if len(date) == 10:
        return datetime.date(*map(int, date.split("-")))
    elif len(date) == 8:
        return datetime.date(*map(int, (date[:4], date[4:6], date[6:])))
    else:
        raise ValueError("Invalid ISO-8601 format for date")


def parse_iso8601_time(time: str) -> datetime.time:
    """Parse ISO-8601 formatted time"""
    pass


def parse_iso8601(timestamp: str) -> datetime.datetime:
    """Parse an ISO-8601 formatted time stamp."""

    if "T" in timestamp:
        date, time = timestamp.split("T")
        time = parse_iso8601_time(time)
    else:
        date = timestamp
        time = datetime.time(0, 0, 0, 0, None)

    date = parse_iso8601_date(date)

    return datetime.datetime.combine(date, time)


if __name__ == "__main__":
    assert parse_iso8601("20170505") == datetime.datetime(2017, 5, 5, 0, 0), "YYYYMMDD"
    assert parse_iso8601("2019-12-16") == datetime.datetime(2019, 12, 16, 0, 0), "YYYY-MM-DD"
    assert parse_iso8601("2017-01-08T12") == datetime.datetime(2017, 1, 8, 12, 0), "YYYY-MM-DDThh"
    assert parse_iso8601("2017-01-08T12") == datetime.datetime(2017, 1, 8, 12, 0), "YYYY-MM-DDThh"
    assert parse_iso8601("2000-10-16T09:23:61") == ValueError("Invalid value for seconds")
