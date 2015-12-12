#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'kevin'

import hashlib
import datetime

import pymongo
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, url_for
import flask.ext.login as flask_login
from flask.ext.login import login_user, login_required

from flask.ext.login import logout_user, current_user

from config import *
from util import MongDBSession
from user import User

app = Flask(__name__)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.secret_key = 'apple apple'  # Change this!
session = MongDBSession()


@login_manager.user_loader
def load_user(username):
    # u = app.config['USERS_COLLECTION'].find_one({"username": username})
    # if not u:
    #     return None
    return User(username, 'test')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Add two numbers server side, ridiculous but well..."""
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', None)
    password = request.form.get('password', None)
    if not username or not password:
        error_msg = u'用户名和密码必填！'
        return render_template('login.html', error_msg=error_msg)

    # check user name and password
    _result = session.query_one(USER_COLLECTION, {'username': username})

    if not _result or _result['password'] != hashlib.md5(password).hexdigest():
        error_msg = u'登录密码错误!'
        return render_template('login.html', error_msg=error_msg)
    else:
        current_user = User(username, password)
        login_user(current_user)
        if username == 'admin':
            return redirect(url_for('.main'))
    return redirect(url_for('.do_order'))


@login_required
@app.route('/do_order', methods=['GET'])
def do_order():
    return render_template('do_order.html')


@login_required
@app.route('/order', methods=['POST', 'GET'])
def order():
    if request.method == 'GET':
        return render_template('do_order.html')

    else:
        phone = request.form.get('phone', None)
        address = request.form.get('address', None)
        quantity1 = request.form.get('quantity1', None)
        quantity2 = request.form.get('quantity2', None)
        quantity3 = request.form.get('quantity3', None)
        quantity4 = request.form.get('quantity4', None)

        if not (quantity1 and quantity2 and quantity3 and quantity4):
            return render_template('do_order.html', error_msg=u'类型数量不能为零！')
        if not phone or not address:
            return render_template('do_order.html', error_msg=u'所有项必填！')

        amount = dict()
        if quantity1 or quantity1 == '0':
            amount['quantity1'] = quantity1
        if quantity2 or quantity2 == '0':
            amount['quantity2'] = quantity2
        if quantity3 or quantity3 == '0':
            amount['quantity3'] = quantity3
        if quantity4 or quantity4 == '0':
            amount['quantity4'] = quantity4
        # save order to db
        save_value = {
            'username': current_user.username,
            'create_at': datetime.datetime.now(),
            'phone': phone,
            'address': address,
            'amount': amount,
            'status': STATUS['created']
        }
        save_result = session.insert_one(ORDER_COLLECTION, save_value)
        return render_template('order_success.html', order_id=str(save_result))


@login_required
@app.route('/my_order', methods=['GET'])
def my_order():
    cur_user = current_user
    orders = session.query_all(
        ORDER_COLLECTION,
        {'username': cur_user.username}).sort(
        "create_at",
        pymongo.DESCENDING)

    results = []
    for order in orders:
        _order = dict()
        if order['status'] == STATUS['created']:
            _order['status_txt'] = u'未接受'

        elif order['status'] == STATUS['accept']:
            _order['status_txt'] = u'已接受'

        elif order['status'] == STATUS['success']:
            _order['status_txt'] = u'成功'

        elif order['status'] == STATUS['cancel']:
            _order['status_txt'] = u'取消'

        for key in order:
            _order[key] = order[key]
        results.append(_order)
    return render_template('my_order.html', orders=results)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    else:
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        re_password = request.form.get('re_password', None)
        if not (username and password and re_password):
            error_msg = u'所有项必填！'
            return render_template('register.html', error_msg=error_msg)

        if password != re_password:
            error_msg = u'两次密码不一致！'
            return render_template('register.html', error_msg=error_msg)

        # check user is exist
        is_exist = session.query_one(USER_COLLECTION, {'username': username})

        if is_exist:
            error_msg = u'用户名已存在！'
            return render_template('register.html', error_msg=error_msg)
        save_value = {
            'username': username,
            'password': hashlib.md5(password).hexdigest(),
            'create_at': datetime.datetime.now()
        }
        save_result = session.insert_one(USER_COLLECTION, save_value)
        # login user
        if save_result:
            _user = User(username, password)
            login_user(_user)
            return redirect(url_for('.do_order'))


@login_required
@app.route('/cancel', methods=['GET'])
def cancel():
    order_id = request.args.get('id', None)
    order = session.query_by_id(ORDER_COLLECTION, order_id)
    if order and order['status'] == STATUS['created']:
        session.update_one(ORDER_COLLECTION, {'_id': ObjectId(order_id)}, {
            "$set": {'status': STATUS['cancel']}
        })
    return redirect(url_for('.my_order'))


@login_required
@app.route('/accept', methods=['GET'])
def accept():
    order_id = request.args.get('id', None)
    order = session.query_by_id(ORDER_COLLECTION, order_id)
    if order and order['status'] == STATUS['created']:
        session.update_one(ORDER_COLLECTION, {'_id': ObjectId(order_id)}, {
            "$set": {'status': STATUS['accept']}
        })
    return redirect(url_for('.main'))


@login_required
@app.route('/success', methods=['GET'])
def success():
    order_id = request.args.get('id', None)
    order = session.query_by_id(ORDER_COLLECTION, order_id)
    if order and order['status'] == STATUS['accept']:
        session.update_one(ORDER_COLLECTION, {'_id': ObjectId(order_id)}, {
            "$set": {'status': STATUS['success']}
        })
    return redirect(url_for('.main'))


@login_required
@app.route('/main')
def main():
    orders = session.query_all(ORDER_COLLECTION).sort(
        "create_at",
        pymongo.DESCENDING)

    results = []
    for order in orders:
        _order = dict()
        if order['status'] == STATUS['created']:
            _order['status_txt'] = u'未接受'

        elif order['status'] == STATUS['accept']:
            _order['status_txt'] = u'已接受'

        elif order['status'] == STATUS['success']:
            _order['status_txt'] = u'成功'

        elif order['status'] == STATUS['cancel']:
            _order['status_txt'] = u'取消'

        for key in order:
            _order[key] = order[key]
        results.append(_order)
    return render_template('orders.html', orders=results)


@login_required
@app.route('/login_out', methods=['GET'])
def login_out():
    logout_user()
    return render_template('login.html')


@app.route('/')
def index():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
