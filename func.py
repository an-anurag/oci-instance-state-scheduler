"""
Created on 01-09-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import io
import time
import json
import threading
import datetime

import pytz
from fdk import response

from core.processor import Processor
import logging


def handler(ctx=None, data: io.BytesIO = None):
    """
    main handler for oci function
    """
    start = time.monotonic()
    # check current execution utc time
    naive_now = datetime.datetime.utcnow()
    utc_now = naive_now.replace(tzinfo=pytz.utc)
    logging.getLogger().info("oci instance scheduler started at '{}'".format(utc_now))
    process = Processor(configs=dict(ctx.Config()))
    process.apply_configs(started_at=utc_now.strftime('%Y-%m-%dT%H:%M:%SZ'))

    if process.activate_auto_start_stop:

        try:
            logging.getLogger().info("pre-processing started")
            delta = datetime.timedelta(minutes=process.minutes_delta)
            rounded_utc_now = utc_now.replace(second=0, microsecond=0)
            past_utc = rounded_utc_now - delta

            records = process.get_records()
            if records:
                pre_processing_threads = []
                for record in records:
                    # fetch all data from table and validate all instances parallelly
                    worker = threading.Thread(target=process.pre_processing, args=(record, past_utc, rounded_utc_now))
                    worker.start()
                    pre_processing_threads.append(worker)

                for th in pre_processing_threads:
                    th.join()

                logging.getLogger().info("pre-processing completed")
            else:
                logging.getLogger().info("no instances to process at this moment")

            instance_queue = process.valid_instances_queue

            if instance_queue:
                # we have instance to start/stop
                logging.getLogger().info("found {} instances in the job queue to take action".format(len(instance_queue)))

                action_threads = []

                for instance in instance_queue:
                    worker = threading.Thread(target=process.take_action, args=(instance,))
                    worker.start()
                    action_threads.append(worker)

                for th in action_threads:
                    th.join()
            else:
                logging.getLogger().info("no instance to start/stop at this moment")

        except Exception as err:
            logging.getLogger().exception("error occurred in function execution with value '{}'".format(err))
            process.run_status = 'FAILURE'

        end = time.monotonic()
        duration = datetime.timedelta(seconds=end - start)
        logging.getLogger().info("oci instance scheduler finished in '{}'".format(duration))
        process.stats['execution_time'] = str(duration.seconds) + " " + "seconds"
        process.stats['instance_processed'] = process.instance_processed
        process.stats['instance_started'] = process.instance_started
        process.stats['instance_stopped'] = process.instance_stopped

        logging.getLogger().info(process.stats)
        return response.Response(
            ctx,
            response_data=json.dumps(process.stats),
            headers={"Content-Type": "application/json"}
        )
    else:
        logging.getLogger().info(process.enable_msg)
        return response.Response(
            ctx,
            response_data=json.dumps(process.enable_msg),
            headers={"Content-Type": "application/json"}
        )


if __name__ == '__main__':
    # driver function
    handler()
