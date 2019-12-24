import datetime as dt


ORDINAL_TABLE = [0, 31, 59, 90, 120, 151, 181,
                 212, 243, 273, 304, 334]


def _is_leap_year(year: int) -> bool:
    "Determine whether a year is a leap year"
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _get_date_from_ordinal(year: int, ordinal: int) -> dt.date:
    """Get date from the day and year"""
    day = ordinal
    for i, x in enumerate(ORDINAL_TABLE):
        if ordinal <= x:
            break
        month = i + 1
        day = ordinal - x
    if _is_leap_year(year) and month > 2:
        day -= 1
    return dt.date(year, month, day)


def _parse_date(date: str) -> dt.date:
    """Parse ISO-8601 formatted date"""
    len_date = len(date)

    if len_date == 10:
        # YYYY-Www-D
        if "W" in date:
            pass
        else:
            return dt.date(*map(int, date.split("-")))
    elif len_date == 8:
        # YYYY-DDD
        if "-" in date:
            year, ordinal = map(int, date.split("-"))
            return _get_date_from_ordinal(year, ordinal)
        # YYYYWwwD
        elif "W" in date:
            pass
        # YYYYMMDD
        else:
            return dt.date(*map(int, (date[:4], date[4:6], date[6:])))
    # YYYYDDD
    elif len_date == 7:
        year, ordinal = int(date[:4]), int(date[4:])
        return _get_date_from_ordinal(year, ordinal)
    else:
        raise ValueError("Invalid ISO-8601 format for date")


def _parse_time(time: str) -> dt.time:
    """Parse ISO-8601 formatted time"""

    if "Z" in time:
        time = time.strip("Z")
        tzinfo = dt.timezone.utc
    elif "+" in time or "-" in time:
        for sign in ("+", "-"):
            if sign in time:
                time, utc = time.split(sign)
                if ":" in utc:
                    hours = int(sign + utc[:2])
                    minutes = int(sign + utc[3:])
                elif len(utc) == 4:
                    hours = int(sign + utc[:2])
                    minutes = int(sign + utc[2:])
                else:
                    hours = int(sign + utc)
                    minutes = 0
                # As far as I can tell current min max timezones are -12 and +14 but some historical
                # timezones were larger so the limit is -16 to 16
                if hours < -16 or hours > 16:
                    raise ValueError("Invalid hour value for utcoffset")
                elif minutes < -59 or minutes > 59:
                    raise ValueError("Invalid minutes value for utcoffset")
                tzinfo = dt.timezone(dt.timedelta(hours=hours, minutes=minutes))
    else:
        tzinfo = None

    # Get the microsecond
    if len(time) in (10, 12, 15) and ("." in time or "," in time):
        if "." in time:
            time, second_factor = time.split(".")
        elif "," in time:
            time, second_factor = time.split(",")
        if len(second_factor) == 3:
            microsecond = int(second_factor) * 1000
        else:
            microsecond = int(second_factor)
    else:
        microsecond = 0

    len_time = len(time)

    if ":" in time:
        # hh:mm:ss
        if len_time == 8:
            return dt.time(*map(int, time.split(":")), microsecond, tzinfo)
        # hh:mm
        elif len_time == 5:
            return dt.time(*map(int, time.split(":")), tzinfo=tzinfo)
        else:
            raise ValueError("Invalid ISO-8601 format for time")
    # hhmmss
    elif len_time == 6:
        return dt.time(*map(int, (time[:2], time[2:4], time[4:])), microsecond, tzinfo)
    # hhmm
    elif len_time == 4:
        return dt.time(*map(int, *(time[:2], time[2:])), tzinfo=tzinfo)
    # hh
    elif len_time == 2:
        return dt.time(int(time), tzinfo=tzinfo)
    else:
        raise ValueError("Invalid ISO-8601 format for time")


def parse_iso8601(timestamp: str) -> dt.datetime:
    """Parse an ISO-8601 formatted time stamp."""
    if "T" in timestamp:
        date, time = timestamp.split("T")
        time = _parse_time(time)
    else:
        date = timestamp
        time = dt.time.min
    date = _parse_date(date)
    return dt.datetime.combine(date, time)
