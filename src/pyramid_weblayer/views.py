# -*- coding: utf-8 -*-

"""Views for ``/favicon.ico`` and ``/robots.txt``."""

import logging
logger = logging.getLogger(__name__)

from pkg_resources import resource_filename

from pyramid.response import FileResponse
from pyramid.security import NO_PERMISSION_REQUIRED as PUBLIC
from pyramid.static import resolve_asset_spec
from pyramid.view import view_config

FAVICON_SPEC = 'pyramid_weblayer:favicon.ico'
ROBOTS_SPEC = 'pyramid_weblayer:robots.txt'

ONE_DAY = 60 * 60 * 24 * 7

def get_absolute_path(spec, resolve=None, filename=None):
    """Turns an asset ``spec`` into an absolute path.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_filename = Mock()
          >>> mock_filename.return_value = '/var/mypkg/assets/favicon.ico'
      
      Resolves ``spec`` into parts and passes to ``resource_filename``::
      
          >>> get_absolute_path('mypkg:assets/favicon.ico', filename=mock_filename)
          '/var/mypkg/assets/favicon.ico'
          >>> mock_filename.assert_called_with('mypkg', 'assets/favicon.ico')
      
    """
    
    if resolve is None: # pragma: no cover
        resolve = resolve_asset_spec
    if filename is None: # pragma: no cover
        filename = resource_filename
    
    return filename(*resolve(spec))

def serve_file(request, spec, cache_max_age=None, get_path=None, response_cls=None):
    """Serve the ``spec``d file.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_get_path = Mock()
          >>> mock_get_path.return_value = '/var/foo.txt'
          >>> mock_response_cls = Mock()
          >>> mock_response_cls.return_value = '<response: /var/foo.txt>'
          >>> kwargs = dict(get_path=mock_get_path, response_cls=mock_response_cls)
      
      Gets the absolute path for the ``spec`` and returns the static file
      response::
      
          >>> serve_file('req', 'pkg:foo.txt', **kwargs)
          '<response: /var/foo.txt>'
          >>> mock_get_path.assert_called_with('pkg:foo.txt')
          >>> mock_response_cls.assert_called_with('/var/foo.txt', request='req',
          ...        cache_max_age=ONE_DAY)
      
    """
    
    if cache_max_age is None:
        cache_max_age = ONE_DAY
    if get_path is None: # pragma: no cover
        get_path = get_absolute_path
    if response_cls is None: # pragma: no cover
        response_cls = FileResponse
    
    path = get_path(spec)
    return response_cls(path, request=request, cache_max_age=cache_max_age)


@view_config(route_name='favicon_ico', permission=PUBLIC)
def favicon_view(request, spec=None, serve=None):
    """Serve the ``favicon.ico`` file.
      
          >>> from mock import Mock
          >>> mock_serve = Mock()
          >>> mock_serve.return_value = 'static file response'
          >>> favicon_view('req', serve=mock_serve)
          'static file response'
          >>> mock_serve.assert_called_with('req', FAVICON_SPEC)
      
    """
    
    if spec is None:
        spec = FAVICON_SPEC
    if serve is None: # pragma: no cover
        serve = serve_file
    
    return serve(request, spec)


@view_config(route_name='robots_txt', permission=PUBLIC)
def robots_view(request, spec=None, serve=None):
    """Serve the ``robots.txt`` file.
      
          >>> from mock import Mock
          >>> mock_serve = Mock()
          >>> mock_serve.return_value = 'static file response'
          >>> robots_view('req', serve=mock_serve)
          'static file response'
          >>> mock_serve.assert_called_with('req', ROBOTS_SPEC)
      
    """
    
    if spec is None:
        spec = ROBOTS_SPEC
    if serve is None: # pragma: no cover
        serve = serve_file
    
    return serve(request, spec)

