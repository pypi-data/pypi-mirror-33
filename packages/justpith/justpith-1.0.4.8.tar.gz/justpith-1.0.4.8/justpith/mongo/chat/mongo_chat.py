# encoding: utf-8
from ..mongo import Mongo

class MongoChat(Mongo):
    def __init__(self,host, port, db):
        super(MongoChat,self).__init__(host, port, db)
