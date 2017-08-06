
import os
import sys
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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
