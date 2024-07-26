"""
Schedule instance representating compute instance schedule tag
Created on 06-09-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import logging


class Schedule:

    def __init__(self, auto_start_state=None):
        """
        Initialization
        """
        self.activate_auto_start = auto_start_state
        self._instance_name = None
        self._life_state = None
        self._start_time = None
        self._stop_time = None
        self._weekdays = None
        self._timezone = None

    def __repr__(self):
        """
        Object representation
        """
        return "{} To {} | {} | {}".format(self._start_time, self._stop_time, self._weekdays, self._timezone)

    def get_instance_name(self):
        """
        Getter for instance name
        """
        return self._instance_name

    def set_instance_name(self, instance_name):
        """
        setter for instance name
        """
        self._instance_name = instance_name

    def get_state(self):
        """
        getter for instance lifecycle state
        """
        return self._life_state

    def set_state(self, state):
        """
        setter for instance lifecycle state
        """
        self._life_state = state

    def get_timezone(self):
        """
        getter for schedule timezone
        """
        return self._timezone

    def set_timezone(self, timezone):
        """
        setter for schedule timezone
        """
        self._timezone = timezone

    def get_weekdays(self):
        """
        getter for weekdays in digit form
        """
        return self._weekdays

    def set_weekdays(self, weekdays):
        """
        setter for weekdays in digit form
        """
        self._weekdays = weekdays

    def get_start_time(self):
        """
        getter for start time in datetime object form
        """
        return self._start_time

    def set_start_time(self, start_time):
        """
        setter for start time in datetime object form
        """
        self._start_time = start_time

    def get_stop_time(self):
        """
        getter for stop time in datetime object form
        """
        return self._stop_time

    def set_stop_time(self, stop_time):
        """
        setter for stop time in datetime object form
        """
        self._stop_time = stop_time

    def update_schedule_from_tag(self, name, state, validated_data: dict):
        """
        populates instance vars from schedule tag value
        eg - 08To18|12345|IST
        """
        try:
            if validated_data:
                self.set_instance_name(name)
                self.set_state(state)
                self.set_timezone(validated_data['schedule']['timezone'])
                self.set_weekdays(validated_data['schedule']['weekdays'])
                # turn off auto starting of the instance if the configs say so
                logging.getLogger().info("applying auto start configuration")
                start_time = validated_data['schedule']['start'] if self.activate_auto_start else None
                self.set_start_time(start_time)

                self.set_stop_time(validated_data['schedule']['stop'])
                logging.getLogger().info(f"schedule created from tag successfully with value '{self}'")
                return self
            return None

        except Exception as err:
            logging.getLogger().info(f"error creating schedule from tag, '{err}'")
            return None

    def update_schedule_from_db(self, validated_data):
        """
        Populates Schedule instance vars from db records
        """
        try:
            if validated_data:
                self.set_instance_name(validated_data['name'])
                self.set_state(validated_data['state'])
                self.set_timezone(validated_data['timezone'])
                self.set_weekdays(validated_data['weekdays'])
                self.set_start_time(validated_data['start'])
                self.set_stop_time(validated_data['stop'])
                logging.getLogger().info(f"schedule created from database successfully with value '{self}'")
                return self
            return None

        except Exception as err:
            logging.getLogger().exception(f"error creating schedule from database, '{err}'")
            return None
