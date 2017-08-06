
from bson.objectid import ObjectId
from bcrypt import hashpw, gensalt
import md5
import jwt
import time
import constants
import datetime
from mailer import send_mail

def _set_account_defaults(doc):
    doc['is_verified'] = False
    doc['permissions'] = {}
    doc['plan'] = {}
    doc['created_ts'] = time.time()

def _set_user_defaults(doc):
    doc['permissions'] = {}
    doc['created_ts'] = time.time()

def create_account(db, company_name, **kwargs):
    doc = {}
    _set_account_defaults(doc)
    for key in kwargs:
        doc[key] = kwargs[key]
    doc['company_name'] = company_name
    job = db.accounts
    inserted_id = job.insert_one(doc).inserted_id
    return get_account(db, inserted_id)

def remove_account(db, id):
    job = db.accounts
    return job.remove({'_id': ObjectId(id)})

def get_account(db, id):
    job = db.accounts
    return job.find_one({'_id': ObjectId(id)})

def save_account(db, account):
    job = db.accounts
    return job.save(account)

def send_welcome_mail(user):
    name = user.get('name', '')
    first_name = name
    if len(first_name.split(' ')):
        first_name = first_name.split(' ')[0]
    mail_subject = "Welcome to {}".format(constants.APP_NAME)
    mail_text = """
Hi {} -

Welcome to {}!

Login using the email or username you registered with:

email: {}
username: {}

https://{}/login

Cheers,

The {} Team

""".format(first_name, constants.APP_NAME, user['email'], user['username'], constants.APP_HOST, constants.APP_NAME)
    send_mail(user['email'], mail_subject, mail_text)

def send_forgot_password_mail(user):
    name = user.get('name', '')
    first_name = name
    if len(first_name.split(' ')):
        first_name = first_name.split(' ')[0]
    mail_subject = "Reset your {} password".format(constants.APP_NAME)
    mail_text = """
Hi {} -

To set a new password, please use the following URL:

https://{}/reset_password?email={}&token={}

Cheers,

The {} Team

""".format(first_name, constants.APP_HOST, user['email'], user['reset_password_token'], constants.APP_NAME)
    send_mail(user['email'], mail_subject, mail_text)

def create_user(db, account_id, email, username, password, name, **kwargs):
    doc = {}
    collection = db.users
    if len(email) == 0 or len(username) == 0 or len(password) == 0 or len(name) == 0:
        raise Exception('Email, username, name or password cannot be blank')
    if collection.find_one({'username': username}):
        raise Exception('User already exist with that username')
    if collection.find_one({'email': email}):
        raise Exception('User already exist with that email address')
    api_key = md5.new()
    api_key.update(str(account_id) + str(time.time()) + username + name)
    if collection.find_one({'api_key': api_key.hexdigest()}):
        raise Exception('User already exist with that api_key (rare), try again')
    _set_user_defaults(doc)
    for key in kwargs:
        doc[key] = kwargs[key]
    doc['account_id'] = str(account_id)
    doc['email'] = email
    doc['username'] = username
    doc['name'] = name
    doc['api_key'] = api_key.hexdigest()
    doc['hash'] = str(hashpw(str(password), gensalt()))
    inserted_id = collection.insert_one(doc).inserted_id
    user = get_user(db, inserted_id)
    if kwargs.get('send_welcome_mail', False) == True:
        send_welcome_mail(user)
    return user

def forgot_password(db, user):
    token = md5.new()
    token.update('forgot_password' + str(user['_id']) + str(time.time()) + user['username'] + user['name'])
    user['reset_password_token'] = token.hexdigest()
    send_forgot_password_mail(user)
    save_user(db, user)

def reset_password(db, user, reset_password_token, new_password):
    if not user.has_key('reset_password_token') or user['reset_password_token'] != reset_password_token:
        raise Exception('Invalid reset_password_token given, could not reset password')
    user['hash'] = str(hashpw(str(new_password), gensalt()))
    del user['reset_password_token']
    save_user(db, user)

def get_user_by_api_key(db, api_key):
    collection = db.users
    return collection.find_one({'api_key': str(api_key)})

def get_user_by_username(db, username):
    collection = db.users
    return collection.find_one({'username': str(username)})

def get_user_by_email(db, email):
    collection = db.users
    return collection.find_one({'email': str(email)})

def authenticate_user(db, email, password):
    job = db.users
    if '@' in email:
        user = job.find_one({'email': email})
        if not user:
            raise Exception('No user exists with that email address')
    else:
        user = job.find_one({'username': email})
    if not user:
        raise Exception('No user exists with that username or email address')
    if hashpw(str(password), str(user['hash'])) == user['hash']:
        return user
    raise Exception('Invalid password for user')

def encode_user_session(user_id):
    payload = {
        'user_id': str(user_id)
    }
    return jwt.encode(payload, constants.JWT_SECRET, algorithm='HS256')

def decode_user_session(token):
    payload = jwt.decode(token, constants.JWT_SECRET, algorithms=['HS256'])
    return payload['user_id']

def remove_user(db, id):
    collection = db.users
    return collection.remove({'_id': ObjectId(id)})

def get_user(db, id):
    collection = db.users
    return collection.find_one({'_id': ObjectId(id)})

def list_users(db, **kwargs):
    collection = db.users
    return collection.find(kwargs)

def save_user(db, user):
    job = db.users
    return job.save(user)

def has_permission(context, permission):
    if not context.has_key('permissions'):
        return False
    if context['permissions'].get(permission, False) == True:
        return True
    return False
