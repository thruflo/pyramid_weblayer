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
      
      Returns the string ``'active'`` if True, otherwise returns an empty string::
          
          >>> nav = ActiveNavigationAdapter(mock_request)
          >>> nav.is_active('/foo')
          'active'
          >>> nav.is_active('/foo/baz')
          ''
      
      The idea being that the return value can be used in a html element's class
      attribute::
      
          <li class="nav-item ${is_active('/foo')}">
            <a href="/foo">Foo</a>
          </li>
      
      Can accept multiple (OR) paths::
      
          >>> nav.is_active('/foo/baz', '/flobble', '/bar')
          ''
          >>> nav.is_active('/foo/baz', '/foo')
          'active'
          >>> nav.is_active('/foo', '/foo/baz')
          'active'
      
      Special cases '/' to require an exact match::
      
          >>> nav.is_active('/')
          ''
          >>> mock_request.path = '/'
          >>> nav = ActiveNavigationAdapter(mock_request)
          >>> nav.is_active('/')
          'active'
      
    """
    
    def __init__(self, request):
        self.request = request
    
    def is_active(self, *args, **kwargs):
        exact = kwargs.get('exact')
        for path in args:
            if exact is None:
                exact = path == '/'
            active = False
            if exact:
                active = self.request.path == path
            else:
                active = self.request.path.startswith(path)
            if active:
                return 'active'
        return ''
    


def add_is_active_function(event, adapter_cls=None):
    """Add the ``is_active`` function to the template global namespace.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_adapter_cls = Mock()
          >>> mock_adapter = Mock()
          >>> mock_adapter.is_active.return_value = True
          >>> mock_adapter_cls.return_value = mock_adapter
          >>> event = {'request': None}
      
      Adds ``as_active`` to the event namespace::
      
          >>> add_is_active_function(event, adapter_cls=mock_adapter_cls)
          >>> is_active = event['is_active']
          >>> is_active('/')
          True
          >>> mock_adapter.is_active.assert_called_with('/')
      
    """
    
    if adapter_cls is None:
        adapter_cls = ActiveNavigationAdapter
    
    nav = adapter_cls(event['request'])
    event['is_active'] = nav.is_active

