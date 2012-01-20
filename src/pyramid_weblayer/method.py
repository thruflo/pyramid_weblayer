#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":py:mod:`pyramid_weblayer.method` provides :py:class:`MethodSelector`, which
  can be used to select a view class method to handle a ``request``, based on
  the request's method, e.g.::
  
      >>> class MockHandler(object):
      ...     def get(self):
      ...         pass
      ...     
      ...     def post(self):
      ...         pass
      ...     
      ... 
      >>> handler = MockHandler()
      >>> selector = MethodSelector(handler)
      >>> callable(selector.select('GET'))
      True
      >>> callable(selector.select('PUT'))
      False
  
"""

__all__ = [
    'MethodSelector'
]

RFC2616_HTTP_METHODS = (
    'connect',
    'delete',
    'get',
    'head',
    'options',
    'post',
    'put',
    'trace',
)

class MethodSelector(object):
    """Adapter that selects a method ``context`` using the ``method_name``."""
    
    def __init__(self, context, exposed_methods=RFC2616_HTTP_METHODS):
        self._context = context
        self._exposed_methods = exposed_methods
    
    def select(self, method_name):
        """Returns ``getattr(self.context, method_name)`` iff the method exists
          and is exposed.  Otherwise returns ``None``.
          
          Special cases HEAD requests to use GET, iff ``get`` exists and ``head``
          doesn't.  This allows applications to respond to HEAD requests without
          writing seperate head methods and takes advantage of the special case
          in ``webob.Response.__call__``::
          
              def __call__(self, environ, start_response):
                  # ... code removed for brevity
                  if environ['REQUEST_METHOD'] == 'HEAD':
                      # Special case here...
                      return EmptyResponse(self.app_iter)
                  return self.app_iter
              
          
        """
        
        if not hasattr(method_name, 'lower'):
            raise ValueError
        
        method_name = method_name.lower()
        if method_name in self._exposed_methods:
            method = getattr(self._context, method_name, None)
            if method_name == 'head' and method is None: # special case
                if 'get' in self._exposed_methods:
                    method = getattr(self._context, 'get', None)
            return method
    

