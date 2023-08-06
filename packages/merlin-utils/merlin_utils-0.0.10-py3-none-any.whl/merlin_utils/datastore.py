from google.cloud import datastore
import os


class DatastoreClient:
    class __DatastoreClient:
        def __init__(self):
            self.client = datastore.Client(os.environ.get("PROJECT"))

    instance = None

    def __init__(self):
        if not DatastoreClient.instance:
            DatastoreClient.instance = DatastoreClient.__DatastoreClient()

    def get_client(self):
        return self.client

    def __getattr__(self, name):
        return getattr(self.instance, name)
