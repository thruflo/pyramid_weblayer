# -*- coding: utf-8 -*-

"""Provides a base `layout class`_ used to consolidate the api provided
  to templates.
  
  _`layout classes`: http://pyramid_layout.readthedocs.org
"""

__all__ = [
    'Layout'
]

import logging
logger = logging.getLogger(__name__)

from pyramid.security import has_permission

class Layout(object):
    """A simple base layout api implementation."""
    
    def has_permission(self, permission, context, has_perm=None):
        """Can the current request (i.e.: the authenticated user if any)
          ``permission`` the ``context``?
        """
        
        # Compose.
        if has_perm is None:
            has_perm = has_permission
        
        # Return the verdict.
        return has_perm(permission, context, self.request)
    
    def can_admin(self, context, has_perm=None):
        return self.has_permission('admin', context)
    
    def can_create(self, context, has_perm=None):
        return self.has_permission('create', context)
    
    def can_delete(self, context, has_perm=None):
        return self.has_permission('delete', context)
    
    def can_edit(self, context, has_perm=None):
        return self.has_permission('edit', context)
    
    def can_view(self, context, has_perm=None):
        return self.has_permission('view', context)
    
    def __init__(self, context, request):
        self.request = request
        self.context = request.context
        self.registry = request.registry
        self.settings = request.registry.settings
        self.home_url = request.application_url
    

