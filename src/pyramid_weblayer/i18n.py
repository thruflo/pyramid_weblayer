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

from pyramid.i18n import get_localizer, TranslationStringFactory

def add_underscore_translation(event):
    """Add i18n support to the template global namespace.
      
      setUp::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_request.translate.return_value = 'manger de tout'
          >>> event = {'request': mock_request}
      
      Example usage::
      
          >>> add_underscore_translation(event)
          >>> translate = event['_']
          >>> translate('eat everything')
          'manger de tout'
      
    """
    
    request = event['request']
    event['_'] = request.translate
    event['localizer'] = request.localizer


class TranslationAdapter(object):
    """Adapt a ``request`` to provide ``self.translate(message_string)``, e.g.::
    
      setUp::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_request.localizer.translate.return_value = 'manger de tout'
      
      Example usage::
          
          >>> translator = TranslationAdapter(mock_request)
          >>> translator.translate('eat everything')
          'manger de tout'
      
    """
    
    def __init__(self, request, domain=None):
        self._localizer = get_localizer(request)
        self._factory = TranslationStringFactory(domain)
    
    def translate(self, message_string):
        return self._localizer.translate(self._factory(message_string))
    

