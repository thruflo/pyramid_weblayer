# -*- coding: utf-8 -*-

"""Extend framework using event hooks."""

import logging
logger = logging.getLogger(__name__)

def set_seen_cookie(event):
    """Add a ``has_been_seen_before`` cookie (that lasts for six weeks) to all
      HTML responses.
      
          >>> from mock import Mock
          >>> mock_event = Mock()
      
      Ignores non HTML responses::
      
          >>> mock_event.response.content_type = 'foo'
          >>> set_seen_cookie(mock_event)
          >>> mock_event.response.set_cookie.called
          False
      
      Sets a ``has_been_seen_before`` cookie::
      
          >>> mock_event.response.content_type = 'text/html'
          >>> set_seen_cookie(mock_event)
          >>> mock_event.response.set_cookie.assert_called_with(
          ...         'has_been_seen_before', 'true', max_age=3628800)
      
    """
    
    # Only set the cookie on HTML responses.
    if 'html' in event.response.content_type:
        cookie_name = 'has_been_seen_before'
        expires_after = 3628800
        event.response.set_cookie(cookie_name, 'true', max_age=expires_after)
    

def get_has_been_seen(request):
    """Return ``True`` if the request has the ``has_been_seen_before`` cookie.
      
          >>> from mock import Mock
          >>> mock_request = Mock()
      
      False if the request doesn't have the cookie::
      
          >>> mock_request.cookies = {}
          >>> get_has_been_seen(mock_request)
          False
      
      True if the request does::
      
          >>> mock_request.cookies = {'has_been_seen_before': 'true'}
          >>> get_has_been_seen(mock_request)
          True
      
    """
    
    return bool(request.cookies.get('has_been_seen_before', False))

