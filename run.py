#!/usr/bin/env python

import logging
import api.constants as constants
from flask import Flask, jsonify, g, request
from flask.ext.cors import CORS
import time

from pymongo import MongoClient

client = MongoClient(constants.MONGO_URL)
db = client[constants.MONGO_DB]

app = Flask(__name__)
CORS(app)

from api.utils import decode_jwt
app.before_request(decode_jwt)

def setup_db():
    g.db = db
    g.mongo_client = client
app.before_request(setup_db)

from api.routes.users import app as users_app
app.register_blueprint(users_app)

@app.before_request
def before_request():
  g.start = time.time()

@app.teardown_request
def teardown_request(exception=None):
    request_duration = time.time() - g.start
    max_seconds = 3
    if request_duration > max_seconds:
        logging.warn('Request took longer than {} seconds: {} {}'.format(max_seconds, request.method, request.path))

@app.route("/", methods=['GET'])
def route_index():
    return jsonify({
        'apiVersion': 1.0
    })

import traceback

@app.errorhandler(KeyError)
def handle_key_error(error):
    error = {'message': 'Missing required parameter: {}'.format(error.message)}
    return jsonify({'error': error})

@app.errorhandler(Exception)
def handle_exception(error):
    logging.warning('Error happened in request: {}'.format(str(error)))
    traceback.print_exc()
    error = {'message': str(error), 'type': str(type(error).__name__)}
    return jsonify({'error': error})

for _ in ["elasticsearch", "urllib3", "PIL"]:
    logging.getLogger(_).setLevel(logging.CRITICAL)

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    app.run(host='localhost', port=3005, debug=False, threaded=False)
