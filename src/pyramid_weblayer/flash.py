# -*- coding: utf-8 -*-

"""Provide a ``request.joined_flash`` method which joins a call to
  ``request.session.flash`` to the current transaction.
"""

__all__ = [
    'get_joined_flash'
]

import logging
logger = logging.getLogger(__name__)

from .tx import join_to_transaction

def get_joined_flash(request, join=None):
    """Return the ``joined_flash`` request method."""
    
    # Compose.
    if join is None:
        join = join_to_transaction
    
    def joined_flash(*args, **kwargs):
        """Join a call to ``request.session.flash`` to the current transaction."""
        
        return join(request.session.flash, *args, **kwargs)
    
    return joined_flash

