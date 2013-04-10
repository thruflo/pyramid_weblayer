# -*- coding: utf-8 -*-

"""Provide a ``request.track_event(category, action, label=None, value=None)``
  method which fires the equivalent of a client side ``ga._trackEvent(...)``
  request to google analytics.
  
  The request is joined to the transaction and made in a background thread.
"""

__all__ = [
    'get_track_event'
]

import logging
logger = logging.getLogger(__name__)

import threading

from pyga.entities import Event, Session, Visitor
from pyga.requests import Tracker

from .tx import join_to_transaction

def get_track_event(request, join=None, event_cls=None, session_cls=None,
        thread_cls=None, tracker_cls=None, visitor_cls=None):
    """Return the ``joined_flash`` request method."""
    
    # Compose.
    if join is None:
        join = join_to_transaction
    if event_cls is None:
        event_cls = Event
    if session_cls is None:
        session_cls = Session
    if thread_cls is None:
        thread_cls = threading.Thread
    if tracker_cls is None:
        tracker_cls = Tracker
    if visitor_cls is None:
        visitor_cls = Visitor
    
    def track_event(category, action, label=None, value=None, noninteraction=False):
        """Join a call to ping google analytics with the given event in a background thread
          to the current transaction.
        """
        
        # Exit if in development.
        settings = request.registry.settings
        if settings.get('mode', None) == 'development':
            return
        
        # Prepare the tracking id, session id and utm cookies.
        gae_tracking_id = settings['gae.tracking_id']
        if not 'gae_session_id' in request.session:
            request.session['gae_session_id'] = session_cls.generate_session_id()
        gae_session_id = request.session['gae_session_id']
        utma_cookie = request.cookies.get('__utma', None)
        utmb_cookie = request.cookies.get('__utmb', None)
        
        # Instantiate the tracker, event, session and visitor.
        tracker = tracker_cls(gae_tracking_id, request.host)
        event = event_cls(category=category, action=action, label=label,
                value=value, noninteraction=noninteraction)
        session = session_cls()
        session.session_id = gae_session_id
        if utmb_cookie:
            session.extract_from_utmb(utmb_cookie)
        visitor = visitor_cls()
        visitor.extract_from_server_meta(request.environ)
        if utma_cookie:
            visitor.extract_from_utma(utma_cookie)
        
        # Join a background call to track the event to the current transaction.
        track_event = lambda: tracker.track_event(event, session, visitor)
        thread = thread_cls(target=track_event)
        return join(thread.start)
    
    return track_event

