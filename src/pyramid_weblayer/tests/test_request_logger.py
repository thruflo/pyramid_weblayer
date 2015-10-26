#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for `pyramid_weblayer.request_logger`."""

import unittest

try: # pragma: no cover
    from mock import Mock
except: # pragma: no cover
    pass

from pyramid_weblayer import request_logger
from pyramid import testing


# XXX Stub the handler so we have better control.
class StubHandler(object):

    def __init__(self, return_status_code):
        self.return_status_code = return_status_code

    def __call__(self, request):
        class StubStub(object):
            status_int = self.return_status_code
        return StubStub()


class TestRequestLogger(unittest.TestCase):
    """Test the logic of py:class:`~pyramid_weblayer.request_logger`."""

    def test_put_item_called(self):
        """Validate logic to request logging."""

        # Stub our request handler.
        handler = StubHandler(return_status_code=200)
        # Mock DynamoDB client.
        client = Mock()
        # Create a dummy request and an empty registry.
        request = testing.DummyRequest(post={}, content_type='', body_file_seekable=Mock())
        registry = Mock()
        # Instantiate the client and call it with the mock request.
        tween_client = request_logger.RequestLoggerTweenFactory(handler, registry, client=client)
        # Let the client process the request.
        logger = tween_client(request)
        # Assert we didn't log as we don't have the right header keys and we have a 200.
        assert not client.put_item.called
        # Now let's put the right header key but status is still 200.
        request = testing.DummyRequest(
                headers={'X_REQUEST_ID': '3rij'},
                post={}, content_type='',
                body_file_seekable=Mock())
        logger = tween_client(request)
        assert not client.put_item.called
        # And now we have an error with the right key, should log.
        handler = StubHandler(return_status_code=400)
        tween_client = request_logger.RequestLoggerTweenFactory(handler, registry, client=client)
        logger = tween_client(request)
        # Assert it was logged.
        assert client.put_item.called
