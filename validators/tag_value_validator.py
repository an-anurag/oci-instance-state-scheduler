"""
Tag value validator to create schedule
Created on 13-10-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import datetime
import logging
from typing import Any

from utils.date_util import get_timezones, get_timezone_from_abbreviation, get_utctime_from_hour
from utils.patterns import HOUR_PATTERN, WEEKDAYS_PATTERN, TIMEZONE_PATTERN, TAG_VALUE_PATTERNS


class TagValueValidator:
    """
    Validates given tag value against predefined regex patterns
    """

    _CONFIGS = None
    _TAG_UNDEFINED = 'TAG_UNDEFINED'
    _TAG_DEFINED_WITH_NO_VALUE = "TAG_DEFINED_WITH_NO_VALUE"
    _TAG_DEFINED_WITH_VALID_VALUE = "TAG_DEFINED_WITH_VALID_VALUE"
    _TAG_DEFINED_WITH_INVALID_VALUE = "TAG_DEFINED_WITH_INVALID_VALUE"
    _TAG_DEFINED_WITH_NO_AUTOMATION = "TAG_DEFINED_WITH_NO_AUTOMATION"

    def __init__(self, tag_value: Any):
        # clean it first
        self._tag_value = tag_value.strip() if tag_value else tag_value
        self.na = 'Na'.casefold()
        self.schedule = {'start': None, 'stop': None, 'weekdays': None, 'timezone': None}
        self._validated_data = {'tag_value': self._tag_value, 'validation_state': None, 'schedule': self.schedule}

    def update_validated_data(self, state):
        """
        update validated data dictionary with validation state
        """
        self._validated_data['validation_state'] = state

    @staticmethod
    def is_tz_abbreviation_valid(tz_abbr) -> bool:
        """
        checks whether given tz abbreviation is correct or not
        """
        return bool(get_timezones()[tz_abbr])

    def set_configs(self, defaults: dict):
        """
        set default schedule env vars values as class attribute
        """
        self._CONFIGS = defaults

    def get_configs(self, key):
        """
        Get default schedule by key
        """
        return self._CONFIGS.get(key)

    def get_default_timezone(self):
        """
        Returns default timezone value set in the function configurations
        """
        default_tz = self.get_configs('DefaultTimezone')

        if not default_tz:
            logging.getLogger().info("default timezone is not set")
            return None

        if default_tz.casefold() == self.na:
            logging.getLogger().info("default timezone set to 'NA'")
            return None

        return get_timezone_from_abbreviation(abbr=default_tz)

    def validate_timezone(self, tz_abbreviation):
        """
        Assign the timezone to the schedule instance
        """

        try:
            if not tz_abbreviation:
                logging.getLogger().info("timezone is not provided in the tag, invalidating tag value")
                return False

            if tz_abbreviation.casefold() == self.na:
                return None

            # clean it first
            tz_abbreviation_upper = tz_abbreviation.upper()
            timezone_match = TIMEZONE_PATTERN.search(tz_abbreviation_upper)

            if timezone_match:
                matched_abbr = timezone_match.group('tz_abbr')
                if self.is_tz_abbreviation_valid(matched_abbr):
                    mapped_tz = get_timezone_from_abbreviation(abbr=matched_abbr)
                    if mapped_tz:
                        return mapped_tz
                    else:
                        logging.getLogger().info("invalid timezone provided, invalidating tag value")
                        return False
                else:
                    logging.getLogger().info("invalid timezone provided, invalidating tag value")
                    return False

            else:
                logging.getLogger().info("invalid timezone provided, invalidating tag value")
                return False

        except Exception as err:
            logging.getLogger().exception(f"error occurred while setting the timezone, '{err}'")

    def get_default_weekdays(self):
        """
        Returns default weekdays value set in the function configurations
        """
        default_weekdays = self.get_configs('DefaultWeekdays')

        if not default_weekdays:
            logging.getLogger().info("default weekdays are not set")
            return None

        if default_weekdays.casefold() == self.na:
            logging.getLogger().info("default weekdays are set to 'NA'")
            return None

        return [int(x) for x in default_weekdays]

    def validate_weekdays(self, weekdays):
        """
        Assigns weekdays to the schedule instance
        ex = 12345
        """
        try:
            if not weekdays:
                logging.getLogger().info("weekdays is not provided in the tag, invalidating tag value")
                return False

            if weekdays.casefold() == self.na:
                return None

            match = WEEKDAYS_PATTERN.findall(weekdays)
            if match:
                result = []
                for ch in "".join(match):
                    if ch not in result:
                        result.append(int(ch))
                return result

            else:
                logging.getLogger().info("invalid weekdays provided, invalidating tag value")
                return False

        except Exception as err:
            logging.getLogger().exception(f"error occurred while setting the weekdays, '{err}'")

    def get_default_start_time(self, default_tz):
        """
        Returns default start time value set in the function configurations
        """
        default_start = self.get_configs('DefaultStart')

        if not default_start:
            logging.getLogger().info("default start time is not set")
            return None

        if default_start.casefold() == self.na:
            logging.getLogger().info("default start time set to 'NA'")
            return None

        return get_utctime_from_hour(int(default_start), timezone=default_tz)

    def validate_start_time(self, start_time, timezone):
        """
        Assigns start time to the schedule instance it will be datetime object
        """
        try:
            if start_time is None:
                return None

            if start_time.casefold() == self.na:
                return None

            # apply provided start time
            live_start_match = HOUR_PATTERN.search(start_time)

            if live_start_match:
                return get_utctime_from_hour(int(live_start_match.group('hour')), timezone=timezone)

            else:
                logging.getLogger().info("invalid start time provided, invalidating tag value")
                return False

        except Exception as err:
            logging.getLogger().exception(f"error occurred while setting the start time, '{err}'")

    def get_default_stop_time(self, default_tz):
        """
        Returns default stop time value set in the function configurations
        """
        default_stop = self.get_configs('DefaultStop')

        if not default_stop:
            logging.getLogger().info("default stop time is not set")
            return None

        if default_stop.casefold() == self.na:
            logging.getLogger().info("default stop time set to 'NA'")
            return None

        return get_utctime_from_hour(int(default_stop), timezone=default_tz)

    def validate_stop_time(self, stop_time, timezone):
        """
        Assigns stop time to the schedule instance it will be datetime object
        """
        try:
            if stop_time is None:
                return None

            if stop_time.casefold() == self.na:
                return None

            # apply provided stop time, not provided means user dont want to stop it
            live_stop_match = HOUR_PATTERN.search(stop_time)

            if live_stop_match:
                return get_utctime_from_hour(int(live_stop_match.group('hour')), timezone=timezone)

            else:
                logging.getLogger().info("invalid stop time provided, invalidating tag value")
                return False

        except Exception as err:
            logging.getLogger().exception(f"error occurred while setting the stop time, '{err}'")

    def validate(self):
        """
        Checks the given tag value against all possible combinations
        returns dictionary of parsed schedule data
        """
        # does tag value has valid schedule attached
        for pattern in TAG_VALUE_PATTERNS.values():
            match = pattern.search(self._tag_value)
            if match:
                return match.groupdict()
        return False

    def create_schedule_from_default_values(self):
        """
        Create the default schedule
        """
        try:
            logging.getLogger().info("creating schedule from default values")
            timezone = self.get_default_timezone()
            if timezone is None:
                logging.getLogger().info("default timezone is not defined, cannot create default schedule")
                return False

            weekdays = self.get_default_weekdays()
            if weekdays is None:
                logging.getLogger().info("default weekdays is not defined, cannot create default schedule")
                return False

            start = self.get_default_start_time(default_tz=timezone)
            stop = self.get_default_stop_time(default_tz=timezone)

            if start is None and stop is None:
                logging.getLogger().info("default start and stop both are not defined, cannot create default schedule")
                return False

            self.schedule['timezone'] = timezone
            self.schedule['weekdays'] = weekdays
            self.schedule['start'] = start
            self.schedule['stop'] = stop

            logging.getLogger().info("default schedule created")
            return self._validated_data

        except Exception as err:
            logging.getLogger().exception(f"error creating schedule from default values '{err}'")
            return False

    def create_schedule_from_provided_values(self, schedule_dict):
        """
        Create schedule from user provided values
        """

        try:
            validated_timezone = self.validate_timezone(tz_abbreviation=schedule_dict['timezone'])
            if validated_timezone is False:
                self.update_validated_data(self._TAG_DEFINED_WITH_INVALID_VALUE)
                return self.create_schedule_from_default_values()

            validated_weekdays = self.validate_weekdays(weekdays=schedule_dict['weekdays'])
            if validated_weekdays is False:
                self.update_validated_data(self._TAG_DEFINED_WITH_INVALID_VALUE)
                return self.create_schedule_from_default_values()

            validated_start = self.validate_start_time(start_time=schedule_dict['start'], timezone=validated_timezone)
            if validated_start is False:
                self.update_validated_data(self._TAG_DEFINED_WITH_INVALID_VALUE)
                return self.create_schedule_from_default_values()

            validated_stop = self.validate_stop_time(stop_time=schedule_dict['stop'], timezone=validated_timezone)
            if validated_stop is False:
                self.update_validated_data(self._TAG_DEFINED_WITH_INVALID_VALUE)
                return self.create_schedule_from_default_values()

            # create schedule
            self.schedule['timezone'] = validated_timezone
            self.schedule['weekdays'] = validated_weekdays
            self.schedule['start'] = validated_start
            self.schedule['stop'] = validated_stop

            # check few things after validation
            if (validated_timezone is None) and (validated_weekdays is None):
                logging.getLogger().info("schedule is created from provided values but instance cannot be automated")
                self.update_validated_data(self._TAG_DEFINED_WITH_NO_AUTOMATION)
                return self._validated_data

            if (validated_start is None) and (validated_stop is None):
                logging.getLogger().info("schedule is created from provided values but instance cannot be automated")
                self.update_validated_data(self._TAG_DEFINED_WITH_NO_AUTOMATION)
                return self._validated_data

            if validated_start == validated_stop:
                logging.getLogger().info("start time and stop time cannot be equal, falling back to default schedule")
                self.update_validated_data(self._TAG_DEFINED_WITH_INVALID_VALUE)
                return self.create_schedule_from_default_values()

            logging.getLogger().info("schedule is created from provided values successfully")
            self.update_validated_data(self._TAG_DEFINED_WITH_VALID_VALUE)
            return self._validated_data

        except Exception as err:
            logging.exception(f"error creating schedule from provided values '{err}'")
            return False

    def run(self):
        """
        Main driver code for this class
        """
        try:
            if self._tag_value is None:
                logging.getLogger().info("schedule tag is not present, applying tag with default value")
                self.update_validated_data(self._TAG_UNDEFINED)
                return self.create_schedule_from_default_values()

            if self._tag_value == "":
                logging.getLogger().info("schedule tag is present with no value, applying default value")
                self.update_validated_data(self._TAG_DEFINED_WITH_NO_VALUE)
                return self.create_schedule_from_default_values()

            result = self.validate()

            if isinstance(result, dict):
                logging.getLogger().info("schedule tag is present with user defined value, checking provided value")
                return self.create_schedule_from_provided_values(schedule_dict=result)

            if result is False:
                logging.getLogger().info("schedule tag is present with invalid value, applying default value")
                self.update_validated_data(self._TAG_DEFINED_WITH_INVALID_VALUE)
                return self.create_schedule_from_default_values()

        except Exception as err:
            logging.getLogger().exception(f"error validating schedule tag value '{err}'")
            return self._validated_data

    @staticmethod
    def normalize(schedule_dict):
        """
        Normalize the schedule to be used for db insertion
        this assumes schedule_dict in form -
        {'start': None,
        'stop': datetime.datetime(2021, 10, 14, 18, 0, tzinfo=<UTC>),
        'weekdays': [1, 2, 3, 4, 5],
        'timezone': 'UTC'}}
        """
        try:
            output = {}
            start = schedule_dict['start']
            stop = schedule_dict['stop']
            weekdays = schedule_dict['weekdays']
            timezone = schedule_dict['timezone']

            if start is None:
                output['start'] = ''
            else:
                output['start'] = start.strftime('%Y-%m-%dT%H:%M:%SZ')

            if stop is None:
                output['stop'] = ''
            else:
                output['stop'] = stop.strftime('%Y-%m-%dT%H:%M:%SZ')

            output['weekdays'] = "".join([str(x) for x in weekdays])
            output['timezone'] = timezone

            return output
        except Exception as err:
            logging.getLogger().exception(f"error occurred while normalizing the schedule '{err}'")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    from local_settings import ENV_VARS
    tag_value = None
    validator = TagValueValidator(tag_value)
    validator.set_configs(ENV_VARS)
    d = validator.run()
    print(d)
    print(validator.normalize(d['schedule']))
