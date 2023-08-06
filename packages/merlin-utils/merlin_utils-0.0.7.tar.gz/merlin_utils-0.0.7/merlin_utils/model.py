from . import ds_client
from google.cloud import datastore

class BaseModel():
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.key = kwargs.get("key", None)

    def save(self):
        if self.key is not None:
            entity = datastore.Entity(self.key)
            entity.update(self.__dict__)
            ds_client.put(entity)

    @staticmethod
    def get(id):
        """
        :param id: This method only works for websafe ids
        :return: Entity
        """
        return ds_client.get_client().get(datastore.Key.from_legacy_urlsafe(id))
