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

from pyga.entities import Event
from pyga.entities import Page
from pyga.entities import Session
from pyga.entities import Visitor
from pyga.requests import Tracker

from .tx import call_in_background

class PyGAFactory(object):
    """Shared boilerplate to get configured ``tracker, session, visitor``
      instances from the current request::
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_request.registry.settings = {'gae.tracking_id': '...'}
          >>> mock_request.session = {}
          >>> mock_session_cls = Mock()
          >>> mock_tracker_cls = Mock()
          >>> mock_visitor_cls = Mock()
          >>> mock_kwargs = dict(session_cls=mock_session_cls,
          ...         tracker_cls=mock_tracker_cls, visitor_cls=mock_visitor_cls)
      
      Test::
      
          >>> factory = PyGAFactory(**mock_kwargs)
          >>> tracker, session, visitor = factory(mock_request)
          >>> assert tracker is mock_tracker_cls.return_value
          >>> assert session is mock_session_cls.return_value
          >>> assert visitor is mock_visitor_cls.return_value
      
    """
    
    def __call__(self, request):
        """Instantiate and return pyga ``tracker, session, visitor`` instances."""
        
        # Prepare the tracking id, session id and utm cookies.
        settings = request.registry.settings
        gae_tracking_id = settings['gae.tracking_id']
        if not 'gae_session_id' in request.session:
            request.session['gae_session_id'] = self.session_cls.generate_session_id()
        gae_session_id = request.session['gae_session_id']
        utma_cookie = request.cookies.get('__utma', None)
        utmb_cookie = request.cookies.get('__utmb', None)
        
        # Instantiate the tracker, session and visitor.
        tracker = self.tracker_cls(gae_tracking_id, request.host)
        session = self.session_cls()
        session.session_id = gae_session_id
        if utmb_cookie:
            session.extract_from_utmb(utmb_cookie)
        visitor = self.visitor_cls()
        visitor.extract_from_server_meta(request.environ)
        if utma_cookie:
            visitor.extract_from_utma(utma_cookie)
        
        # Return the tuple.
        return tracker, session, visitor
    
    def __init__(self, session_cls=None, tracker_cls=None, visitor_cls=None):
        """Initialise with the dependencies provided."""
        
        # Compose.
        if session_cls is None: #pragma: no cover
            session_cls = Session
        if tracker_cls is None: #pragma: no cover
            tracker_cls = Tracker
        if visitor_cls is None: #pragma: no cover
            visitor_cls = Visitor
        
        # Assign.
        self.session_cls = session_cls
        self.tracker_cls = tracker_cls
        self.visitor_cls = visitor_cls
    


def get_track_event(request, call_in_bg=None, event_cls=None, factory_cls=None):
    """Return a request method that uses the pyga library to track a custom
      event with google analytics.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_call_in_bg = Mock()
          >>> mock_event_cls = Mock()
          >>> mock_event_cls.return_value = '<event>'
          >>> mock_factory_cls = Mock()
          >>> mock_factory = Mock()
          >>> mock_tracker = Mock()
          >>> mock_factory.return_value = (mock_tracker, '<session>', '<visitor>')
          >>> mock_factory_cls.return_value = mock_factory
          >>> mock_request = Mock()
          >>> track_event = get_track_event(mock_request,
          ...         call_in_bg=mock_call_in_bg, event_cls=mock_event_cls,
          ...         factory_cls=mock_factory_cls)
      
      Tracks the event::
      
          >>> return_value = track_event('cat', 'act')
          >>> args = ('<event>', '<session>', '<visitor>')
          >>> mock_call_in_bg.assert_called_with(mock_tracker.track_event, args=args)
      
      Unless in development::
      
          >>> mock_request.registry.settings = {'mode': 'development'}
          >>> mock_call_in_bg = Mock()
          >>> track_event = get_track_event(mock_request,
          ...         call_in_bg=mock_call_in_bg, event_cls=mock_event_cls,
          ...         factory_cls=mock_factory_cls)
          >>> return_value = track_event('cat', 'act')
          >>> assert not mock_call_in_bg.called
      
    """
    
    # Compose.
    if call_in_bg is None: #pragma: no cover
        call_in_bg = call_in_background
    if event_cls is None: #pragma: no cover
        event_cls = Event
    if factory_cls is None: #pragma: no cover
        factory_cls = PyGAFactory
    
    def track_event(category, action, label=None, value=None, noninteraction=False):
        """Join a call to ping google analytics with the given event in a background thread
          to the current transaction.
        """
        
        # Exit if in development.
        settings = request.registry.settings
        if settings.get('mode', None) == 'development':
            return
        
        # Instantiate configured pyga ``tracker``, ``session`` and ``visitor``s.
        factory = factory_cls()
        tracker, session, visitor = factory(request)
        
        # Create the event to track.
        event = event_cls(category=category, action=action, label=label,
                value=value, noninteraction=noninteraction)
        
        # Join a background call to track the event to the current transaction.
        return call_in_bg(tracker.track_event, args=(event, session, visitor))
    
    return track_event

def get_track_page(request, call_in_bg=None, page_cls=None, factory_cls=None):
    """Return a request method that uses the pyga library to track a page view
      (or a virtual page view) with google analytics.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_call_in_bg = Mock()
          >>> mock_page_cls = Mock()
          >>> mock_page_cls.return_value = '<page>'
          >>> mock_factory_cls = Mock()
          >>> mock_factory = Mock()
          >>> mock_tracker = Mock()
          >>> mock_factory.return_value = (mock_tracker, '<session>', '<visitor>')
          >>> mock_factory_cls.return_value = mock_factory
          >>> mock_request = Mock()
          >>> track_page = get_track_page(mock_request,
          ...         call_in_bg=mock_call_in_bg, page_cls=mock_page_cls,
          ...         factory_cls=mock_factory_cls)
      
      Tracks the page view::
      
          >>> return_value = track_page('/foo?baz=bar')
          >>> mock_page_cls.assert_called_with('/foo?baz=bar')
          >>> args = ('<page>', '<session>', '<visitor>')
          >>> mock_call_in_bg.assert_called_with(mock_tracker.track_pageview, args=args)
      
      Unless in development::
      
          >>> mock_request.registry.settings = {'mode': 'development'}
          >>> mock_call_in_bg = Mock()
          >>> track_page = get_track_page(mock_request,
          ...         call_in_bg=mock_call_in_bg, page_cls=mock_page_cls,
          ...         factory_cls=mock_factory_cls)
          >>> return_value = track_page('/foo?baz=bar')
          >>> assert not mock_call_in_bg.called
      
    """
    
    # Compose.
    if call_in_bg is None: #pragma: no cover
        call_in_bg = call_in_background
    if page_cls is None: #pragma: no cover
        page_cls = Page
    if factory_cls is None: #pragma: no cover
        factory_cls = PyGAFactory
    
    def track_page(path):
        """Join a call to ping google analytics with the given event in a background thread
          to the current transaction.
        """
        
        # Exit if in development.
        settings = request.registry.settings
        if settings.get('mode', None) == 'development':
            return
        
        # Instantiate configured pyga ``tracker``, ``session`` and ``visitor``s.
        factory = factory_cls()
        tracker, session, visitor = factory(request)
        
        # Create the page to track.
        page = page_cls(path)
        
        # Join a background call to track the event to the current transaction.
        return call_in_bg(tracker.track_pageview, args=(page, session, visitor))
    
    return track_page

