"""
schedule tag values valid patterns. If schedule present in with below patterns only then instance can
be considered for automated scheduling
Created on 03-09-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import re

TAG_VALUE_PATTERNS = {

    1: re.compile(r'^((?P<start>\d+)?To(?P<stop>\d+)?)\|(?P<weekdays>\d+)\|(?P<timezone>[A-Za-z]+)$', re.IGNORECASE),

    # MANUAL START STOP BELOW
    # all NA
    2: re.compile(r'^(?P<timezone>(?P<weekdays>(?P<stop>(?P<start>Na))))$', re.IGNORECASE),

    # na|12345|UTC -- no start/stop cannot automate
    3: re.compile(r'^(?P<start>(?P<stop>Na))\|(?P<weekdays>\d+)\|(?P<timezone>[A-Za-z]+)$', re.IGNORECASE)

}

TIMEZONE_PATTERN = re.compile(r'^(?P<tz_abbr>[A-Za-z]{3})$')

WEEKDAYS_PATTERN = re.compile(r'(?P<weekdays>[1-7]+)')

HOUR_PATTERN = re.compile(r'^(?P<hour>0[0-9]|1[0-9]|2[0-3])$')

DB_TIME_PATTERN = re.compile(r'^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)$')
