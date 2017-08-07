
from flask import request, jsonify, redirect, g, Response
from users import decode_user_session, get_user, get_account, has_permission, get_user_by_api_key
import json

class NotFoundError(Exception):

    def __init__(self, object_type, object_id):
        message = 'Could not find {} with ID {}'.format(object_type, object_id)
        super(Exception, self).__init__(message)

def response_with_optional_filename(res):
    if type(res).__name__ == 'str':
        res = Response(res)
    filename = request.args.get('filename', None)
    if filename != None:
        res.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return res

def sanitize_result(result):
    if type(result) == type([]):
        for item in result:
            if item.has_key('_id'):
                item['_id'] = str(item['_id'])
    else:
        if result and result.has_key('_id'):
            result['_id'] = str(result['_id'])
    return result

def decode_jwt():
    authorization_header = request.headers.get('Authorization', '')
    parsed = authorization_header.split(' ')
    g.user_id = None
    if len(parsed) > 1:
        g.user_id = decode_user_session(parsed[1])

def get_user_and_account():
    user = None
    account = None
    if g.user_id:
        user = get_user(g.db, g.user_id)
    if user:
        account = get_account(g.db, user['account_id'])
    return user, account

def get_api_key(params={}):
    api_key_header = request.headers.get('X-Api-Key', '')
    if len(api_key_header) > 0:
        return api_key_header
    if params != None:
        return params['api_key']
    return None

def require_user(params={}):
    if g.user_id:
        user = get_user(g.db, g.user_id)
        if not user:
            raise Exception('Failed to authenticate via JWT session (user object not found)')
    else:
        api_key = get_api_key(params)
        if not api_key:
            raise Exception('Not authenticated, expected either valid JWT session or api_key')
        user = get_user_by_api_key(g.db, api_key)
        if not user:
            raise Exception('Failed to authenticate via api_key')
    return user

def require_user_and_account(params={}):
    user = require_user(params)
    return user, get_account(g.db, user['account_id'])

def require_permission(context, permission):
    if not has_permission(context, permission):
        raise Exception('Sorry, you have no permissions for this action')
    return True

def has_feature_access(feature, user, account):
    if user['permissions'].get('super_admin', False):
        return True
    features = account['permissions'].get('features', [])
    return feature in features

def require_feature_access(feature, user, account):
    if not has_feature_access(feature, user, account):
        raise Exception('Sorry, no permission to access {} found. Please contact support'.format(feature))
