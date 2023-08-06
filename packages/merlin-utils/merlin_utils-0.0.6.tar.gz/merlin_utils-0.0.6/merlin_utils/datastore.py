from google.cloud import datastore
import os
import uuid


class DatastoreEntity(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.key = kwargs.get("key", None)
        self.client = datastore.Client(os.environ.get("PROJECT"))

    def save(self):
        if self.key is not None:
            entity = datastore.Entity(self.key)
            entity.update(self.__dict__)
            self.client.put(entity)
