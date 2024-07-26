"""
Module working as OCI API client. implemented all required apis for this project
Created on 06-09-2021
@author: Anurag Gundappa
@email: an.anurag@msn.com
"""

import logging

from oci.config import from_file
from oci.core import ComputeClient
from oci.nosql import NosqlClient, models
from oci.exceptions import ServiceError, RequestException


class OCIClient:

    def __init__(self):
        self.config = from_file('config')
        self.compute = ComputeClient(self.config)
        self.nosql_db = NosqlClient(self.config)

    def get_instance_metadata(self, instance_id) -> dict:
        """
        implements get_instance api from OCI sdk
        :return:
        """
        details = {}
        try:
            response = self.compute.get_instance(instance_id)
            if response.status == 200:
                details = {
                    'ocid': response.data.id,
                    'name': response.data.display_name,
                    'state': response.data.lifecycle_state,
                    'oracle_tags': response.data.defined_tags['Oracle-Tags'],
                    'freeform_tags': response.data.freeform_tags,
                }
                logging.getLogger().info(f"instance metadata retrieved for '{details['name']}'")
                return details
            logging.getLogger().error("instance metadata retrieval failed")
            return details
        except ServiceError as err:
            logging.getLogger().exception(f"error occurred while getting instance metadata, {err}")
            return details
        except RequestException as err:
            logging.getLogger().exception(f"error occurred while getting instance metadata, {err}")
            return details

    def set_instance_action(self, instance_id, action) -> dict:
        """
        implements instance_action api from oci sdk
        """
        details = {}
        try:
            response = self.compute.instance_action(instance_id, action)
            if response.status == 200:
                details = {
                    'ocid': response.data.id,
                    'display_name': response.data.display_name,
                    'lifecycle_state': response.data.lifecycle_state
                }
                logging.getLogger().info("instance action set successfully")
                return details
            logging.getLogger().error("unable to set instance action")
            return details
        except ServiceError as err:
            logging.getLogger().exception(f"error occurred while getting instance metadata, {err}")
            return details
        except RequestException as err:
            logging.getLogger().exception(f"error occurred while getting instance metadata, {err}")
            return details

    def query_database(self, compartment_id, query):
        """
        qeries the given database and returns list as a result set
        :return: list
        """
        try:
            response = self.nosql_db.query(query_details=models.QueryDetails(
                compartment_id=compartment_id,
                statement=query
            ))

            if response.status == 200:
                result = response.data

                while response.has_next_page:
                    response = self.nosql_db.query(query_details=models.QueryDetails(
                        compartment_id=compartment_id,
                        statement=query
                        ), page=response.next_page)
                    result.extend(response.data)

                result = result.items
                if result:
                    logging.getLogger().info("query returned result successfully")
                    return result
                logging.getLogger().error("query did not returned any result")
                return None
        except ServiceError as err:
            logging.getLogger().exception(f"error occurred while querying the database {err}")
            return None
        except RequestException as err:
            logging.getLogger().exception(f"error occurred while querying the database, {err}")
            return None


client = OCIClient()
