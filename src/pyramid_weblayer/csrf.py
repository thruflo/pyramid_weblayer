#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides ``CSRFValidator``, a utility to validate requests against cross
  site request forgeries by matching a request param with a session token::
  
      validator = CSRFValidator(session_token)
      try:
          validator.validate(request)
      except CSRFError:
          raise
  
"""

__all__ = [
    'CSRFError',
    'CSRFValidator'
]

METHODS_WITH_SIDE_EFFECTS = (
    'delete',
    'post', 
    'put',
)

class CSRFError(ValueError):
    """Raised when csrf validation fails."""


class CSRFValidator(object):
    """Validate a request against cross site request forgeries."""
    
    def __init__(self, session_token, target_methods=METHODS_WITH_SIDE_EFFECTS):
        self._session_token = session_token
        self._target_methods = target_methods
    
    def validate(self, request):
        if not request.method.lower() in self._target_methods:
            return
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return
        request_param = request.params.get('csrf_token', None)
        if request_param is None:
            raise CSRFError('`csrf_token` missing from %s' % request.method)
        if request_param != self._session_token:
            raise CSRFError('`csrf_token` param does not match session token.')
    
