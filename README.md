A re-factor of some elements of [weblayer][] for use within a [Pyramid][] app.

Provides a `pyramid_weblayer.view.BaseView` class to use as a view
callable and a `pyramid_weblayer.i18n.add_underscore_translation` subscriber
that, when configured, extends the template namespace with an `_` translation
function.

The `BaseView` class protects against CSRF attacks and handles the request
by calling the method that corresponds to the request's HTTP method, i.e.: if
the subclass of `BaseView` has a `get` method and a GET request is routed to
the subclass, its `get` method will be called to handle the request.

Meaning you can write code like:

```python
@view_config(route_name='foo')
class FooView(BaseView):
    def get(self): # handle GET request
    def post(self): # handle POST request
```

Registering the `add_underscore_translation` subscriber, e.g.::

    config.include('pyramid_weblayer')

Allows you to write template code like::

    ${_('Translate me')}

There's also a `pyramid_weblayer.i18n.TranslationAdapter` that adapts a request
to provide a translate method, e.g.::

    translator = TranslationAdapter(request)
    translator.translate('Translate me')

This is provided as an adaptor and not a `pyramid.events.NewRequest` subscriber
(as per the example in [these docs][]) to avoid extending *every request*.

[these docs]: http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/i18n.html

## Tests

I've run the tests under Python2.6 and Python3.2 using, e.g.:

    $ ../bin/nosetests --cover-package=src/pyramid_weblayer --with-doctest --with-coverage --cover-erase
    .....................
    Name                                     Stmts   Miss  Cover   Missing
    ----------------------------------------------------------------------
    src/pyramid_weblayer/__init__                4      0   100%   
    src/pyramid_weblayer/csrf                   18      0   100%   
    src/pyramid_weblayer/i18n                   12      0   100%   
    src/pyramid_weblayer/method                 17      0   100%   
    src/pyramid_weblayer/tests/__init__          0      0   100%   
    src/pyramid_weblayer/tests/test_csrf        54      0   100%   
    src/pyramid_weblayer/tests/test_method      64      0   100%   
    src/pyramid_weblayer/tests/test_view        59      0   100%   
    src/pyramid_weblayer/utils                  19      0   100%   
    src/pyramid_weblayer/view                   23      0   100%   
    ----------------------------------------------------------------------
    TOTAL                                      270      0   100%
    ----------------------------------------------------------------------
    Ran 21 tests in 0.271s
    
    OK

[pyramid]: http://pypi.python.org/pypi/pyramid
[weblayer]: http://github.com/thruflo/weblayer
