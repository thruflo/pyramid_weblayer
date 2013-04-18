# -*- coding: utf-8 -*-

"""Utility functions to flatten strings and a template before render hook."""

__all__ = [
    'add_flat_string',
    'as_flat_string',
    'flatten_breadcrumb'
]

import logging
logger = logging.getLogger(__name__)

import html2text

def as_flat_string(markup, to_string=None):
    """Convert html to text and replace all whitespace with single spaces."""
    
    # Compose.
    if to_string is None:
        handler = html2text.HTML2Text()
        handler.ignore_links = True
        handler.ignore_images = True
        to_string = handler.handle
    
    if not markup:
        return markup
    
    s = to_string(markup)
    return u' '.join(s.split()).strip()

def flatten_breadcrumb(markup, to_string=None):
    """Convert html to text and replace bullets and ``/``s."""
    
    # Compose.
    if to_string is None:
        to_string = as_flat_string
    
    if not markup:
        return markup
    
    s = as_flat_string(markup)
    s = s.replace('* ', '').replace('/', '-')
    return s

def add_flatten_functions(event, flat_string=None, flatten_crumb=None):
    """Add ``flat_string`` & ``flatten_breadcrumb`` to the tempate namespace."""
    
    if flat_string is None:
        flat_string = as_flat_string
    if flatten_crumb is None:
        flatten_crumb = flatten_breadcrumb
    
    event['flat_string'] = flat_string
    event['flatten_breadcrumb'] = flatten_breadcrumb

