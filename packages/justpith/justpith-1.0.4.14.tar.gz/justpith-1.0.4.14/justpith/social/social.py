from pymongo import MongoClient

class MongoSocial(object):
    def __init__(self, host, port, db):
        self.host       = host
        self.port       = port
        self.db         = db

        self.client     = None
        self.connection = None
        self.connect()

    def connect(self):
        self.client     = MongoClient(self.host, self.port)
        self.connection = self.client[self.db]


    def write_social_reccomendations(self, user_id, reccomendations):
        selected_collection = self.connection['Social']
        result = selected_collection.update({"_id": user_id},reccomendations,upsert=True)
        return result

    def write_social_logs(self, user_id, logs):
        selected_collection = self.connection['SocialLogs']
        result = selected_collection.update({"_id": user_id}, logs, upsert=True)
        return result


    def write_social_normalization(self, user_id, normalization):
        selected_collection = self.connection['SocialNormalizations']
        result = selected_collection.update({"_id": user_id}, normalization, upsert=True)
        return result
