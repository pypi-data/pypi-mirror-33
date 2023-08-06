"""The client for the Heap Api."""
import json

import requests


class HeapAPIClient(object):
    """
    The client for the Heap Api.
    """
    base_url = "https://heapanalytics.com/api"
    headers = {'Content-Type': 'application/json'}

    def __init__(self, app_id):
        """
        Initialize the client.

        :param app_id: Heap analytics app_id
        :type app_id: str
        """
        assert app_id, 'app_id must be valid!'
        self.app_id = str(app_id)

    def track(self, identity, event, properties=None):
        """
        Send a "track" event to the Heap Analytics API server.

        :param identity: user identity
        :type identity: str
        :param event: event name
        :type event: str
        :param properties: optional, additional event properties
        :type properties: dict
        """
        data = {
            "app_id": self.app_id,
            "identity": identity,
            "event": event
        }

        if properties is not None:
            data["properties"] = properties

        response = requests.post(
            self.base_url + '/track',
            data=json.dumps(data),
            headers=self.headers
        )
        response.raise_for_status()
        return response

    def add_user_properties(self, identity, properties):
        """
        Post a "add_user_properties" event to the Heap Analytics API server.

        :param identity: user identity
        :type identity: str
        :param properties: additional properties to associate with the user
        :type properties: dict
        """
        data = {
            "app_id": self.app_id,
            "identity": identity,
            "properties": properties,
        }

        response = requests.post(
            self.base_url + '/add_user_properties',
            data=json.dumps(data),
            headers=self.headers
        )
        response.raise_for_status()
        return response
