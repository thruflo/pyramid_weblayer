#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for `pyramid_weblayer.csrf`."""

import unittest

try: # pragma: no cover
    from mock import Mock
except: # pragma: no cover
    pass


"""
class CSRFValidator(object):
    def __init__(self, session_token, target_methods=METHODS_WITH_SIDE_EFFECTS):
        self._session_token = session_token
        self._target_methods = target_methods
    
    def validate(self, request):
        if not request.method.lower() in self._target_methods:
            return
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return
        request_param = request.params.get('csrf_token', None)
        if request_param is None:
            raise CSRFError('`csrf_token` missing from %s' % request.method)
        if request_param != self._session_token:
            raise CSRFError('`csrf_token` param does not match session token.')
    

"""

class TestCSRFValidator(unittest.TestCase):
    """Test the logic of py:class:`~pyramid_weblayer.csrf.CSRFValidator`."""
    
    def makeOne(self, session_token, **kwargs):
        from pyramid_weblayer.csrf import CSRFValidator
        return CSRFValidator(session_token, **kwargs)
    
    def test_validates_with_correct_request_param(self):
        """Requests validate OK when they have the correct ``csrf_token``."""
        
        from pyramid_weblayer.csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'a'
        mock_request.params = {'csrf_token': 'token'}
        
        validator = self.makeOne('token', target_methods=['a'])
        retval = validator.validate(mock_request)
        self.assertTrue(retval is None)
    
    def test_raises_csrf_error_with_no_request_param(self):
        """Requests must have ``csrf_token``."""
        
        from pyramid_weblayer.csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'a'
        mock_request.params = {}
        
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_raises_csrf_error_with_wrong_request_param(self):
        """Requests must have the right ``csrf_token``."""
        
        from pyramid_weblayer.csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'a'
        mock_request.params = {'csrf_token': 'wrong'}
        
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_method_must_have_side_effects(self):
        """Method must have side effects."""
        
        from pyramid_weblayer.csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'b'
        
        validator = self.makeOne('token', target_methods=['a'])
        retval = validator.validate(mock_request)
        
        self.assertTrue(retval is None)
        self.assertRaises(
            AssertionError,
            mock_request.headers.get.assert_called_with,
            'X-Requested-With'
        )
        
        mock_request = Mock()
        mock_request.method = 'a'
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_force_to_lowercase(self):
        """Method name is forced to lower case."""
        
        from pyramid_weblayer.csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'A'
        
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_ignores_xmlhttprequests(self):
        """Ignores ``XMLHttpRequest``s."""
        
        from pyramid_weblayer.csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'A'
        
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
        
        mock_request.headers = {'X-Requested-With': 'XMLHttpRequest'}
        retval = validator.validate(mock_request)
        self.assertTrue(retval is None)
    

