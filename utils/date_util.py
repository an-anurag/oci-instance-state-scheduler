"""
A datetime related utilities for this project
Created on 02-09-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import datetime
import collections

import pytz


TIMEZONES = {

    'IST': 'Asia/Kolkata',
    'PST': 'America/Los_Angeles',
    'CST': 'Asia/Shanghai',
    'UTC': 'UTC',
}


def get_utctime_from_hour(hour: int = None, timezone: str = None):
    """
    A function to convert given time in specified timezone to utc
    """
    local = pytz.timezone(timezone)
    # as reference point
    naive_now = datetime.datetime.now()
    # create local time wrt utc first
    local_time = naive_now.astimezone(local)
    # create datetime obj from given timezone and hour
    updated_local = local_time.replace(hour=hour, minute=0, second=0, microsecond=0)
    # convert local time to utc
    converted_utc = updated_local.astimezone(pytz.utc)
    return converted_utc


def get_timezone_from_abbreviation(abbr: str):
    """
    A function to get tz database value from given abbreviation
    abbr = timezone abbreviation IST, PST, etc
    """
    return TIMEZONES.get(abbr, None)


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def get_utc_from_str(utc_str):
    """
    Converts given utc date string into utc aware datetime
    """
    date = datetime.datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%SZ')
    utc_date = date.replace(tzinfo=pytz.utc)
    return utc_date


def get_timezones():
    """
    Get the dict of all timezones group by timezone abbreviation
    """
    tzones = collections.defaultdict(set)
    # abbrevs = collections.defaultdict(set)

    for name in pytz.all_timezones:
        tzone = pytz.timezone(name)
        data = getattr(tzone, '_transition_info', [[None, None, datetime.datetime.now(tzone).tzname()]])
        for utcoffset, dstoffset, tzabbrev in data:
            tzones[tzabbrev].add(name)
            # abbrevs[name].add(tzabbrev)
    return tzones
