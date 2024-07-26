"""
A simple validator to validates all values from db record from which the db_schedule is to be created
Created on 13-10-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import logging

from utils.date_util import get_utc_from_str
from utils.patterns import DB_TIME_PATTERN


class DBScheduleValidator:

    def __init__(self, db_record):
        self.db_record = db_record
        self.validated_data = {'name': None, 'state': None, 'timezone': None, 'weekdays': None, 'start': None,
                               'stop': None}

    def validate_weekdays(self):
        """
        Clean and validate given weekdays from db record
        """
        weekdays = self.db_record['working_days']
        return [int(x) for x in weekdays]

    def validate_start_time(self):
        """
        Assigns start time to the schedule instance it will be datetime object
        """
        try:
            start_time = self.db_record['utc_start_time']

            if start_time == "":
                return None

            db_start_match = DB_TIME_PATTERN.search(start_time)

            if db_start_match:
                return get_utc_from_str(db_start_match.group('datetime'))

            else:
                return False

        except Exception as err:
            logging.getLogger().exception(f"error occurred while setting the start time, '{err}'")

    def validate_stop_time(self):
        """
        Assigns stop time to the schedule instance it will be datetime object
        """
        try:
            stop_time = self.db_record['utc_stop_time']

            if stop_time == "":
                return None

            db_stop_match = DB_TIME_PATTERN.search(stop_time)

            if db_stop_match:
                return get_utc_from_str(db_stop_match.group('datetime'))

            else:
                return False

        except Exception as err:
            logging.getLogger().exception(f"error occurred while setting the stop time, '{err}'")

    def run(self):
        try:
            valid_data = self.validated_data
            valid_data['name'] = self.db_record['instance_name']
            valid_data['state'] = self.db_record['lifecycle_state']
            valid_data['timezone'] = self.db_record['working_timezone']
            valid_data['weekdays'] = self.validate_weekdays()
            valid_start = self.validate_start_time()
            valid_stop = self.validate_stop_time()

            if (valid_start is False) or (valid_stop is False):
                logging.getLogger().info("either start or stop time is invalid in db, cannot create schedule")
                return None

            valid_data['start'] = valid_start
            valid_data['stop'] = valid_stop

            return self.validated_data
        except Exception as err:
            logging.getLogger().exception(f"error occurred while validating db record '{err}'")
            return False
