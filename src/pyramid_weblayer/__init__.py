#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyramid.events import BeforeRender

from .i18n import add_underscore_translation

def includeme(config):
    """Allow developers to use ``config.include('pyramid_weblayer')`` to register
      the ``add_underscore_translation`` subscriber::
      
      setUp::
      
          >>> from mock import Mock
          >>> mock_config = Mock()
      
      test::
      
          >>> includeme(mock_config)
          >>> mock_config.add_subscriber.assert_called_with(
          ...    add_underscore_translation,
          ...    BeforeRender
          ... )
      
    """
    
    config.add_subscriber(add_underscore_translation, BeforeRender)

