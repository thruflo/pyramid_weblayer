#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for `pyramid_weblayer.view`."""

import unittest

try: # pragma: no cover
    from mock import Mock
except: # pragma: no cover
    pass

class TestBaseView(unittest.TestCase):
    """Test the logic of py:class:`~pyramid_weblayer.view.BaseView`."""
    
    def makeOne(self, request, **kwargs):
        from pyramid_weblayer.view import BaseView
        return BaseView(request, **kwargs)
    
    def test_handles_request(self):
        """Handle a GET request by calling ``self.get()``."""
        
        mock_callable = Mock()
        mock_selector = Mock()
        mock_selector_factory = Mock()
        mock_selector_factory.return_value = mock_selector
        mock_selector.select.return_value = mock_callable
        mock_callable.return_value = 'view callable return value'
        
        base_view = self.makeOne(
            Mock(), 
            Selector=mock_selector_factory, 
            Validator=Mock()
        )
        self.assertTrue(base_view() == 'view callable return value')
    
    def test_raises_httpnotfound(self):
        """Raises ``HTTPNotFound`` if there isn't a view callable."""
        
        from pyramid.httpexceptions import HTTPNotFound
        
        mock_callable = Mock()
        mock_selector = Mock()
        mock_selector_factory = Mock()
        mock_selector_factory.return_value = mock_selector
        mock_selector.select.return_value = None
        
        base_view = self.makeOne(
            Mock(), 
            Selector=mock_selector_factory, 
            Validator=Mock()
        )
        self.assertRaises(
            HTTPNotFound,
            base_view
        )
    
    def test_validates_the_request(self):
        """Validates the request against CSRF attacks."""
        
        mock_request = Mock()
        mock_selector_factory = Mock()
        mock_validator = Mock()
        mock_validator_factory = Mock()
        mock_validator_factory.return_value = mock_validator
        base_view = self.makeOne(
            mock_request, 
            Selector=mock_selector_factory, 
            Validator=mock_validator_factory
        )
        retval = base_view()
        mock_validator.validate.assert_called_with(mock_request)
    
    def test_doesnt_validate_the_request(self):
        """Only validates the request against CSRF attacks if self.check_csrf
          and settings['check_csrf'] are both True.
        """
        
        mock_request = Mock()
        mock_selector_factory = Mock()
        mock_validator = Mock()
        mock_validator_factory = Mock()
        mock_validator_factory.return_value = mock_validator
        base_view = self.makeOne(
            mock_request, 
            Selector=mock_selector_factory, 
            Validator=mock_validator_factory
        )
        # If self.check_csrf isn't, doesn't.
        base_view.check_csrf = False
        mock_request.registry.settings = {'check_csrf': True}
        retval = base_view()
        self.assertRaises(
            AssertionError,
            mock_validator.validate.assert_called_with,
            mock_request
        )
        # If settings['check_csrf'] isn't, doesn't.
        base_view.check_csrf = True
        mock_request.registry.settings = {'check_csrf': False}
        retval = base_view()
        self.assertRaises(
            AssertionError,
            mock_validator.validate.assert_called_with,
            mock_request
        )
    
    def test_raises_httpunauthorized(self):
        """Raises ``HTTPUnauthorized`` if CSRF doesn't validate."""
        
        from pyramid.httpexceptions import HTTPUnauthorized
        from ..csrf import CSRFError
        
        def raise_exc(*args):
            raise CSRFError
        
        mock_validator = Mock()
        mock_validator_factory = Mock()
        mock_validator_factory.return_value = mock_validator
        mock_validator.validate = raise_exc
        base_view = self.makeOne(
            Mock(), 
            Selector=Mock(),
            Validator=mock_validator_factory
        )
        self.assertRaises(
            HTTPUnauthorized,
            base_view
        )
    

