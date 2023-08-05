import bson
import pymongo

class mongodb():
    def __init__(self, config):
        client = pymongo.MongoClient(config['addr'], config['port'])
        self.handler = client[config['db']]

        # Define default collection
        if config.has_key('collection'):
            self.default_collection = config['collection']
        else:
            self.default_collection = 'default'

        if config.has_key('primary_keys'):
            for key in config['primary_keys']:
                self.set_primary_key(key)


    def load_default_collection(self, collection):
        if collection == None:
            collection = self.default_collection
        return collection


    def set_primary_key(self, key, collection=None):
        # load default collection when collection isn't declared
        collection = self.load_default_collection(collection)

    	# Creamos las collecciones en el caso de que aun no existan
    	collections = self.handler.collection_names()
    	if not(collection in collections):
            self.handler.create_collection(collection)
        self.handler[collection].create_index(key, unique=True)


    def create(self, data, collection=None):
        # load default collection when collection isn't declared
        collection = self.load_default_collection(collection)
        r = self.handler[collection].insert_one(data)
        if r.acknowledged:
            return r.inserted_id
        else:
            return None

    def load(self, filt={}, collection=None):
        # load default collection when collection isn't declared
        collection = self.load_default_collection(collection)

        result = []
        for doc in self.handler[collection].find(filt):
            del doc['_id']
            result.append(doc)
        return result

    def update(self, filt, data, collection=None, upsert=False):
        # load default collection when collection isn't declared
        collection = self.load_default_collection(collection)

        return self.handler[collection].replace_one(filt, data, upsert=upsert)

    def delete(self, filt, collection=None):
        # load default collection when collection isn't declared
        collection = self.load_default_collection(collection)
        r = self.handler[collection].delete_one(filt)
        if r.acknowledged:
            return r.deleted_count
        else:
            return None