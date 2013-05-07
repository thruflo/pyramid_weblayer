# -*- coding: utf-8 -*-

"""Provide a convienience method to serve a static file from an
  asset specification::
  
      # E.g. in a view callable
      return request.serve_spec('mypkg:foo/bar.js')
  
  Note that the implementation gets the file using its static url, so
  this is only really useful as a way to *obfuscate* the actual url
  that a file is downloaded from, i.e.: if you want to proxy a
  download so as not to expose the actual url to the file.
  
  Note also that this obfuscation is only itself useful if the downloaded
  file is served over HTTPS and has an unguessable file path.
"""

import logging
logger = logging.getLogger(__name__)

import mimetypes
import requests as requests_lib
from cStringIO import StringIO

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import FileIter
from pyramid.response import Response

def get_serve_spec(request, requests=None, buf_cls=None, iter_cls=None,
        response_cls=None, not_found=None):
    """Return a function that serves an asset specification as a static file."""
    
    # Compose.
    if requests is None:
        requests = requests_lib
    if buf_cls is None:
        buf_cls = StringIO
    if iter_cls is None:
        iter_cls = FileIter
    if response_cls is None:
        response_cls = Response
    if not_found is None:
        not_found = HTTPNotFound
    
    # Prepare.
    not_found_msg = u'The static file could not be found.'
    err_message = u'There was a problem downloading the file. Try again later.'
    
    # Return the serving function.
    def serve(spec):
        """Resolve the asset ``spec`` to a file path and return a static
          file response that serves it. If the file isn't found, return
          a 404.
        """
        
        # Resolve the spec to a url.
        url = request.static_url(spec)
        if url.startswith('//'):
            url = 'https:' + url
        
        # Download the url.
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            msg = not_found_msg if r.status_code == 404 else err_message
            return not_found(explanation=msg)
        
        # Return the file response.
        filename = spec.split('/')[-1]
        disposition = 'attachment; filename="{0}"'.format(filename)
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        response = Response(content_type=mime_type)
        response.headers['Content-Disposition'] = disposition
        response.body = r.content
        return response
    
    
    return serve

