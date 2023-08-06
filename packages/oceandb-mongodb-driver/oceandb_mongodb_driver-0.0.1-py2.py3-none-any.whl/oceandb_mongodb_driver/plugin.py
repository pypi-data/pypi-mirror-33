"""Implementation of OceanDB plugin based in MongoDB"""
from oceandb_driver_interface.plugin import AbstractPlugin
from oceandb_mongodb_driver.instance import get_database_instance


class Plugin(AbstractPlugin):
    """Mongo ledger plugin for `Ocean DB's Python reference
    implementation <https://github.com/oceanprotocol/oceandb-mongo-driver>`_.
    Plugs in a MongoDB instance as the persistence layer for Ocean Db
    related actions.
    """

    def __init__(self, config):
        """Initialize a :class:`~.Plugin` instance and connect to MongoDB.
        Args:
            *nodes (str): One or more URLs of MongoDB nodes to
                connect to as the persistence layer
        """
        self.driver = get_database_instance(config)

    @property
    def type(self):
        """str: the type of this plugin (``'MongoDB'``)"""
        return 'MongoDB'

    def write(self, obj):
        o = self.driver.instance.insert_one(obj)
        print('mongo::write::{}'.format(o.inserted_id))
        return o.inserted_id

    def read(self, id):
        return self.driver.instance.find_one({"_id": id})

    def update(self, id, obj):
        prev = self.read(id)
        print('mongo::update::{}'.format(id))
        return self.driver.instance.replace_one(prev, obj)

    def delete(self, id):
        print('mongo::delete::{}'.format(id))
        return self.driver.instance.delete_one({"_id": id})

    def list(self, search_from=None, search_to=None, offset=None, limit=None):
        return self.driver.instance.find()

    def query(self, query_string):
        return self.driver.instance.find(query_string)
