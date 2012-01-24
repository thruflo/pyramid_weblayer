#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyramid.events import BeforeRender, NewRequest

from .csrf import validate_against_csrf
from .i18n import add_underscore_translation
from .utils import generate_hash

def includeme(config):
    """Allow developers to use ``config.include('pyramid_weblayer')`` to register
      the ``add_underscore_translation`` subscriber::
      
      setUp::
      
          >>> from mock import Mock
          >>> mock_config = Mock()
      
      test::
      
          >>> includeme(mock_config)
          >>> expected = (validate_against_csrf, NewRequest)
          >>> mock_config.add_subscriber.call_args_list[0][0] == expected 
          True
          >>> expected = (add_underscore_translation, BeforeRender)
          >>> mock_config.add_subscriber.call_args_list[1][0] == expected
          True
      
    """
    
    config.add_subscriber(validate_against_csrf, NewRequest)
    config.add_subscriber(add_underscore_translation, BeforeRender)
    

