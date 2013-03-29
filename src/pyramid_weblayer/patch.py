# -*- coding: utf-8 -*-

"""Library patches."""

import logging
logger = logging.getLogger(__name__)

import sys

from beaker import cache
from beaker.util import coerce_cache_params
from pyramid import mako_templating

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
                kwargs['cache_args'] = cache_args
            super(TemplateLookup, self).__init__(*args, **kwargs)
        
    
    return TemplateLookup


def patch_all(settings):
    """Run all the patches."""
    
    # Patch ``mako.lookup.TemplateLookup`` to be our ``TemplateLookup`` class.
    mako_templating.PkgResourceTemplateLookup = templateLookupFactory(settings)

