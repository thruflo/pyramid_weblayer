# -*- coding: utf-8 -*-

"""Library patches."""

import logging
logger = logging.getLogger(__name__)

import sys

from beaker import cache
from beaker.util import coerce_cache_params
from pyramid import mako_templating

from mako.cache import register_plugin
from mako.lookup import TemplateLookup

try:
    from dogpile.cache import make_region
    from dogpile.cache.plugins.mako_cache import MakoPlugin
except ImportError:
    pass
else:
    class UnicodeKeyCapableMakoPlugin(MakoPlugin):
        """Override the plugin to handle unicode keys gracefully."""
        
        def get_and_replace(self, key, *args, **kw):
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            return MakoPlugin.get_and_replace(self, key, *args, **kw)

        def get_or_create(self, key, *args, **kw):
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            return MakoPlugin.get_or_create(self, key, *args, **kw)

        def put(self, key, *args, **kw):
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            return MakoPlugin.put(self, key, *args, **kw)

        def get(self, key, *args, **kw):
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            return MakoPlugin.get(self, key, *args, **kw)

        def invalidate(self, key, *args, **kw):
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            return MakoPlugin.invalidate(self, key, *args, **kw)
        
    

def coerge_dogpile_args(args):
    """Coerce INI settings into cache args with a ``default`` dogpile region.
      
      Requires args having at least:
      - url
      - type
      - expire
      
      XXX replace this as and when you actually want multiple regions.
    """
    
    # If the url isn't a list, make it so.
    url = args['url']
    if isinstance(url, basestring):
        url = [url]
    
    # Build the backend args.
    backend = args['type']
    backend_kwargs = {
        'url': [args['url']],
    }
    expiration_time = args['expire']
    
    # With optional auth.
    username = args.get('username', None)
    if username is not None:
        backend_kwargs['username'] = username
    password = args.get('password', None)
    if password is not None:
        backend_kwargs['password'] = password
    
    # Make the mako cache happy dogpile region.
    region = make_region().configure(
        backend,
        expiration_time=expiration_time,
        arguments=args
    )
    return {'regions': {'default': region}}

    
def templateLookupFactory(settings):
    """Use the ``settings`` to return a patched ``TemplateLookup`` class."""
    
    class TemplateLookup(mako_templating.PkgResourceTemplateLookup):
        """Sets ``cache_args`` if not passed into the lookup constructor."""
    
        def __init__(self, *args, **kwargs):
            """Patch ``kwargs['cache_args']``."""
            
            if not 'cache_args' in kwargs:
                # Read the ``cache.*`` ones into ``cache_args``.
                cache_args = {}
                prefix = 'mako.cache_args.'
                for key in settings.keys():
                    if key.startswith(prefix):
                        name = key.split(prefix)[1].strip()
                        value = settings[key]
                        try:
                            value = value.strip()
                        except AttributeError:
                            pass
                        cache_args[name] = value
                coerce_cache_params(cache_args)
                cache_args['timeout'] = cache_args.get('expire')
                if cache_args['type'].startswith('dogpile.cache'):
                    cache_args = coerge_dogpile_args(cache_args)
                    register_plugin("dogpile.cache",
                            "pyramid_weblayer.patch", "UnicodeKeyCapableMakoPlugin")
                    kwargs['cache_impl'] = 'dogpile.cache'
                kwargs['cache_args'] = cache_args
            super(TemplateLookup, self).__init__(*args, **kwargs)
        
    
    return TemplateLookup


def patch_all(settings):
    """Run all the patches."""
    
    # Patch ``mako.lookup.TemplateLookup`` to be our ``TemplateLookup`` class.
    mako_templating.PkgResourceTemplateLookup = templateLookupFactory(settings)

