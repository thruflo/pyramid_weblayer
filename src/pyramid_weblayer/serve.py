# -*- coding: utf-8 -*-

"""Provide a convienience method to serve a static file from an
  asset specification::
  
      # E.g. in a view callable
      return request.serve_spec('mypkg:foo/bar.js')
      
"""

import logging
logger = logging.getLogger(__name__)

from pyramid.httpexceptions import HTTPNotFound
from pyramid.path import AssetResolver
from pyramid.response import FileResponse

def get_serve_spec(request, resolver_cls=None, response_cls=None, not_found=None):
    """Return a function that serves an asset specification as a static file."""
    
    # Compose.
    if resolver_cls is None:
        resolver_cls = AssetResolver
    if response_cls is None:
        response_cls = FileResponse
    if not_found is None:
        not_found = HTTPNotFound
    
    # Prepare.
    not_found_msg = u'The static file could not be found.'
    
    # Return the serving function.
    def serve(spec, package=None):
        """Resolve the asset ``spec`` to a file path and return a static
          file response that serves it. If the file isn't found, return
          a 404.
        """
        
        # Resolve the spec to a file path.
        resolver = resolver_cls(package)
        descriptor = resolver.resolve(spec)
        path = descriptor.abspath()
        
        # Serve the file.
        try:
            return response_cls(path, request=request)
        except OSError as err:
            return not_found(explanation=not_found_msg)
    
    return serve

