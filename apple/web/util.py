#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient

from config import *


client = MongoClient(MONGODB_HOST, MONGODB_PORT)


class MongDBSession(object):
    def __init__(self, db_name=DB_NAME):
        self.session = client
        self.new_db = None

        # init
        self._connect_db(db_name)
        self.collection = None

    def create_db(self, db_name=DB_NAME):
        self.new_db = self.session[db_name]

    def _connect_db(self, db_name=DB_NAME):
        self.connect = self.session[db_name]

    def _connect_collection(self, collection):
        self.collection = self.connect[collection]

    def query_all(self, collection, find_=None):
        self._connect_collection(collection)
        return self.collection.find(find_)

    def query_one(self, collection, find_=None):
        self._connect_collection(collection)
        return self.collection.find_one(find_)

    def query_sort(self, collection, find_=None):
        self._connect_collection(collection)
        return self.collection.find().sort(find_, pymongo.DESCENDING)

    def query_by_id(self, collection, query_id):
        self._connect_collection(collection)
        return self.collection.find_one({'_id': ObjectId(query_id)})

    def insert_one(self, collection, value):
        self._connect_collection(collection)
        inserted_id = self.collection.insert_one(value).inserted_id
        return inserted_id

    def insert_all(self, collection, values):
        self._connect_collection(collection)
        inserted_ids = self.collection.insert_many(values).inserted_ids
        return inserted_ids

    def update_one(self, collection, filter, value):
        self._connect_collection(collection)
        matched_count = self.collection.update_one(filter, value).matched_count
        return matched_count
