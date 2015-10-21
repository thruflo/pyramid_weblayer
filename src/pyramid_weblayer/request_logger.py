# -*- coding: utf-8 -*-

"""WSGI middleware to log all requests to Dynamodb on AWS.
Username and API Key are infered from following environment variables:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
The user needs a policy on AWS that allows it to PUT to DynamoDB.
You can ignore body of the requests by controlling the regexes set by env var:
- REQUEST_LOGGER_MIMETYPE_IGNORE_REGEX
- REQUEST_LOGGER_PATH_IGNORE_REGEX
"""

import logging
logger = logging.getLogger(__name__)

import threading
import os

from pyramid import request

from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER
from boto import dynamodb2

import re

from sys import getsizeof
import datetime


DEFAULTS = {
    'request_logger.max_body_size_in_bytes': os.environ.get('REQUEST_LOGGER_MAX_BODY_SIZE_IN_BYTES', 2000),
    'request_logger.path_ignore_regex': os.environ.get('REQUEST_LOGGER_PATH_IGNORE_REGEX', '.*/auth/.*'),
    'request_logger.mimetype_ignore_regex': os.environ.get('REQUEST_LOGGER_MIMETYPE_IGNORE_REGEX', '.*multipart.*'),
}

# 20 KB.
MAX_BODY_SIZE_IN_BYTES = 20000
# Roughly two bytes per char.
MAX_BODY_SIZE_IN_LEN = MAX_BODY_SIZE_IN_BYTES / 2

IGNORE_PATH_VALIDATOR = re.compile('{0}'.format(DEFAULTS['request_logger.path_ignore_regex']))
IGNORE_MIMETYPE_VALIDATOR = re.compile('{0}'.format(DEFAULTS['request_logger.mimetype_ignore_regex']))

class RequestLoggerMiddleware(object):
    """Simple middleware to log all of our requests by Heroku request id."""

    def __init__(self, app, **kwargs):
        self.app = app

    def __call__(self, environ, start_response):

        # Unpack.
        app = self.app

        # Get Heroku's request identifier.
        request_id = environ.get('HTTP_X_REQUEST_ID', None)
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        content_type = environ.get('CONTENT_TYPE', None)

        # If we have it, save the request data.
        if request_id:
            # Create a pyramid request from environ.
            pyramid_request = request.Request(environ)
            headers = pyramid_request.headers
            path = pyramid_request.path
            body = None

            # If it's a PUT or POST request log body as well.
            if environ['REQUEST_METHOD'].upper() == 'POST' or\
                    environ['REQUEST_METHOD'].upper() == 'PUT':
                # If it's a multipart request don't bother.
                if IGNORE_MIMETYPE_VALIDATOR.match(content_type):
                    body = 'it is a multipart request'
                else:
                    # Unless we are in the path we want to ignore body (e.g: auth)
                    if not IGNORE_PATH_VALIDATOR.match(path):
                        # Truncate string to MAX_BODY_SIZE_IN_LEN.
                        if content_length > MAX_BODY_SIZE_IN_LEN:
                            body = pyramid_request.body_file.read(MAX_BODY_SIZE_IN_BYTES)
                            pyramid_request.body_file.seek(0)
                        else:
                            body = pyramid_request.body

            self.log_request(request_id, path, headers, body)

        return app(environ, start_response)

    def log_request(self, key, path, headers, body):
        """Log the path, headers and body of the HTTP request on a
        key value store db, key is heroku request id.
        """

        if not body:
            body = {}
        # Build a dict with key, headers and body.
        now = datetime.datetime.now().isoformat()
        data = {'request_id': key, 'body': body, 'path': path, 'created': now}
        for k, v in headers.items():
            data[k] = v
        # Put to Dynamodb as a separated thread.
        threading.Thread(target=put_to_dynamodb, args=(data,)).start()


def put_to_dynamodb(data):
    """Make a PUT request to dynamodb2 and insert the data"""

    requests_table = Table('request_storer',
            schema=[HashKey('request_id')],
            connection=dynamodb2.connect_to_region('eu-west-1')
    )
    try:
        requests_table.put_item(data=data)
    except UnicodeDecodeError:
        data['body'] = 'Unicode error when parsing'
        requests_table.put_item(data=data)

def request_logger_middleware_factory(app, global_config):
    return RequestLoggerMiddleware(app)

