# -*- coding: utf-8 -*-

"""Provides ``torque.HookDispatcher`` a simple client to dispatch tasks to
  the `Torque <http://ntorque.com>`_ web hook task queue.
"""

__all__ = [
    'HookDispatcher',
]

import logging
logger = logging.getLogger(__name__)

import requests

from os.path import join as join_path
from urllib import basejoin as join_url
from urllib import urlencode

from pyramid_weblayer import tx

class HookDispatcher(object):
    """Very basic wrapper around the ``requests`` lib."""
    
    def __init__(self, request, **kwargs):
        self.request = request
        self.post = kwargs.get('post', requests.post)
        self.call_in_bg = kwargs.get('call_in_bg', tx.call_in_background)
    
    def __call__(self, hook_path, data=None, headers={}, **kwargs):
        """Patch the api key into a POST request to the url."""
        
        # Unpack.
        request = self.request
        settings = request.registry.settings
        torque_url = settings.get('torque.url')
        torque_api_key = settings.get('torque.api_key')
        webhooks_url = settings.get('fabbed.hooks.url')
        webhooks_api_key = settings.get('fabbed.hooks.api_key')
        
        # Build the hook url.
        if '://' in webhooks_url:
            hook_url = join_url(webhooks_url, hook_path)
        else:
            hook_url = join_url(request.application_url, join_path(webhooks_url,
                    hook_path))
        
        # If we're in development, then skip the torque queue and just call
        # the hook directly.
        if settings.get('mode') == 'development':
            headers['FABBED_HOOKS_API_KEY'] = webhooks_api_key
            url = hook_url
        else:
            headers['TORQUE_API_KEY'] = torque_api_key
            headers['TORQUE-PASSTHROUGH-FABBED_HOOKS_API_KEY'] = webhooks_api_key
            divider = '&' if '?' in torque_url else '?'
            encoded_param = urlencode({'url': hook_url})
            url = ''.join([torque_url, divider, encoded_param])
        
        # Then, as long as we're not ftesting, post to the web hook and verify
        # the response is 200 or 201.
        should_do_post = not request.environ.get('paste.testing', False)
        if should_do_post:
            # XXX n.b.: we call after the current tx because otherwise our
            # hook executes before the data is committed! This may or may
            # not be necessary when we use an async queue.
            # The consequence is that we lose the ability to check the
            # "has it enqueued" status of the post response.
            post = lambda: self.post(url, data=data, headers=headers, **kwargs)
            self.call_in_bg(post)
        
        # Return where we dispatched to.
        return {
            hook_path: {
                'status': 'DISPATCHED', 
                'url': url
            }
        }
    

