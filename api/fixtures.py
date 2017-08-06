
import logging
import time
import constants
from bson.objectid import ObjectId
from bcrypt import hashpw, gensalt
import md5

def create_root_accounts(db):
    user = db.users.find_one({"username": "admin"})
    if user:
        return
    logging.info('Creating root account fixtures in MongoDB')
    db.accounts.insert({
        "_id": ObjectId("57d2f84ac0b9a374e874e1fb"),
        "company_name": "Skeleton",
        "is_verified": True
    })
    api_key = md5.new()
    api_key.update(constants.ADMIN_ACCOUNT_PASSWORD)
    db.users.insert({
        "_id": ObjectId("57d2f84bc0b9a374e874e1fc"),
        "username": "admin",
        "account_id": "57d2f84ac0b9a374e874e1fb",
        "hash": str(hashpw(str(constants.ADMIN_ACCOUNT_PASSWORD), gensalt())),
        "email" : constants.ADMIN_ACCOUNT_EMAIL,
        "api_key": api_key.hexdigest(),
    	"permissions" : {
    		"account_owner" : True,
    		"super_admin" : True
    	}
    })
    db.accounts.insert({
        "_id": ObjectId("57d2f84ac0b9a374e884e1fb"),
        "company_name": "Skeleton Demo",
        "is_verified": True
    })
