# encoding: utf-8
from ..mongo import Mongo

class MongoChat(Mongo):
    def __init__(self,host, port, db):
        super(MongoChat,self).__init__(host, port, db)
        self.collection_chat = "Chat"

    def set_status(self, user, status):
        selected_collection = self.connection[self.collection_chat]
        tmp = {
            "user": user,
            "status": status
        }
        selected_collection.insert_one(tmp)
