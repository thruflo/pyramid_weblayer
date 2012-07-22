# -*- coding: utf-8 -*-

"""Provide ``get_session_id`` function."""

import logging
logger = logging.getLogger(__name__)

from .utils import generate_random_digest

def get_session_id(request, key='session_id', gen_digest=None):
    """Make sure there's a ``session_id`` in ``request.session`` and return it.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_gen_digest = Mock()
          >>> mock_gen_digest.return_value = '<digest>'
      
      If there's no existing id in the session, then generate, store and return::
      
          >>> mock_request.session = {}
          >>> get_session_id(mock_request, key='k', gen_digest=mock_gen_digest)
          '<digest>'
          >>> mock_request.session['k'] = '<digest>'
      
      Otherwise return the xisting value::
      
          >>> mock_request.session = {'k': '<existing>'}
          >>> get_session_id(mock_request, key='k')
          '<existing>'
      
    """
    
    # Test jig.
    if gen_digest is None:
        gen_digest = generate_random_digest
    
    digest = request.session.get(key)
    if not digest:
        digest = gen_digest()
        request.session[key] = digest
    return digest

