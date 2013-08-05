#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyramid.events import BeforeRender, ContextFound, NewRequest, NewResponse
from pyramid.settings import asbool

from .campaign import get_campaign_url
from .csrf import validate_against_csrf
from .flash import get_joined_flash
from .flat import add_flatten_functions
from .hsts import hsts_redirect_to_https
from .hsts import set_hsts_header
from .hsts import secure_application_url
from .hsts import secure_resource_url
from .hsts import secure_route_url
from .i18n import add_underscore_translation
from .markdown import markdown_to_html
from .nav import add_is_active_function
from .seen import set_seen_cookie
from .seen import get_has_been_seen
from .serve import get_serve_spec
from .session import get_session_id
from .snip import add_snip_functions
from .track import get_track_event
from .track import get_track_page
from .utils import *

def includeme(config):
    """Allow developers to use ``config.include('pyramid_weblayer')`` to register
      the ``add_underscore_translation`` subscriber::
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_config = Mock()
          >>> includeme(mock_config)
      
      CSRF validation::
      
          >>> mock_config.add_subscriber.assert_any_call(validate_against_csrf, 
          ...         ContextFound)
      
      Provide `_` template namespace::
      
          >>> mock_config.add_subscriber.assert_any_call(add_underscore_translation,
          ...         BeforeRender)
          >>> mock_config.add_subscriber.assert_any_call(add_is_active_function,
          ...         BeforeRender)
      
      Add flatten and snip functions to template namespace::
      
          >>> mock_config.add_subscriber.assert_any_call(add_flatten_functions,
          ...         BeforeRender)
          >>> mock_config.add_subscriber.assert_any_call(add_snip_functions,
          ...         BeforeRender)
      
      Optionally force https::
      
          >>> mock_config.registry.settings = {'hsts.force_https': True}
          >>> includeme(mock_config)
          >>> mock_config.add_subscriber.assert_any_call(hsts_redirect_to_https, 
          ...         NewRequest)
          >>> mock_config.add_subscriber.assert_any_call(set_hsts_header, 
          ...         NewResponse)
          >>> mock_config.set_request_property.assert_any_call(secure_route_url,
          ...         'route_url', reify=True)
      
      Has been seen flag.::
      
          >>> mock_config.add_subscriber.assert_any_call(set_seen_cookie, 
          ...         NewResponse)
          >>> mock_config.set_request_property.assert_any_call(get_has_been_seen,
          ...         'has_been_seen', reify=True)
      
      Session ID::
      
          >>> mock_config.set_request_property.assert_any_call(get_session_id, 
          ...         'session_id', reify=True)
      
      Joined session flash::
      
          >>> mock_config.set_request_property.assert_any_call(get_joined_flash, 
          ...         'joined_flash', reify=True)
      
      Markdown rendering::
      
          >>> mock_config.set_request_property.assert_any_call(markdown_to_html, 
          ...         'markdown_to_html', reify=True)
      
      Track event::
      
          >>> mock_config.set_request_property.assert_any_call(get_track_event, 
          ...         'track_event', reify=True)
      
      
      Prereq routes::
      
          >>> mock_config.add_route.assert_any_call('favicon_ico', 'favicon.ico')
          >>> mock_config.add_route.assert_any_call('robots_txt', 'robots.txt')
      
      Scan::
      
          >>> mock_config.scan.assert_called_with('pyramid_weblayer')
      
    """
    
    # CSRF validation.
    config.add_subscriber(validate_against_csrf, ContextFound)
    
    # Provide `_` template namespace.
    config.add_subscriber(add_underscore_translation, BeforeRender)
    config.add_subscriber(add_is_active_function, BeforeRender)
    
    # Add snip and flatten functions to the template namespace.
    config.add_subscriber(add_flatten_functions, BeforeRender)
    config.add_subscriber(add_snip_functions, BeforeRender)
    
    # Optionally force https://
    settings = config.registry.settings
    should_force_https = asbool(settings.get('hsts.force_https', False))
    if should_force_https:
        config.add_subscriber(hsts_redirect_to_https, NewRequest)
        config.add_subscriber(set_hsts_header, NewResponse)
        config.set_request_property(secure_application_url, 'application_url',
                reify=True)
        config.set_request_property(secure_resource_url, 'resource_url',
                reify=True)
        config.set_request_property(secure_route_url, 'route_url', reify=True)
        config.add_tween('pyramid_weblayer.hsts.secure_redirect_tween')
    
    # Has been seen flag.
    config.add_subscriber(set_seen_cookie, NewResponse)
    config.set_request_property(get_has_been_seen, 'has_been_seen', reify=True)
    
    # Session id.
    config.set_request_property(get_session_id, 'session_id', reify=True)
    
    # Provide ``request.campaign_url``.
    config.set_request_property(get_campaign_url, 'campaign_url', reify=True)
    
    # Provide ``request.joined_flash``.
    config.set_request_property(get_joined_flash, 'joined_flash', reify=True)
    
    # Provide ``request.markdown_to_html``.
    config.set_request_property(markdown_to_html, 'markdown_to_html', reify=True)
    
    # Provide ``request.serve_spec``.
    config.set_request_property(get_serve_spec, 'serve_spec', reify=True)
    
    # Provide ``request.track_event``.
    config.set_request_property(get_track_event, 'track_event', reify=True)
    config.set_request_property(get_track_page, 'track_page', reify=True)
    
    # Favicon and robots.txt.
    config.add_route('favicon_ico', 'favicon.ico')
    config.add_route('robots_txt', 'robots.txt')
    config.scan('pyramid_weblayer')

