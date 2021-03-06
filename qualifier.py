import datetime as dt
from math import modf
from functools import lru_cache
from typing import Tuple


ORDINAL_TABLE = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


@lru_cache(maxsize=8)
def _is_leap_year(year: int) -> bool:
	"""Determine whether a year is a leap year"""
	return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


@lru_cache(maxsize=8)
def _days_in_year(year: int) -> int:
	"""Get the number of days in a year"""
	return 365 + _is_leap_year(year)


def _validate_format(date: str, time: str) -> None:
	"""Raise a value error if date and time are not both in the same format"""
	if "-" in date and ":" not in time and len(time) != 2 or "-" not in date and ":" in time:
		raise ValueError("Cannot mix extended and basic format")


def _get_date_from_ordinal(year: int, ordinal: int) -> dt.date:
	"""Get date from the ordinal day and year"""
	if ordinal < 1 or ordinal > _days_in_year(year):
		raise ValueError("Invalid ordinal day")

	day = ordinal
	for i, x in enumerate(ORDINAL_TABLE):
		if ordinal <= x:
			break
		month = i + 1
		day = ordinal - x
	if _is_leap_year(year) and month > 2:
		day -= 1
	return dt.date(year, month, day)


def _get_date_from_week_date(year: int, week: int, weekday: int) -> dt.date:
	"""Get date from week number and weekday"""
	if weekday < 1 or weekday > 7:
		raise ValueError("Invalid weekday")
	elif week < 1 or week > 53:
		raise ValueError("Invalid week")

	ordinal = week * 7 + weekday - (dt.date(year, 1, 4).weekday() + 4)
	if ordinal < 1:
		year -= 1
		ordinal += _days_in_year(year)
	elif ordinal > _days_in_year(year):
		ordinal -= _days_in_year(year)
		year += 1
	return _get_date_from_ordinal(year, ordinal)


def _parse_date(date: str) -> dt.date:
	"""Parse ISO-8601 formatted date"""
	len_date = len(date)

	if len_date == 10:
		# YYYY-Www-D
		if "W" in date:
			return _get_date_from_week_date(int(date[:4]), int(date[6:8]), int(date[9]))
		else:
			return dt.date(*map(int, date.split("-")))
	elif len_date == 8:
		# YYYY-DDD
		if "-" in date:
			return _get_date_from_ordinal(*map(int, date.split("-")))
		# YYYYWwwD
		elif "W" in date:
			return _get_date_from_week_date(int(date[:4]), int(date[5:7]), int(date[7]))
		# YYYYMMDD
		else:
			return dt.date(*map(int, (date[:4], date[4:6], date[6:])))
	# YYYYDDD
	elif len_date == 7:
		return _get_date_from_ordinal(int(date[:4]), int(date[4:]))
	else:
		raise ValueError("Invalid ISO-8601 format for date")


def _parse_timezone(time: str) -> Tuple[str, str]:
	"""Parse the timezone and return the seperated time and timezone"""
	if "Z" in time:
		return time.strip("Z"), dt.timezone.utc
	else:
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
				return time, dt.timezone(dt.timedelta(hours=hours, minutes=minutes))

	return time, None


def _solve_fractional_minutes(frac_min: float) -> Tuple[int, int]:
	"""Extract seconds and microseconds from the fractional minutes"""
	frac_min *= 60
	if frac_min.is_integer():
		return int(frac_min), 0
	else:
		microseconds, seconds = modf(frac_min)
		return int(seconds), round(microseconds * 1000000)


def _solve_fractional_hours(frac_hour: float) -> Tuple[int, int, int]:
	frac_hour *= 60
	if frac_hour.is_integer():
		return int(frac_hour), 0, 0
	else:
		frac_min, minutes = modf(frac_hour)
		seconds, microseconds = _solve_fractional_minutes(frac_min)
		return int(minutes), seconds, microseconds


def _parse_time(time: str) -> dt.time:
	"""Parse ISO-8601 formatted time"""

	time, tzinfo = _parse_timezone(time)
	minutes, seconds, microseconds, fraction = 0, 0, 0, None

	# Get the fractions
	try:
		for dot in (".", ","):
			if dot in time:
				time, fraction = time.split(dot)
				len_time = len(time)
				fraction = float("." + fraction)
				break
		else:
			len_time = len(time)

	except ValueError:
		raise ValueError("Invalid fractional value for time")

	if ":" in time:
		# hh:mm:ss
		if len_time == 8:
			if fraction:
				microseconds = round(fraction * 1000000)
			return dt.time(*map(int, time.split(":")), microseconds, tzinfo=tzinfo)

		# hh:mm
		elif len_time == 5:
			if fraction:
				seconds, microseconds = _solve_fractional_minutes(fraction)
			return dt.time(*map(int, time.split(":")), seconds, microseconds, tzinfo=tzinfo)

		else:
			raise ValueError("Invalid ISO-8601 format for time")

	# hhmmss
	elif len_time == 6:
		if fraction:
			microseconds = round(fraction * 1000000)
		return dt.time(*map(int, (time[:2], time[2:4], time[4:])), microseconds, tzinfo=tzinfo)

	# hhmm
	elif len_time == 4:
		if fraction:
			seconds, microseconds = _solve_fractional_minutes(fraction)
		return dt.time(*map(int, (time[:2], time[2:])), seconds, microseconds, tzinfo=tzinfo)

	# hh
	elif len_time == 2:
		if fraction:
			minutes, seconds, microseconds = _solve_fractional_hours(fraction)
		return dt.time(int(time), minutes, seconds, microseconds, tzinfo=tzinfo)

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
