from ..mongo import Mongo
from pymongo import ReturnDocument

class MongoAffinity(Mongo):
    def __init__(self,host, port, db):
        super(MongoAffinity,self).__init__(host, port, db)


    def update_affinity(self, collection, cluster_info, category, clustering_type):
        #controllare se esiste un doc per la news
        selected_collection = self.connection[collection]
        updated = selected_collection.update_one({'category':category}, {"$set":{"clustering_type": cluster_info}}, upsert=True)
