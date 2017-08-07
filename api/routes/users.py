
from flask import Blueprint, request, jsonify, redirect, g
import logging
import time

import api.constants as constants
from ..users import *
from ..utils import sanitize_result, require_user, require_user_and_account, require_permission


app = Blueprint('users', __name__)

def public_user(user):
    return {
        '_id': str(user['_id']),
        'username': user['username']
    }

def clean_internals(user):
    if user.has_key('hash'):
        del user['hash']
    return user

@app.route("", methods=['POST'])
def route_create_user():
    params = request.get_json()
    if params['invite_code'] != 'invitecode':
        raise Exception('Invalid Invite Code given')
    account = create_account(g.db, params['company_name'])
    permissions = {'account_owner': True}
    user = create_user(g.db, account['_id'], params['email'], params['username'], params['password'], params['name'], permissions=permissions, send_welcome_mail=True)
    return jsonify({'result': clean_internals(sanitize_result(user))})

@app.route("", methods=['GET'])
def route_list_users():
    username = str(request.args['username'])
    users = list_users(g.db, username=username)
    return jsonify({
        'result': map(public_user, users)
    })

@app.route("/<user_id>", methods=['GET'])
def route_get_user(user_id):
    admin_user, admin_account = require_user_and_account()
    require_permission(admin_user, 'super_admin')
    user = get_user(g.db, user_id)
    account = get_account(g.db, str(user['account_id']))
    return jsonify({
        'result': {
            'user': clean_internals(sanitize_result(user)),
            'account': sanitize_result(account)
        }
    })

@app.route("/<user_id>", methods=['POST'])
def route_update_user(user_id):
    admin_user, admin_account = require_user_and_account()
    require_permission(admin_user, 'super_admin')
    user = get_user(g.db, user_id)
    account = get_account(g.db, str(user['account_id']))
    params = request.get_json()
    valid_fields = ['name', 'thumbnail_image_uid']
    for key in params:
        if key not in valid_fields:
            raise Exception('Not a valid updateable field: {}'.format(key))
        if key == 'name' and len(params['name']) == 0:
            raise Exception('Field name cannot be blank')
        user[key] = params[key]
    save_user(g.db, user)
    return jsonify({'result': clean_internals(sanitize_result(user))})

@app.route("/<user_id>", methods=['DELETE'])
def route_remove_user(user_id):
    admin_user, admin_account = require_user_and_account()
    require_permission(admin_user, 'super_admin')
    user = get_user(g.db, user_id)
    account = get_account(g.db, str(user['account_id']))
    params = request.get_json()
    if params['confirm'] != True:
        raise Exception('Need confirmation for user removal')
    remove_account(g.db, account['_id'])
    remove_user(g.db, user['_id'])
    return jsonify({'result': {'success': True}})

@app.route("/self", methods=['GET'])
def route_get_users_self():
    user, account = require_user_and_account()
    del user['hash']
    return jsonify({
        'result': {
            'user': clean_internals(sanitize_result(user)),
            'account': sanitize_result(account)
        }
    })

@app.route("/self", methods=['POST'])
def route_update_users_self():
    params = request.get_json()
    user, account = require_user_and_account(params)
    valid_fields = ['name', 'thumbnail_image_uid']
    for key in params:
        if key not in valid_fields:
            raise Exception('Not a valid updateable field: {}'.format(key))
        if key == 'name' and len(params['name']) == 0:
            raise Exception('Field name cannot be blank')
        user[key] = params[key]
    save_user(g.db, user)
    return jsonify({'result': clean_internals(sanitize_result(user))})

@app.route("/self", methods=['DELETE'])
def route_remove_users_self():
    params = request.get_json()
    user = require_user()
    account = get_account(g.db, user['account_id'])
    if params['confirm'] != True:
        raise Exception('Need confirmation for user removal')
    remove_account(g.db, account['_id'])
    remove_user(g.db, user['_id'])
    return jsonify({'result': {'success': True}})

@app.route("/sessions", methods=['POST'])
def route_create_users_session():
    params = request.get_json()
    authenticated_user = authenticate_user(g.db, params['email'], params['password'])
    token = encode_user_session(authenticated_user['_id'])
    return jsonify({'result': {'token': token}})

@app.route("/forgot_password", methods=['POST'])
def route_forgot_password():
    params = request.get_json()
    user = get_user_by_email(g.db, params['email'])
    if not user:
        user = get_user_by_username(g.db, params['email'])
    if not user:
        raise Exception('No user known by this email or username')
    forgot_password(g.db, user)
    return jsonify({'result': {'success': True}})

@app.route("/reset_password", methods=['POST'])
def route_reset_password():
    params = request.get_json()
    user = get_user_by_email(g.db, params['email'])
    if not user:
        raise Exception('No user known by this email')
    reset_password(g.db, user, params['reset_password_token'], params['new_password'])
    return jsonify({'result': {'success': True}})
