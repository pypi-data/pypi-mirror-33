from google.cloud import datastore
import os
import uuid


class DatastoreEntity(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.key = kwargs.get("key", None)

    def save(self):
        if self.key is not None:
            entity = datastore.Entity(self.key)
            entity.update(self.__dict__)
            self.client.put(entity)


class DatastoreClient(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DatastoreClient, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        from google.cloud import datastore
        self.client = datastore.Client(os.environ.get("PROJECT"))

    def get_client(self):
        return self.client
