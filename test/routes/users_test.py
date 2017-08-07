import os
import sys
import unittest
import json
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from utils import *
db = setup_mock_db()
app = create_flask_app(mock=True, db=db)

from api.routes.users import app as users_app
app.register_blueprint(users_app, url_prefix='/1/users')

from api.users import get_user

class RoutesUsersTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_self_crud(self):
        db.accounts.remove({'company_name': 'Skeleton'})
        db.users.remove({'username': 'dominiek'})

        # Sign Up
        params = {
            'invite_code': 'invitecode',
            'username': 'dominiek',
            'password': 'blabla',
            'name': 'Dominiek',
            'company_name': 'Skeleton',
            'email': 'hello@dominiek.com'
        }
        error, result = api_post(self.app, '/1/users', params)
        self.assertEquals(error, None)
        self.assertEquals(result['permissions']['account_owner'], True)
        params = {
            'email': 'hello@dominiek.com',
            'password': 'blabla'
        }

        # Login
        error, result = api_post(self.app, '/1/users/sessions', params)
        self.assertEquals(error, None)
        token = result['token']

        # Get info
        error, result = api_get(self.app, '/1/users/self', token=token)
        self.assertEquals(error, None)
        self.assertEquals(result['user']['username'], 'dominiek')

        # Forgot Password
        error, result = api_post(self.app, '/1/users/forgot_password', {'email': 'dominiek'})
        self.assertEquals(error, None)
        _, me = api_get(self.app, '/1/users/self', token=token)
        user = me['user']
        self.assertEquals(len(user['reset_password_token']), 32)

        # Reset Password
        params = {
            'reset_password_token': user['reset_password_token'],
            'email': 'hello@dominiek.com',
            'new_password': 'blabla2'
        }
        error, result = api_post(self.app, '/1/users/reset_password', params)
        self.assertEquals(error, None)
        _, me = api_get(self.app, '/1/users/self', token=token)
        user = me['user']
        self.assertEquals(user.has_key('reset_password_token'), False)

        # Delete account
        error, result = api_post(self.app, '/1/users/self', params={'confirm': True}, delete=True, token=token)
        self.assertEquals(error, None)

    def test_admin_crud(self):
        user, token = create_test_user_and_token(db)
        admin_user, admin_token = create_test_user_and_token(db, 'admin', admin=True)

        # Get user (no permissions)
        error, result = api_get(self.app, '/1/users/{}'.format(user['_id']), token=token)
        self.assertEquals(error['message'], 'Sorry, you have no permissions for this action')

        params = {
            'name': 'Funky'
        }

        # Update user (no permissions)
        error, result = api_post(self.app, '/1/users/{}'.format(user['_id']), params, token=token)
        self.assertEquals(error['message'], 'Sorry, you have no permissions for this action')

        # Delete user (no permissions)
        error, result = api_post(self.app, '/1/users/{}'.format(user['_id']), params={'confirm': True}, delete=True, token=token)
        self.assertEquals(error['message'], 'Sorry, you have no permissions for this action')

        # Get user
        error, result = api_get(self.app, '/1/users/{}'.format(user['_id']), token=admin_token)
        self.assertEquals(error, None)
        self.assertEquals(result['user']['_id'], str(user['_id']))

        # Update user
        error, result = api_post(self.app, '/1/users/{}'.format(user['_id']), params, token=admin_token)
        self.assertEquals(error, None)
        error, result = api_get(self.app, '/1/users/{}'.format(user['_id']), token=admin_token)
        self.assertEquals(error, None)
        self.assertEquals(result['user']['name'], 'Funky')

        # Delete user
        error, result = api_post(self.app, '/1/users/{}'.format(user['_id']), params={'confirm': True}, delete=True, token=admin_token)
        self.assertEquals(error, None)


    def test_list_public_users(self):
        # Sign Up
        params = {
            'invite_code': 'invitecode',
            'username': 'someone',
            'password': 'blabla',
            'name': 'Dominiek',
            'company_name': 'Skeleton',
            'email': 'info@dominiek.com'
        }
        error, result = api_post(self.app, '/1/users', params)
        self.assertEquals(error, None)

        # Find public record
        error, result = api_get(self.app, '/1/users?username=someone')
        self.assertEquals(error, None)
        self.assertEquals(result[0]['username'], 'someone')
        self.assertEquals(result[0].get('email', None), None)
        self.assertEquals(result[0].get('hash', None), None)

if __name__ == "__main__":
    unittest.main()
