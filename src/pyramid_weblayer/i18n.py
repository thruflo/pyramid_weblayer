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
        self.localizer = get_localizer(request)
        self.factory = TranslationStringFactory(domain)
    
    def translate(self, message_string):
        return self.localizer.translate(self.factory(message_string))
    


def add_underscore_translation(event, Adapter=TranslationAdapter):
    """Add i18n support to the template global namespace.
      
      setUp::
      
          >>> from mock import Mock
          >>> MockAdapter = Mock()
          >>> mock_translator = Mock()
          >>> mock_translator.translate.return_value = 'manger de tout'
          >>> MockAdapter.return_value = mock_translator
          >>> event = {'request': None}
      
      Example usage::
      
          >>> add_underscore_translation(event, Adapter=MockAdapter)
          >>> translate = event['_']
          >>> translate('eat everything')
          'manger de tout'
      
    """
    
    translator = Adapter(event['request'])
    event['_'] = translator.translate
    event['localizer'] = translator.localizer


