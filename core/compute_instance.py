"""
A module to manage given oci compute instance identified by ocid
Created on 01-09-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

# local imports
import logging

from core.oci_client import client


class ComputeInstance:
    """
    A management wrapper for given OCI compute instance
    """

    def __init__(self, **kwargs):
        """ Initialization """
        self._schedule_tag = kwargs['schedule_tag']
        self.ocid = kwargs['ocid']
        self.name = kwargs['name']
        self.oracle_tag = kwargs['oracle_tag']
        self.freeform_tags = kwargs['freeform_tags']

        self._action = None
        # two schedule
        self._db_schedule = None
        self._live_schedule = None

    def __repr__(self):
        """
        Object representation
        """
        return self.name

    def get_action(self):
        """
        Getter for instance to be applied lifecycle state
        """
        return self._action

    def set_action(self, action):
        """
        Set the start or stop action for this instance
        """
        self._action = action

    def set_db_schedule(self, schedule_obj):
        """
        Attach schedule instance to the vm instance
        """
        self._db_schedule = schedule_obj

    def get_db_schedule(self):
        """
        Getter for db schedule
        """
        return self._db_schedule

    def set_live_schedule(self, schedule_obj):
        """
        Attach schedule instance to the vm instance
        """
        self._live_schedule = schedule_obj

    def get_live_schedule(self):
        """
        Getter for live schedule
        """
        return self._live_schedule

    def get_tag_value(self):
        try:
            logging.getLogger().info("looking for schedule tag on instance")

            if self._schedule_tag in self.freeform_tags:
                logging.getLogger().info("schedule tag found in freeform tags")
                return self.freeform_tags.get(self._schedule_tag)

            elif self._schedule_tag in self.oracle_tag:
                logging.getLogger().info("schedule tag found in oracle tags")
                return self.oracle_tag.get(self._schedule_tag)

            else:
                return None

        except Exception as err:
            logging.getLogger().exception(f"something went wrong while getting tag from the instance, {err}")

    def start(self) -> dict:
        """
        Start the given compute instance identified by ocid
        :return:
        """
        response = {}
        try:
            response = client.set_instance_action(self.ocid, 'START')
            if response:
                logging.getLogger().info("instance started successfully")
                return response
            logging.getLogger().error("something went wrong while starting the instance")
            return response
        except Exception as err:
            logging.getLogger().error(f"something went wrong while starting the instance, {err}")
            return response

    def stop(self) -> dict:
        """
        Stop the given compute instance identified by ocid
        :return:
        """
        response = {}
        try:
            response = client.set_instance_action(self.ocid, 'STOP')
            if response:
                logging.getLogger().info("instance stopped successfully")
                return response
            logging.getLogger().error("something went wrong while stopping the instance")
            return response
        except Exception as err:
            logging.getLogger().error(f"something went wrong while starting the instance, {err}")
            return response
