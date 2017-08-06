
# Python API Skeleton

This is a simple Python-based JSON API skeleton. It contains basic foundational User and Account creation API logic for SaaS applications (mobile or SPAs). Features:

* Simple persistence using MongoDB
* Versioned JSON API calls
* User authentication using JSON Web Token
* Forgot/reset password logic
* User search, creation and deletion
* Simple user permissions (super_admin vs none)
* Emailing using [Postmark](http://postmarkapp.com)
* Unit tests for both model and controller level logic
* API token creation and authentication logic
* Helper functions for accessing resources
* Automatically creates fixtures for development mode
* Docker build file with build speed optimizations

## API Routes


All routes are name spaced with a v1 version:

```
POST    /1/users                       # Create user
GET     /1/users/self                  # Get my user info
DELETE  /1/users/self                  # Delete my account
POST    /1/users/self                  # Update my account
GET     /1/users                       # Search/List users (for admin)
POST    /1/users/sessions              # Get auth token (create session)
DELETE  /1/users/self                  # Delete my account
POST    /1/users/forgot_password       # Send forgot password mail
POST    /1/users/reset_password        # Use reset password token to set new password
```

## Configuration

All defaults are set in `api/constants.py`:

```python

ENVIRONMENT = os.getenv('PYTHON_ENV', 'test')
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_URL = 'mongodb://'+MONGO_HOST+':27017/'
MONGO_DB = os.getenv('MONGO_DB', 'api_' + ENVIRONMENT)

APP_NAME = 'Skeleton'
APP_HOST = 'skeleton.api'
if ENVIRONMENT == 'development':
    APP_HOST = 'skeleton.localhost:3000'
JWT_SECRET = 'JWTs3cr3t'

ADMIN_ACCOUNT_EMAIL = 'info@skeleton.api'
ADMIN_ACCOUNT_PASSWORD = 'api.skeleton'

MAILER_FROM = 'notifier@skeleton.api'
MAILER_INBOUND = 'info@skeleton.api'
MAILER_POSTMARK_API_KEY = ''
```

## Unit Tests

```
make test
```

## Running

```
python run.py
```

The API can now be accessed at [http://localhost:3005](http://localhost:3005). To run via Gunicorn:

```
make gunicorn
```

To adjust the number of workers, either edit the Makefile or use the `GUNICORN_NUM_WORKERS` env variable.

## Deployment / Docker

```bash
docker build -t my-api .
```

## Todo

* Admin user management routes
