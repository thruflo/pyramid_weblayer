#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functional tests for ``pyramid_weblayer``."""

import unittest

try: # pragma: no cover
    from mock import Mock
except: # pragma: no cover
    pass

class TestI18N(unittest.TestCase):
    def setUp(self):
        from pyramid.i18n import Localizer
        self._localizer = Localizer
        self._original_translate = Localizer.translate
        self.mock_translate = Mock()
        self.mock_translate.return_value = 'Bonjour'
        Localizer.translate = self.mock_translate
    
    def tearDown(self):
        self._localizer.translate = self._original_translate
    
    def makeOne(self):
        from os.path import dirname
        from webtest import TestApp
        from pyramid.config import Configurator
        from pyramid.session import UnencryptedCookieSessionFactoryConfig
        session_factory = UnencryptedCookieSessionFactoryConfig('a')
        def test_i18n(request):
            return {}
        config = Configurator(
            settings={'mako.directories': dirname(__file__)},
            session_factory=session_factory
        )
        config.add_route('r1', '/r1')
        config.add_view(test_i18n, route_name='r1', renderer='test_i18n.mako')
        config.include('pyramid_weblayer')
        return TestApp(config.make_wsgi_app())
    
    def test_i18n(self):
        """Making a GET request should work the translation machinery."""
        
        app = self.makeOne()
        res = app.get('/r1', status=200)
        self.mock_translate.assert_called_with('Hello _i18n')
        self.assertTrue('Bonjour'.encode() in res.body)
    


class TestCSRF(unittest.TestCase):
    def makeOne(self):
        from webtest import TestApp
        from pyramid.config import Configurator
        from pyramid.response import Response
        from pyramid.session import UnencryptedCookieSessionFactoryConfig
        session_factory = UnencryptedCookieSessionFactoryConfig('a')
        def test_get(request):
            return Response(request.session.get_csrf_token())
        def test_post(request):
            return Response('posted')
        config = Configurator(settings={}, session_factory=session_factory)
        config.add_route('r1', '/r1')
        config.add_view(test_get, route_name='r1', request_method='GET')
        config.add_view(test_post, route_name='r1', request_method='POST')
        config.include('pyramid_weblayer')
        return TestApp(config.make_wsgi_app())
    
    def test_csrf_token(self):
        """Making a POST with the right CSRF token is OK."""
        
        app = self.makeOne()
        res = app.get('/r1')
        res = app.post('/r1', {'_csrf_token': res.body})
        self.failUnless('posted'.encode() in res.body)
    
    def test_csrf_invalid_token(self):
        """Making a POST without the right CSRF token fails."""
        
        app = self.makeOne()
        res = app.post('/r2', status=401)
        self.failUnless('Unauthorized'.encode() in res.body)
        res = app.post('/r2', {'_csrf_token': 'blah'}, status=401)
        self.failUnless('Unauthorized'.encode() in res.body)
    
