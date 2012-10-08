#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides a request hook that can be used to generate a google analytics
 trackable route url.
"""

def get_campaign_url(request):
    """Returns a function that will generate a trackable campaign url."""
    
    def campaign_url(spec, source=u'', medium=u'', term=u'', content=u'', campaign=u'', **kwargs):
        """Encode the kwargs as query params"""
        
        # Either create a new query or extend the existing one.
        if '_query' in kwargs:
            query = kwargs.pop('_query')
        else:
            query = {}
        
        # Append the google analytics tracking params, if provided.
        if source:
            query['utm_source'] = source
        if medium:
            query['utm_medium'] = medium
        if term:
            query['utm_term'] = term
        if content:
            query['utm_content'] = content
        if campaign:
            query['utm_campaign'] = campaign
        return request.route_url(spec, _query=query, **kwargs)
    
    return campaign_url

