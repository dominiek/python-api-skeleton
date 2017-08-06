
import os
import json
import urllib
import sys
from flask import Flask, g, jsonify
from pymongo import MongoClient
from mongomock import MongoClient as MongoClientMock
from bson.objectid import ObjectId
test_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(test_dir + '/../')
from api.users import *
from api.utils import decode_jwt
import traceback
import api.constants as constants
import logging

for _ in ["elasticsearch", "urllib3", "PIL"]:
    logging.getLogger(_).setLevel(logging.CRITICAL)

def setup_db():
    client = MongoClient(constants.MONGO_URL)
    db = client.api_test
    return db

def setup_mock_db():
    client = MongoClientMock(constants.MONGO_URL)
    db = client.api_test
    return db

def create_test_user_and_token(db, appendix='', admin=False):
    account = db.accounts.find_one({'name': 'api-test'})
    if not account:
        account = create_account(db, 'api-test')
    user = db.users.find_one({'username': 'dominiek-test' + appendix})
    permissions = {'account_owner': True}
    if admin:
        permissions['super_admin'] = True
    if not user:
        user = create_user(db, account['_id'], 'dominiek-test@dominiek.com' + appendix, 'dominiek-test' + appendix, 'ntskntsk', 'Dominiek Ter Heide' + appendix, permissions=permissions)
    authenticated_user = authenticate_user(db, user['email'], 'ntskntsk')
    token = encode_user_session(authenticated_user['_id'])
    return user, token

def create_flask_app(mock=False, db=None):
    if db == None:
        if mock:
            db = setup_mock_db()
        else:
            db = setup_db()
    def before_setup_db():
        g.db = db
    app = Flask(__name__)
    app.before_request(before_setup_db)
    app.before_request(decode_jwt)

    @app.errorhandler(KeyError)
    def handle_key_error(error):
        error = {'message': 'Missing required parameter: {}'.format(error.message)}
        return jsonify({'error': error})

    @app.errorhandler(Exception)
    def handle_exception(error):
        traceback.print_exc()
        error = {'message': str(error), 'type': str(type(error).__name__)}
        return jsonify({'error': error})

    return app

def api_post(app, endpoint, params={}, token=None, delete=False, wait=True):
    headers = None
    if token:
        headers = {}
        headers['Authorization'] = 'Bearer {}'.format(token)
    method = app.post
    if delete:
        method = app.delete
    res = method(endpoint, data=json.dumps(params), content_type='application/json', headers=headers)
    if res.data[0] != '{':
        raise Exception('Invalid Response from API: {}'.format(res.data))
    data = json.loads(res.data)
    if wait == True and data.get('queued', None):
        time.sleep(1)
        return api_post(app, endpoint, params=params, token=token, delete=delete, wait=wait)
    error = data.get('error', None)
    result = data.get('result', None)
    return error, result

def api_get(app, endpoint, params=None, token=None, wait=True, raw=False):
    if params:
        endpoint += '?{}'.format(urllib.urlencode(params))
    headers = None
    if token:
        headers = {}
        headers['Authorization'] = 'Bearer {}'.format(token)
    res = app.get(endpoint, headers=headers)
    if raw == True:
        return res
    if res.data[0] != '{':
        raise Exception('Invalid Response from API: {}'.format(res.data))
    data = json.loads(res.data)
    if wait == True and data.get('queued', None):
        time.sleep(1)
        return api_get(app, endpoint, params=params, token=token, wait=wait)
    error = data.get('error', None)
    result = data.get('result', None)
    return error, result
