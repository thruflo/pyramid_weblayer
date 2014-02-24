#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides a ``validate_against_csrf`` ``pyramid.events.ContextFound`` subscriber
  that uses a ``CSRFValidator`` utility to validate incoming requests against
  cross site request forgeries.
"""

__all__ = [
    'CSRFError',
    'CSRFValidator',
    'METHODS_WITH_SIDE_EFFECTS',
    'validate_against_csrf',
    'validate_authenticated_xhr',
]

import logging
logger = logging.getLogger(__name__)

from pyramid.httpexceptions import HTTPUnauthorized
from pyramid_layout.panel import panel_config

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
        if request.is_xhr:
            default_value = request.headers.get('X-CSRFToken', None)
        else:
            default_value = None
        token_value = request.params.get('_csrf', default_value)
        if token_value is None or token_value != self._session_token:
            raise CSRFError
    


def validate_against_csrf(event, validator_cls=None):
    """Event subscriber that uses the session to validate incoming requests."""
    
    # Compose.
    if validator_cls is None:
        validator_cls = CSRFValidator
    
    # Unpack.
    request = event.request
    settings = request.registry.settings
    
    # Only validate if enabled.
    if not settings.get('csrf.validate', True):
        return
    
    # Ignore specified routes.
    matched_route = request.matched_route
    ignore_routes = settings.get('csrf.ignore_routes', None)
    if matched_route and ignore_routes:
        if matched_route.name in ignore_routes.split():
            return
    
    # Ignore specified paths.
    ignore_paths = settings.get('csrf.ignore_paths', None)
    if ignore_paths:
        for path in ignore_paths.split():
            if request.path.startswith(path):
                return
    
    session_token = request.session.get_csrf_token()
    csrf_validator = validator_cls(session_token)
    try:
        csrf_validator.validate(request)
    except CSRFError:
        raise HTTPUnauthorized

def validate_authenticated_xhr(event, validate=None):
    """Event subscriber that uses the session to validate authenticated XHR
      requests against Cross Site Request Forgery.
      
      The point being to allow an API to validate cookie authenticated XHR
      requests, as per https://www.djangoproject.com/weblog/2011/feb/08/security/
      While still allowing the API to be accessed without CSRF protection for
      non-XHR usage, e.g.: in tests or via alternative authentication.
    """
    
    # Compose.
    if validate is None:
        validate = validate_against_csrf
    
    request = event.request
    if request.is_xhr and request.is_authenticated:
        validate(event)


@panel_config('csrf-ajax-setup',
        renderer='pyramid_weblayer:templates/csrf_ajax_setup.mako')
def csrf_ajax_setup_panel(context, request):
    """Pass the current CSRF token and target methods to the panel template."""
    
    return {
        'token': request.session.get_csrf_token(), 
        'methods': [item.upper() for item in METHODS_WITH_SIDE_EFFECTS]
    }

