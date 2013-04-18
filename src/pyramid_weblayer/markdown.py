# -*- coding: utf-8 -*-

"""Provides a function to render markdown as html."""

import logging
logger = logging.getLogger(__name__)

import markdown2

def markdown_to_html(request, to_html=None):
    """Return a function that renders markdown as html."""
    
    # Compose.
    if to_html is None:
        to_html = markdown2.markdown
    
    # If ``None`` return ''
    def render_as_html(markdown_str):
        """Render ``markdown_str`` as html."""
        
        # Coerce ``None`` to ``u''``.
        if markdown_str is None:
            markdown_str = u''
        
        return to_html(markdown_str)
    
    return render_as_html

