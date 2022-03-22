"""Series of functions to extract and/or convert metadata field values to the right SQL type"""

import datetime
import regex as re

INTEGER = re.compile(r"(\d{1,})")  # we are assuming positive years
YEAR_MONTH_DAY = re.compile(r"(\d+)-(\d+)-(\d+)")
YEAR_MONTH = re.compile(r"^(\d+)-(\d+)\Z")
YEAR = re.compile(r"^(\d+)\Z")
MONTH_MAX_DAY = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def day_fail_safe(day, month=None):
    """Make sure we have a valid day"""
    if month is not None and month != 0:
        if day > MONTH_MAX_DAY[month]:
            day = 1
    if day > 31 or day <= 0:
        day = 1
    return day


def month_fail_safe(month):
    """Make sure we have a valid month"""
    if month > 12 or month < 1:
        month = 1
    return month


def extract_full_date(date):
    """Extract full dates and format as year-month-day"""
    full_date_match = re.search(r"^(\d+)-(\d+)-(\d+)", date)
    if full_date_match:  # e.g. 1987-10-23
        year, month, day = map(int, full_date_match.groups())
        month = month_fail_safe(month)
        day = day_fail_safe(day, month)
        return datetime.date(year, month, day)
    month_year_match = re.search(r"^(\d+)-(\d+)$", date)
    if month_year_match:  # e.g. 1987-10
        year, month = map(int, month_year_match.groups())
        month = month_fail_safe(month)
        return datetime.date(year, month, 1)
    year_match = re.search(r"^(\d+)$", date)
    if year_match:  # e.g. 1987
        year_str = year_match.groups()[0]
        if len(year_str) > 4:
            year_str = year_str[:4]
        year = int(year_str)
        return datetime.date(year, 1, 1)
    return datetime.date(9999, 12, 31)


def extract_integer(field_value):
    """Extract integer from field value and return a Python int"""
    integer = INTEGER.search(field_value)
    if integer is not None:
        return int(integer.group())
    else:
        return None
