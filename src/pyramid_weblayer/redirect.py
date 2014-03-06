# -*- coding: utf-8 -*-

"""Provide ``request.redirect_to(location)``."""

import logging
logger = logging.getLogger(__name__)

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPMovedPermanently

def get_redirect_to(request, location, permanently=False, **kwargs):
    """Return a redirect response to the location provided."""
    
    # Compose.
    redirect_cls = HTTPMovedPermanently if permanently else HTTPFound
    return redirect_cls(location=location, **kwargs)

