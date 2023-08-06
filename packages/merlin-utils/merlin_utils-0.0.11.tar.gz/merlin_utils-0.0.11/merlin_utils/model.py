from . import ds_client
from google.cloud import datastore
from google.cloud.datastore import Entity


class BaseModel():
    def __init__(self, **kwargs):
        self.kind = kwargs.get("kind", None)
        self.id = kwargs.get("id", None)
        self.key = kwargs.get("key", None)
        self.parent = kwargs.get("parent", None)

    def save(self):
        if self.key is not None:
            entity = datastore.Entity(self.key)
            entity.update(self.__dict__)
            ds_client.get_client().put(entity)

    @staticmethod
    def get(id):
        """
        :param id: This method only works for websafe ids
        :return: Entity
        """
        return ds_client.get_client().get(datastore.Key.from_legacy_urlsafe(id))

    def to_entity(self):
        if self.key is None:
            self.key = ds_client.get_client().key(self.kind, self.id) if self.parent is None else ds_client.get_client() \
                .key(self.parent[0], self.parent[1], self.kind, self.id)
        entity = Entity(self.key)
        entity.update(self.__dict__)
        return entity
