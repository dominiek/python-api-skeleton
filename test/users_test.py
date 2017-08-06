
import os
import sys
import unittest
import time
test_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(test_dir + '/../')
from api.users import *
from mongomock import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.api_test

class UsersTest(unittest.TestCase):

    def test_crud(self):
        db.accounts.remove({'company_name': 'Skeleton'})
        db.users.remove({'username': 'dominiek'})
        account = create_account(db, 'Skeleton')
        user = create_user(db, account['_id'], 'info@dominiek.com', 'dominiek', 'ntskntsk', 'Dominiek Ter Heide', permissions={'account_owner': True})
        self.assertEqual(user['username'], 'dominiek')
        self.assertEqual(True, len(user['hash']) > 0)
        with self.assertRaises(Exception) as context:
            create_user(db, account['_id'], 'info@dominiek.com', 'dominiek', 'ntskntsk', 'Dominiek Ter Heide', permissions={'account_owner': True})
        self.assertTrue('already exist' in context.exception.message)
        with self.assertRaises(Exception) as context:
            authenticate_user(db, 'invalid@dominiek.com', 'ntskntsk')
        self.assertTrue('exist' in context.exception.message)
        with self.assertRaises(Exception) as context:
            authenticate_user(db, 'info@dominiek.com', 'invalid')
        self.assertTrue('password' in context.exception.message)
        # By email
        authenticated_user = authenticate_user(db, 'info@dominiek.com', 'ntskntsk')
        self.assertTrue(authenticated_user['email'], 'info@dominiek.com')
        # By username
        authenticated_user = authenticate_user(db, 'dominiek', 'ntskntsk')
        self.assertTrue(authenticated_user['email'], 'info@dominiek.com')
        token = encode_user_session(authenticated_user['_id'])
        self.assertEqual(True, len(token) > 0)
        user_id = decode_user_session(token)
        self.assertEqual(str(user['_id']), user_id)

if __name__ == "__main__":
    unittest.main()
