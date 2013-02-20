# -*- coding: utf-8 -*-

"""Utility functions to snip text at a certain length."""

import logging
logger = logging.getLogger(__name__)

import html2text

def snip_text(text, n=140):
    """Snip text at word boundary. Defaults to 140 characters.
      
          >>> text = u'lorum ipsum dolores. ' * 10
          >>> snip_text(text)
          u'lorum ipsum dolores. lorum ipsum dolores. lorum ipsum dolores. lorum ipsum dolores. lorum ipsum dolores. lorum ipsum dolores. lorum ipsum dolores. lorum ipsum \u2026'
          >>> snip_text(u'lorum ipsum dolores')
          u'lorum ipsum dolores'
          >>> snip_text(u'lorum ipsum dolores', n=8)
          u'lorum \u2026'
      
      Anything that evaluates to False comes out as an empty string::
      
          >>> snip_text(None)
          u''
      
    """
    
    if not text:
        return u''
    
    if len(text) < n:
        return text
    
    i = 0
    words = []
    for item in text.split():
        l = len(item)
        if i + l < n:
            words.append(item)
            i += l
        else:
            break
    return u'{0} …'.format(u' '.join(words))

def snip_html(html, n=140, handler=None, snip=None):
    """Snip html => raw text at word boundary.
      
          >>> html = 'Hello <em>is it me</em> you are looking for? ' * 10
          >>> snip_html(html)
          u'Hello _is it me_ you are looking for? Hello _is it me_ you are looking for? Hello _is it me_ you are looking for? Hello _is it me_ you are looking for? Hello _is it me_ you are \u2026'
          >>> snip_html(html, n=8)
          u'Hello \u2026'
      
    """
    
    # Test jig.
    if handler is None:
        handler = html2text.HTML2Text()
        handler.ignore_links = True
        handler.ignore_images = True
    if snip is None:
       snip = snip_text
    
    # Turn the html into plain text.
    text = handler.handle(html)
    
    # Run it through the snip text function.
    return snip(text, n=n)


def add_snip_functions(event):
    """Add ``snip_text`` and ``snip_html`` functions to the template namespace.
      
          >>> event = {}
          >>> add_snip_functions(event)
          >>> event['snip_text'] == snip_text
          True
          >>> event['snip_html'] == snip_html
          True
      
    """
    
    event['snip_text'] = snip_text
    event['snip_html'] = snip_html

