from ..mongo import Mongo
from pymongo import ReturnDocument

class MongoAffinity(Mongo):
    def __init__(self,host, port, db):
        super(MongoAffinity,self).__init__(host, port, db)


    def update_affinity(self, cluster_info, category, clustering_type):
        collection_name = "AffinityUsers"
        selected_collection = self.connection[collection_name]
        updated = selected_collection.update_one({'category':category}, {"$set":{clustering_type: cluster_info}}, upsert=True)
