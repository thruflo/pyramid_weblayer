#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for `pyramid_weblayer.method`."""

import unittest

try: # pragma: no cover
    from mock import Mock
except: # pragma: no cover
    pass

class TestMethodSelector(unittest.TestCase):
    """Test the logic of py:class:`~pyramid_weblayer.method.MethodSelector`."""
    
    def makeOne(self, **kwargs):
        from pyramid_weblayer.method import MethodSelector
        class MockContext(object):
            a = 'method_a'
            c = 'method_c'
        
        return MethodSelector(MockContext(), **kwargs)
    
    def test_method_name_must_be_basestring(self):
        """Method name must be a ``basestring``."""
        
        method_selector = self.makeOne()
        self.assertRaises(ValueError, method_selector.select, 42)
        self.assertRaises(ValueError, method_selector.select, None)
    
    def test_select(self):
        """For a method to be selected it must exist and be exposed."""
        
        method_selector = self.makeOne(exposed_methods=['a'])
        return_value = method_selector.select('a')
        self.assertTrue(return_value == 'method_a')
        
        return_value = method_selector.select('b')
        self.assertTrue(return_value is None)
        
        method_selector = self.makeOne(exposed_methods=[])
        return_value = method_selector.select('a')
        self.assertTrue(return_value is None)
    
    def test_force_to_lowercase(self):
        """Method name is forced to lower case."""
        
        method_selector = self.makeOne(exposed_methods=['a'])
        self.assertTrue(method_selector.select('A') == 'method_a')
    


class TestHEADSpecialCase(unittest.TestCase):
    """Test special casing HEAD requests."""
    
    def makeOne(self, *args, **kwargs):
        from pyramid_weblayer.method import MethodSelector
        return MethodSelector(*args, **kwargs)
    
    def test_head_exposed_head_defined(self):
        """If there's an exposed head method, a HEAD request will select it."""
        
        class MockContext(object):
            head = 'method_head'
        
        context = MockContext()
        method_selector = self.makeOne(context, exposed_methods=['head'])
        
        return_value = method_selector.select('HEAD')
        self.assertTrue(return_value == 'method_head')
    
    def test_head_not_exposed(self):
        """If there's a head method but it's not exposed, the return value is
          ``None``.
        """
        
        class MockContext(object):
            head = 'method_head'
        
        context = MockContext()
        method_selector = self.makeOne(context, exposed_methods=[])
        
        return_value = method_selector.select('HEAD')
        self.assertTrue(return_value is None)
    
    def test_head_exposed_get_exposed_and_exists(self):
        """If there isn't a head method but there is a get method and both
          head and get are exposed, the return value is the get method.
        """
        
        class MockContext(object):
            get = 'method_get'
        
        context = MockContext()
        method_selector = self.makeOne(context, exposed_methods=['head', 'get'])
        
        return_value = method_selector.select('HEAD')
        self.assertTrue(return_value == 'method_get')
    
    def test_head_exposed_get_exposed_get_not_defined(self):
        """If there isn't a head method or a get method and both head and get
          are exposed, the return value is ``None``.
        """
        
        class MockContext(object):
            pass
        
        context = MockContext()
        method_selector = self.makeOne(context, exposed_methods=['head', 'get'])
        
        return_value = method_selector.select('HEAD')
        self.assertTrue(return_value is None)
    
    def test_head_exposed_get_exposed_get_defined(self):
        """If there isn't a head method but there is a get method, head is
          exposed but get isn't, the return value is ``None``.
        """
        
        class MockContext(object):
            get = 'method_get'
        
        context = MockContext()
        method_selector = self.makeOne(context, exposed_methods=['head'])
        
        return_value = method_selector.select('HEAD')
        self.assertTrue(return_value is None)
    
