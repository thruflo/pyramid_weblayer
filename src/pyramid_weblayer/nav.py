#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides py:func`~pyramid_weblayer.nav.is_active`` function that determines
  whether a navigation item is active based on the request and path provided.
"""

import logging
logger = logging.getLogger(__name__)

class ActiveNavigationAdapter(object):
    """Adapt a ``request`` to provide ``self.is_active(path)``.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_request.path = '/foo/bar'
      
      Example usage::
          
          >>> nav = ActiveNavigationAdapter(mock_request)
          >>> nav.is_active('/foo')
          True
          >>> nav.is_active('/foo/baz')
          False
      
      Special cases '/' to require an exact match::
      
          >>> nav.is_active('/')
          False
      
          >>> mock_request.path = '/'
          >>> nav = ActiveNavigationAdapter(mock_request)
          >>> nav.is_active('/')
          True
      
    """
    
    def __init__(self, request):
        self.request = request
    
    def is_active(self, path, exact=None):
        if exact is None:
            exact = path == '/'
        active = False
        if exact:
            active = self.request.path == path
        else:
            active = self.request.path.startswith(path)
        return 'active' if active else ''
    


def add_is_active_function(event, adapter_cls=None):
    """Add the ``is_active`` function to the template global namespace.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_adapter_cls = Mock()
          >>> mock_adapter = Mock()
          >>> mock_adapter.is_active_return_value = True
          >>> mock_adapter_cls.return_value = mock_adapter
          >>> event = {'request': None}
      
      Adds ``as_active`` to the event namespace::
      
          >>> add_is_active_function(event, adapter_cls=mock_adapter_cls)
          >>> is_active = event['is_active']
          >>> is_active('/')
          True
          >>> mock_nav.is_active.assert_called_with('/')
      
    """
    
    if adapter_cls is None:
        adapter_cls = ActiveNavigationAdapter
    
    nav = adapter_cls(event['request'])
    event['is_active'] = nav.is_active

