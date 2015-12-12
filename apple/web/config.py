#!/usr/bin/python
# -*- coding: utf-8 -*-


DB_NAME = 'Aplle'
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017

USER_COLLECTION = 'User'
ORDER_COLLECTION = 'Order'

STATUS = {
    'created': 0,
    'accept': 1,
    'success': 2,
    'cancel': 3,
}
