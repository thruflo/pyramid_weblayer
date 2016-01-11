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


from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
from boto import dynamodb2

import re

import datetime

DEFAULTS = {
    'request_logger.max_body_size_in_bytes': os.environ.get('REQUEST_LOGGER_MAX_BODY_SIZE_IN_BYTES', 2000),
    'request_logger.path_ignore_regex': os.environ.get('REQUEST_LOGGER_PATH_IGNORE_REGEX', '.*/auth/.*'),
    'request_logger.mimetype_ignore_regex': os.environ.get('REQUEST_LOGGER_MIMETYPE_IGNORE_REGEX', '.*multipart.*'),
    'request_logger.request_id_header_name': os.environ.get('REQUEST_LOGGER_REQUEST_ID_HEADER_NAME', 'X_REQUEST_ID'),
}

# 20 KB.
MAX_BODY_SIZE_IN_BYTES = 20000

IGNORE_PATH_VALIDATOR = re.compile('{0}'.format(DEFAULTS['request_logger.path_ignore_regex']))
IGNORE_MIMETYPE_VALIDATOR = re.compile('{0}'.format(DEFAULTS['request_logger.mimetype_ignore_regex']))

WRITE_METHODS = ('POST', 'PUT', 'DELETE', 'PATCH')
REQUEST_ID_HEADER_NAME = DEFAULTS['request_logger.request_id_header_name']

def client_factory():
    """Return an AmazonDB client that provides a
      ``put_item(data=data)`` method.
    """

    return Table(
        'request_storer',
        schema=[HashKey('request_id')],
        connection=dynamodb2.connect_to_region('eu-west-1')
    )

class RequestLoggerTweenFactory(object):
    """Simple pyramid tween to log all of our requests by Heroku request id."""

    def __init__(self, handler, registry, client=None):
        self.handler = handler
        self.registry = registry
        self.settings = registry.settings
        self.client = client
        if not self.client:
            # If we are testing and haven't supplied a client, mock it out.
            if self.settings.get('mode') == 'testing':
                from mock import Mock
                self.client = Mock()
            else:
                self.client = client_factory()

    def __call__(self, request):
        """Request logger pyramid tween, logs requests that have errored and
        are of HTTP WRITE_METHODS to DynamoDB."""

        # Unpack the request.
        path = request.path
        headers = request.headers

        # Figure out if we'll want to log an exception or not.
        request_id = headers.get(REQUEST_ID_HEADER_NAME, None)
        should_log_exc = request_id and request.method.upper() in WRITE_METHODS

        # Let the app actually handle the request.
        try:
            response = self.handler(request)
        except Exception:
            # Extract the information and re-raise.
            body = self.get_body(request)
            self.log_request(request_id, path, headers, body)
            raise

        # Then if the request was interesting and resulted in
        # an error response, then spawn a green thread to log
        # the request data in the background.
        if should_log_exc and response.status_int > 399:
            body = self.get_body(request)
            self.log_request(request_id, path, headers, body)

        return response

    def get_body(self, request):
        """Read the request body upto a maximum length."""

        if IGNORE_MIMETYPE_VALIDATOR.match(request.content_type):
            return 'N/a - multipart request.'

        if IGNORE_PATH_VALIDATOR.match(request.path):
            return 'N/a - may contain password'

        # Get the body file and wind it back to the beginning.
        sock = request.body_file_seekable
        start_pos = sock.tell()
        sock.seek(0)

        # Read upto a maximum length.
        body = sock.read(MAX_BODY_SIZE_IN_BYTES)

        # And just for sanity's sake, put it back where we
        # found it.
        sock.seek(start_pos)
        return body

    def put_to_dynamodb(self, data):
        """Make a PUT request to dynamodb2 and insert the data"""

        try:
            self.client.put_item(data=data)
        except UnicodeDecodeError:
            data['body'] = 'Unicode error when parsing'
            self.client.put_item(data=data)

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

        # Fire and forget.
        t = threading.Thread(target=self.put_to_dynamodb, args=(data,))
        t.start()
