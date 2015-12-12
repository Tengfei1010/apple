#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'kevin'

from flask import Flask, render_template, request, redirect, url_for

import flask.ext.login as flask_login
from flask.ext.login import login_user, login_required
from flask.ext.login import logout_user


from user import User

app = Flask(__name__)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.secret_key = 'apple apple'  # Change this!


@login_manager.user_loader
def load_user(username):
    # u = app.config['USERS_COLLECTION'].find_one({"_id": username})
    # if not u:
    #     return None
    return User('test', 'test')


@app.route('/login', methods=['POST'])
def login():
    """Add two numbers server side, ridiculous but well..."""
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    if not username or not password:
        error_msg = u'用户名和密码必填！'
        return render_template('login.html', error_msg=error_msg)
    if username != 'test' or password != 'test':
        error_msg = u'用户名或者密码错误!'
        return render_template('login.html', error_msg=error_msg)
    else:
        current_user = User(username, password)
        login_user(current_user)

    return redirect(url_for('.do_order'))


@app.route('/do_order', methods=['POST', 'GET'])
def do_order():
    return render_template('do_order.html')


@login_required
@app.route('/order', methods=['POST', 'GET'])
def order():
    if request.method == 'GET':
        return render_template('do_order.html')

    else:
        phone = request.form.get('phone', None)
        amount = request.form.get('amount', None)
        address = request.form.get('address', None)
        apple_type = request.form.get('type', None)

        if not phone or not amount or not address:
            return render_template('do_order.html', error_msg='所有项必填！')
        # save in db
        return render_template('order_success.html', order_id='123456')


@login_required
@app.route('/my_order', methods=['GET'])
def my_order():

    return render_template('my_order.html')


@login_required
@app.route('/login_out', methods=['GET'])
def login_out():
    logout_user()
    return render_template('login.html')


@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(port=8888, debug=True)
