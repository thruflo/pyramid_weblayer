#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides ``BaseView``, a base class for a Pyramid view callable."""

from pyramid.httpexceptions import HTTPNotFound, HTTPUnauthorized

from .csrf import CSRFError, CSRFValidator
from .method import MethodSelector

class BaseView(object):
    """A base class to use as a view callable.  Protects against CSRF attacks
      and uses a `.method.MethodSelector` to get the appropriate method to
      handle the request with, based on the request's HTTP method.
      
      In practise, this allows you to expose a class to a particular
      route and skip the step of configuring ``def get(self)`` to handle
      GET requests: if the class has a ``get`` method and a GET request is
      routed to it, the ``get`` method will be called to handle the request.
      
      This means you can write code like::
      
          @view_config(route_name='foo')
          class FooView(BaseView):
              def get(self):
                  tmpl = '<form method="post"><input type="submit" /></form>'
                  return Response(tmpl)
              
              def post(self):
                  return Response('Handling a POST')
              
      
    """
    
    # Subclasses can set this to ``False`` to skip XSRF validation
    # on a view callable by view callable basis, as well as configuring
    # ``check_csrf`` in the application settings.
    check_csrf = True
    
    def __init__(self, request, Selector=MethodSelector, Validator=CSRFValidator):
        self.request = request
        self._MethodSelector = Selector
        self._CSRFValidator = Validator
    
    def __call__(self, *args, **kwargs):
        view_callable = self._MethodSelector(self).select(self.request.method)
        if view_callable is None:
            raise HTTPNotFound
        else:
            settings = self.request.registry.settings
            if self.check_csrf and settings.get('check_csrf', True):
                session_token = self.request.session.get_csrf_token()
                validator = self._CSRFValidator(session_token)
                try:
                    validator.validate(self.request)
                except CSRFError:
                    raise HTTPUnauthorized
        return view_callable(*args, **kwargs)
    
