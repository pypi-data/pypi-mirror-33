# encoding: utf-8
from ..mongo import Mongo

class MongoChat(Mongo):
    def __init__(self,host, port, db):
        super(MongoChat,self).__init__(host, port, db)
        self.collection_chat = "Chat"
        self.collection_user_social_sid = "Users_Social_Sid"
        self.collection_user_social = "Users_Social"

    def set_status(self, user, status):
        selected_collection = self.connection[self.collection_chat]
        tmp = {
            "user": user,
            "status": status
        }
        selected_collection.insert_one(tmp)

    def update_user_sid(self, user_id, sid):
        selected_collection = self.connection[self.collection_user_social_sid]
        selected_collection.update({"_id": user_id}, {"$set": {"sid": sid}}, upsert=True)

    def update_status(self, user_id, status):
        selected_collection = self.connection[self.collection_user_social]
        selected_collection.update({"_id": user_id}, {"$set": {"status": status}})

    def register_user(self, user_id):
        selected_collection = self.connection[self.collection_user_social]
        selected_collection.insert_one({"_id": user_id, "friends": [], "status": 0})

    def add_friend(self, user_id, friend_user_id):
        selected_collection = self.connection[self.collection_user_social]
        selected_collection.update({"_id": user_id}, {"$addToSet": {"friends": friend_user_id}})

    def remove_friend(self, user_id, friend_user_id):
        selected_collection = self.connection[self.collection_user_social]
        selected_collection.update({"_id": user_id}, {"$pull": {"friends": friend_user_id}})

    def get_friends_list(self, user_id):
        selected_collection = self.connection[self.collection_user_social]
        friends = selected_collection.find_one({"_id": user_id}, {"friends": 1})
        if friends:
            return friends["friends"]
        return []