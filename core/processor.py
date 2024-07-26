"""
A module to process database, instances, time related functionality. it will also create handler for oci function
Created on 01-09-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import sys
import datetime
import logging

import pytz

# local imports
from core.compute_instance import ComputeInstance
from core.schedule import Schedule
from core.oci_client import client
from validators import schedule_change_validator, tag_value_validator, db_schedule_validator


class Processor:
    """
    A central management wrapper for start/stop functionality
    """

    def __init__(self, configs):
        self._configs = configs
        self.client = client
        self.compartment_id = None
        self.table_name = None
        self.activate_auto_start_stop = None
        self.activate_auto_start = None
        self.minutes_delta = None
        self.valid_instances_queue = []
        self.started_instances = []
        self.stopped_instances = []
        self.processed_instances = []
        self.run_status = 'SUCCESS'
        self.enable_msg = {"message": "resource command scheduler is disabled, please enable it from configuration"}
        self.instance_processed = {'count': 0, 'instances': []}
        self.instance_started = {'count': 0, 'instances': []}
        self.instance_stopped = {'count': 0, 'instances': []}
        self.stats = {
            "message": "resource command scheduler executed",
            'status': self.run_status,
            "started_at": None,
            'execution_time': None,
        }

    def get_config(self, key):
        """
        Get required project config from env vars
        """
        return self._configs.get(key)

    def apply_configs(self, started_at):
        """
        Apply necessary configuration from OCI function configs
        """
        try:
            logging.getLogger().info("applying function configurations")

            kill_switch = self.get_config('ActivateAutoStartStopProcess').strip()
            auto_start_switch = self.get_config("ActivateAutoStart").strip()

            self.activate_auto_start_stop = True if kill_switch.casefold() == 'True'.casefold() else False
            self.activate_auto_start = True if auto_start_switch.casefold() == 'True'.casefold() else False
            self.compartment_id = self.get_config('CompartmentId').strip()
            self.table_name = self.get_config('TableName').strip()
            self.stats['started_at'] = started_at
            self.minutes_delta = int(self.get_config('MinutesDelta').strip())

        except Exception as err:
            logging.getLogger().exception(f"error occurred while applying configs '{err}'")
            logging.getLogger().info("terminating function execution")
            sys.exit(0)

    def get_records(self):
        """
        Queries the given database and returns list as a result set
        :return: list
        """
        # need to handle pagination if records are lot more
        try:
            logging.getLogger().info(f"fetching instance records from table '{self.table_name}'")
            query = "SELECT * FROM {}".format(self.table_name)
            response = client.query_database(compartment_id=self.compartment_id, query=query)
            if response:
                return response
            return None
        except Exception as err:
            logging.getLogger().exception(f"error occurred while fetching the records from the table '{err}'")
            self.run_status = 'FAILURE'

    def create_instances(self, record: dict):
        """
        create database and live instance objects, depending on the tag information creates schedule
        and attach to both the instances
        """
        try:
            # preparation
            instance_info = {'name': None, 'db_schedule': None, 'live_schedule': None}
            self.instance_processed['instances'].append(instance_info)
            # get live metadata
            instance_name, instance_id = record['instance_name'], record['instance_id']
            logging.getLogger().info(f"started processing instance '{instance_name}'")
            response = client.get_instance_metadata(instance_id)
            # get instance from db first
            compute_instance = ComputeInstance(
                schedule_tag=self.get_config('ScheduleTagKey'),
                name=instance_name,
                ocid=instance_id,
                oracle_tag=response['oracle_tags'],
                freeform_tags=response['freeform_tags']
            )
            # is it having schedule attached
            schedule_tag_value = compute_instance.get_tag_value()
            self.instance_processed['count'] += 1
            instance_info['name'] = compute_instance.name

            validator = tag_value_validator.TagValueValidator(tag_value=schedule_tag_value)
            validator.set_configs(self._configs)
            validated_data = validator.run()
            # create live schedule and bind
            schedule = Schedule(auto_start_state=self.activate_auto_start)
            live_schedule = schedule.update_schedule_from_tag(response['name'], response['state'], validated_data)
            compute_instance.set_live_schedule(live_schedule)

            if live_schedule:
                instance_info['live_schedule'] = str(live_schedule)
                # create db schedule and bind
                validated_data = db_schedule_validator.DBScheduleValidator(db_record=record).run()
                schedule = Schedule()
                db_schedule = schedule.update_schedule_from_db(validated_data)
                compute_instance.set_db_schedule(db_schedule)
                instance_info['db_schedule'] = str(db_schedule)
                return compute_instance
            return compute_instance

        except Exception as err:
            logging.getLogger().exception(f"error occurred while creating compute instance objects '{err}'")
            self.run_status = 'FAILURE'
            return False

    def pre_processing(self, db_record, past, now):
        """
        Creates instances and their schedules
        validated db instance and live instances and adds them to valid instance queue
        to be processed later
        """
        try:
            compute_instance = self.create_instances(db_record)

            if compute_instance is False:
                raise Exception(f"instance or schedule creation failed for '{db_record['instance_name']}'")

            db_schedule = compute_instance.get_db_schedule()
            live_schedule = compute_instance.get_live_schedule()

            if db_schedule and live_schedule:
                validator = schedule_change_validator.ScheduleChangeValidator(
                    db_schedule=db_schedule,
                    live_schedule=live_schedule,
                    past=past,
                    now=now,
                )
                validated_instance = validator.run(compute_instance)
                self.processed_instances.append(compute_instance.name)

                # instance has passed all the tests
                if validated_instance:
                    logging.getLogger().info("instance is valid to take action")
                    self.valid_instances_queue.append(validated_instance)
                else:
                    logging.getLogger().info("instance invalidated for taking action")
            else:
                logging.getLogger().info("instance do not have either live instance or db schedule, cannot validate")

        except Exception as err:
            logging.getLogger().exception(f"error occurred while preprocessing the instance '{err}'")
            self.run_status = 'FAILURE'

    def take_action(self, instance: ComputeInstance):
        """
        A method to take action on given instance based on its action attribute
        """
        try:
            logging.getLogger().info(f"started taking action on instance '{instance.name}'")

            if instance.get_action() == 'start':
                started_info = {'name': None, 'started_at': None}
                instance.start()
                self.instance_started['count'] += 1
                started_info['name'] = instance.name
                started_info['started_at'] = datetime.datetime.now(tz=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                self.instance_started['instances'].append(started_info)

            if instance.get_action() == 'stop':
                stopped_info = {'name': None, 'stopped_at': None}
                instance.stop()
                self.instance_stopped['count'] += 1
                stopped_info['name'] = instance.name
                stopped_info['stopped_at'] = datetime.datetime.now(tz=pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                self.instance_stopped['instances'].append(stopped_info)

        except Exception as err:
            logging.getLogger().exception(f"error occurred while taking action on instance '{err}'")
            self.run_status = 'FAILURE'
