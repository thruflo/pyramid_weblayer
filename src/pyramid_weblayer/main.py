# -*- coding: utf-8 -*-

"""Provides the ``main()`` WSGI application entry point."""

import logging
logger = logging.getLogger(__name__)

import os

from pyramid.config import Configurator

from pyramid_basemodel import Session
from pyramid_weblayer.patch import patch_all

def augment_settings(settings, env):
    """Use the ``env`` to augment the ``settings``."""
    
    # Extend the settings with the INI_* environment variables.
    for k, v in env.items():
        if k.startswith('INI_'):
            k = k[4:].replace('__', '.')
            settings[k] = v
    
    # Use the env `DATABASE_URL` as our `sqlalchemy.url`.
    if env.has_key('DATABASE_URL') or env.has_key('SHARED_DATABASE_URL'):
        settings['sqlalchemy.url'] = env.get('DATABASE_URL', 
                env.get('SHARED_DATABASE_URL'))
    
    # Use the memcache settings for the beaker backend.
    has_memcache = False
    memcache_stub = None
    for item in ('MEMCACHIER', 'MEMCACHE'):
        if env.has_key('{0}_SERVERS'.format(item)):
            has_memcache = True
            memcache_stub = item
            break
    if has_memcache:
        mc_username_key = '{0}_USERNAME'.format(memcache_stub)
        mc_password_key = '{0}_PASSWORD'.format(memcache_stub)
        mc_servers_key = '{0}_SERVERS'.format(memcache_stub)
        # Check the ``type`` config for the session and the template cache.
        # We want to set the url etc. for ext types.
        namespaces = []
        if settings['session.type'].startswith('ext:'):
            namespaces.append('session.')
        if settings['mako.cache_args.type'].startswith('ext:'):
            namespaces.append('mako.cache_args.')
        # Build the data to set.
        data = {'url': env[mc_servers_key]}
        if env.has_key(mc_username_key) and env.has_key(mc_password_key):
            data['username'] = env[mc_username_key]
            data['password'] = env[mc_password_key]
            data['protocol'] = 'binary'
        # Update the settings.
        for ns in namespaces:
            for k, v in data.items():
                settings['{0}{1}'.format(ns, k)] = v
    
    # Forcibly coerce all setting values that can be coerced to integers.
    for k, v in settings.items():
        try:
            settings[k] = int(v)
        except ValueError:
            pass
    
    # Return, augmented.
    return settings

def make_wsgi_app(root_factory, includeme, patch=None, bind=None, augment=None,
        env=None, configurator_cls=None, session=None, **settings):
    """Create and return a WSGI application."""
    
    # Compose.
    if augment is None: 
        augment = augment_settings
    if env is None:
        env = os.environ
    if configurator_cls is None:
        configurator_cls = Configurator
    if session is None:
        session = Session
    
    # If we should augment the settings with the environment variables, do so.
    if augment is not None:
        settings = augment(settings, env)
    
    # Now we have the settings, run the patches.
    if patch is not None:
        patch(settings)
    
    # Bind the db model.
    if bind is not None:
        bind()
    
    # Initialise a ``Configurator`` and apply the package configuration.
    config = configurator_cls(settings=settings, root_factory=root_factory)
    includeme(config)
    
    # Close the db connection for this thread.
    session.remove()
    
    # Return a WSGI app.
    return config.make_wsgi_app()

