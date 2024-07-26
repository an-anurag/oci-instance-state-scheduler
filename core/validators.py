"""
Global validators for this project
Created on 18-09-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import re
import datetime
import logging

import pytz

from utils.date_util import time_in_range
from utils.patterns import TAG_VALUE_PATTERNS


class ScheduleValidator:
    """
    Universal validator wrapper for this project
    """

    def __init__(self, db_schedule=None, live_schedule=None, past=None, now=None):
        """
        Initialization
        """
        self.db_schedule = db_schedule
        self.live_schedule = live_schedule
        self.past = past
        self.now = now

    def is_start_valid(self):
        """
        Compares db start time and live start time and validated there difference
        based on certain conditions
        """
        db_start = self.db_schedule.get_start_time()
        live_start = self.live_schedule.get_start_time()

        if db_start and live_start:
            logging.getLogger().info(f"validating db start time '{db_start}' and live start time '{live_start}'")
            # both present but live start may be updated
            if db_start == live_start:
                logging.getLogger().info("no change in start time, checking the time range")
                # no change
                # check range
                is_okay = time_in_range(self.past, self.now, live_start)
                if is_okay:
                    return True
                logging.getLogger().info("start time mismatched with time range")
                return False
            else:
                logging.getLogger().info(f"start time has changed to '{live_start}', checking the time range")
                # change found, check range in live
                is_okay = time_in_range(self.past, self.now, live_start)
                if is_okay:
                    return True
                logging.getLogger().info("start time mismatched with time range")
                return False

        if not db_start and not live_start:
            logging.getLogger().info("no start time present cannot perform start")
            return False

        if db_start and not live_start:
            logging.getLogger().info("start time has been removed, cannot perform start")
            return False

        if not db_start and live_start:
            logging.getLogger().info("start time added recently")
            # check the range
            is_okay = time_in_range(self.past, self.now, live_start)
            if is_okay:
                return True
            logging.getLogger().info("start time mismatched with time range")
            return False

    def is_stop_valid(self):
        """
        Compares db stop time and live stop time and validated there difference
        based on certain conditions
        """
        db_stop = self.db_schedule.get_stop_time()
        live_stop = self.live_schedule.get_stop_time()

        if db_stop and live_stop:
            logging.getLogger().info(f"validating db stop time '{db_stop}' and live stop time '{live_stop}'")
            # both present but live start might be updated
            if db_stop == live_stop:
                logging.getLogger().info("no change in stop time, checking the time range")
                # no change
                # check range
                is_okay = time_in_range(self.past, self.now, live_stop)
                if is_okay:
                    return True
                logging.getLogger().info("stop time mismatched with time range")
                return False
            else:
                logging.getLogger().info(f"stop time has changed to '{live_stop}', checking the time range")
                # change found
                # check range in live
                is_okay = time_in_range(self.past, self.now, live_stop)
                if is_okay:
                    return True
                logging.getLogger().info("stop time mismatched with time range")
                return False

        if not (db_stop and live_stop):
            logging.getLogger().info("no stop time present cannot perform stop")
            return False

        if db_stop and not live_stop:
            logging.getLogger().info("stop time has been removed, cannot perform stop")
            return False

        if not db_stop and live_stop:
            logging.getLogger().info("stop time added recently")
            # check the range
            is_okay = time_in_range(self.past, self.now, live_stop)
            if is_okay:
                return True
            logging.getLogger().info("stop time mismatched with time range")
            return False

    def is_state_valid_for_start(self):
        """
        checks instance lifecycle state is valid for starting the instance
        returns: bool
        """
        db_state = self.db_schedule.get_state()
        live_state = self.live_schedule.get_state()

        if (live_state == 'TERMINATING') or (live_state == 'TERMINATED'):
            logging.getLogger().info("instance is terminated cannot take action")
            return False

        if (db_state == 'STOPPED' or db_state == 'RUNNING') and (live_state == 'RUNNING'):
            logging.getLogger().info("instance is already running cannot start it")
            return False

        if (db_state == 'STOPPED') and (live_state == 'STOPPED'):
            logging.getLogger().info("instance is stopped start action will be applied")
            return True

    def is_state_valid_for_stop(self):
        """
        checks instance lifecycle state is valid for starting the instance
        returns: bool
        """
        db_state = self.db_schedule.get_state()
        live_state = self.live_schedule.get_state()

        if (live_state == 'TERMINATING') or (live_state == 'TERMINATED'):
            logging.getLogger().info("instance is terminated cannot take action")
            return False

        if (db_state == 'RUNNING' or db_state == 'STOPPED') and (live_state == 'STOPPED'):
            logging.getLogger().info("instance is already stopped cannot be stopped")
            return False

        if (db_state == 'RUNNING') and (live_state == 'RUNNING'):
            logging.getLogger().info("instance is running, stop action will be applied")
            return True

    def is_weekdays_valid(self):
        """
        validate today by comparing db weekdays and live weekdays
        """
        # check if schedule weekday matches current weekday
        live_timezone = self.live_schedule.get_timezone()
        today = datetime.datetime.now(tz=pytz.timezone(live_timezone)).weekday() + 1
        db_weekdays = [int(x) for x in self.db_schedule.get_weekdays()]
        live_weekdays = [int(x) for x in self.live_schedule.get_weekdays()]

        if (today not in db_weekdays) and (today not in live_weekdays):
            # today is not anywhere
            logging.getLogger().info("today is not present in schedule")
            return False

        if (today in db_weekdays) and (today in live_weekdays):
            # today in db
            logging.getLogger().info("today is present in schedule")
            return True

        if (today not in db_weekdays) and (today in live_weekdays):
            # today is not in db but added in live
            logging.getLogger().info("today is recently added in schedule")
            return True

        if (today in db_weekdays) and (today not in live_weekdays):
            # today is in db but removed from live
            logging.getLogger().info("today is removed from the schedule")
            return False

    def run(self, db_instance):
        """"
        driver code for schedule validator. if db schedule validates against live schedule
        then instance will be eligible for taking action
        """
        logging.getLogger().info(f"validation started for instance '{self.db_schedule.instance_name}'")
        logging.getLogger().info(f"current time window is '{self.now}' to '{self.past}'")

        # if state is okay then check today is the day to be started or stopped
        if not self.is_weekdays_valid():
            logging.getLogger().info("instance scheduled weekday invalid")
            return False
        logging.getLogger().info("weekdays validated successfully")

        start_okay = self.is_start_valid()
        stop_okay = self.is_stop_valid()

        if (not start_okay) and (not stop_okay):
            logging.getLogger().info("action cannot be taken on this instance")
            return False

        if start_okay:
            logging.getLogger().info("start time validated successfully")

            if self.is_state_valid_for_start():
                logging.getLogger().info("instance state is validated successfully")
                db_instance.set_action('start')
                logging.getLogger().info("instance marked for starting")
                return db_instance
            logging.getLogger().info("instance state is invalid cannot take action")
            return False

        if stop_okay:
            logging.getLogger().info("stop time validated successfully")

            if self.is_state_valid_for_stop():
                logging.getLogger().info("instance state is validated successfully")
                db_instance.set_action('stop')
                logging.getLogger().info("instance marked for stopping")
                return db_instance
            logging.getLogger().info("instance state is invalid cannot take action")
            return False


class TagValueValidator:
    """
    Validates given tag value against predefined regex patterns
    """

    def __init__(self, tag_value=None):
        self.tag_value = tag_value
        self.tag_value_pattern = TAG_VALUE_PATTERNS

    def validate(self):
        """
        Checks the given tag value against all possible combinations
        returns dictionary of parsed schedule data
        """

        if not self.tag_value:
            return None

        # check 1 does tag value has valid schedule attached
        for pattern in self.tag_value_pattern.values():
            match = re.search(pattern, self.tag_value)
            if match:
                return match.groupdict()
        return None
