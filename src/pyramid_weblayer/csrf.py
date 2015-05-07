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
    'validate_session_authenticated',
]

import logging
logger = logging.getLogger(__name__)

from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import unauthenticated_userid
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
        header_value = request.headers.get('X-CSRFToken', None)
        token_value = request.params.get('_csrf', header_value)
        if token_value is None or token_value != self._session_token:
            raise CSRFError
    


def validate_against_csrf(event, validator_cls=None):
    """Event subscriber that uses the session to validate incoming requests."""
    
    # logger.warn(('validate_against_csrf', event))

    # Compose.
    if validator_cls is None:
        validator_cls = CSRFValidator
    
    # Unpack.
    request = event.request
    settings = request.registry.settings
    
    # logger.warn('A')

    # Only validate if enabled.
    if not settings.get('csrf.validate', True):
        return
    
    # logger.warn('B')
    
    # Ignore specified routes.
    matched_route = request.matched_route
    ignore_routes = settings.get('csrf.ignore_routes', None)
    if matched_route and ignore_routes:
        if matched_route.name in ignore_routes.split():
            return
    
    # logger.warn('C')
    
    # Ignore specified paths.
    ignore_paths = settings.get('csrf.ignore_paths', None)
    if ignore_paths:
        for path in ignore_paths.split():
            if request.path.startswith(path):
                return
    
    # logger.warn('D')
    
    session_token = request.session.get_csrf_token()
    csrf_validator = validator_cls(session_token)
    
    # logger.warn(('session_token', session_token))

    try:
        csrf_validator.validate(request)
    except CSRFError:
        # logger.warn('RAISING 401')
        raise HTTPUnauthorized

def validate_session_authenticated(event, unauth_userid=None, validate=None):
    """Event subscriber that validates *session authenticated* requests
      against Cross Site Request Forgery.
    """

    # logger.warn(('csrf.validate_session_authenticated', event))

    # Compose.
    if unauth_userid is None:
        unauth_userid = unauthenticated_userid
    if validate is None:
        validate = validate_against_csrf
    
    # Unpack.
    request = event.request
    registry = request.registry
    
    # Start by making CSRF validation the default. This protects against
    # exposure to having coded against the internal implementation detail
    # noted below -- if something changes and this logic breaks, we'll
    # hopefully deny requests we should allow, rather than allowing requests
    # we should deny.
    should_validate = True
    
    # Determine whether to validate the request -- first checking that the
    # request *is* authenticated, then that we're not running tests,
    # then that it was authenticated using a policy that is (or is like)
    # the pyramid ``SessionAuthenticationPolicy``.
    if not request.is_authenticated:
        # logger.warn(('not authenticated'))
        should_validate = False
    elif request.environ.get('paste.testing'):
        # logger.warn(('testing'))
        should_validate = False
    else: # XXX this next logic is coded against an internal implementation
        # detail of the ``SessionAuthenticationPolicy``.
        policy = registry.queryUtility(IAuthenticationPolicy)
        key = getattr(policy, 'userid_key', None)
        session_value = key and request.session.get(key) or None
        principal_id = unauth_userid(request)
        # We know that the principal_id exists as the request is authenticated,
        # so checking that the session_value equals it also checks that the
        # session value is not None.
        # logger.warn(('session_value == principal_id', session_value == principal_id))
        should_validate = session_value == principal_id
    # logger.warn(('should_validate', should_validate))
    if should_validate:
        validate(event)


@panel_config('csrf-ajax-setup',
        renderer='pyramid_weblayer:templates/csrf_ajax_setup.mako')
def csrf_ajax_setup_panel(context, request):
    """Pass the current CSRF token and target methods to the panel template."""
    
    return {
        'token': request.session.get_csrf_token(), 
        'methods': [item.upper() for item in METHODS_WITH_SIDE_EFFECTS]
    }

