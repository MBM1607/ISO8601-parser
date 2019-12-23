import datetime


def parse_iso8601_date(date: str) -> datetime.date:
    """Parse ISO-8601 formatted date"""
    len_date = len(date)

    #YYYY-MM-DD
    if len_date == 10:
        return datetime.date(*map(int, date.split("-")))
    elif len_date == 8:
        #Week date
        if "-" in date and "W" in date:
            pass
        #Ordinal date
        elif "-" in date:
            pass
        #YYYYMMDD
        else:
            return datetime.date(*map(int, (date[:4], date[4:6], date[6:])))
    elif len_date == 7:
        #Truncated Week date
        if "W" in date:
            pass
        #Truncated Ordinal date
        else:
            pass
    else:
        raise ValueError("Invalid ISO-8601 format for date")


def parse_iso8601_time(time: str) -> datetime.time:
    """Parse ISO-8601 formatted time"""
    #Get the microsecond
    if len(time) in (10, 12, 15):
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
        #hh:mm:ss
        if len_time == 8:
            return datetime.time(*map(int, time.split(":")), microsecond)
        #hh:mm
        elif len_time == 5:
            return datetime.time(*map(int, time.split(":")))
    #hhmmss
    elif len_time == 6:
        return datetime.time(*map(int, (time[:2], time[2:4], time[4:])), microsecond)
    #hhmm
    elif len_time == 4:
        return datetime.time(*map(int, *(time[:2], time[2:])))
    #hh
    elif len_time == 2:
        return datetime.time(int(time))
    else:
        raise ValueError("Invalid ISO-8601 format for time")


def parse_iso8601(timestamp: str) -> datetime.datetime:
    """Parse an ISO-8601 formatted time stamp."""

    if "T" in timestamp:
        date, time = timestamp.split("T")
        time = parse_iso8601_time(time)
    else:
        date = timestamp
        time = datetime.time.min

    date = parse_iso8601_date(date)

    print(datetime.datetime.combine(date, time))
    return datetime.datetime.combine(date, time)


if __name__ == "__main__":
    assert parse_iso8601("20170505") == datetime.datetime(2017, 5, 5, 0, 0), "YYYYMMDD"
    assert parse_iso8601("2019-12-16") == datetime.datetime(2019, 12, 16, 0, 0), "YYYY-MM-DD"
    assert parse_iso8601("2017-01-08T12") == datetime.datetime(2017, 1, 8, 12, 0), "YYYY-MM-DDThh"
    assert parse_iso8601("2017-01-08T12") == datetime.datetime(2017, 1, 8, 12, 0), "YYYY-MM-DDThh"
    assert parse_iso8601("2010-02-18T16:23:48,444") == datetime.datetime(2010, 2, 18, 16, 23, 48, 444000)
    try:
        parse_iso8601("2000-10-16T09:23:61")
    except ValueError as e:
        print(e)
