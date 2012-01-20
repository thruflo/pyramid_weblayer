A re-factor of some elements of [weblayer][] for use within a [Pyramid][] app.

Mainly provides a `pyramid_weblayer.view.BaseView` class to use as a view
callable.  This class protects against CSRF attacks and handles the request
by calling the method that corresponds to the request's HTTP method, i.e.: if
the subclass of `BaseView` has a `get` method and a GET request is routed to
the subclass, its ``get`` method will be called to handle the request.

Meaning you can write code like:

```python
@view_config(route_name='foo')
class FooView(BaseView):
    def get(self): # handle GET request
    def post(self): # handle POST request
```

## Tests

I've run the tests under Python2.6 and Python3.2 using, e.g.:

    $ ../bin/nosetests --cover-package=src/pyramid_weblayer --with-doctest --with-coverage --cover-erase
    .....................
    Name                                     Stmts   Miss  Cover   Missing
    ----------------------------------------------------------------------
    src/pyramid_weblayer/__init__                0      0   100%   
    src/pyramid_weblayer/csrf                   18      0   100%   
    src/pyramid_weblayer/method                 17      0   100%   
    src/pyramid_weblayer/tests/__init__          0      0   100%   
    src/pyramid_weblayer/tests/test_csrf        54      0   100%   
    src/pyramid_weblayer/tests/test_method      64      0   100%   
    src/pyramid_weblayer/tests/test_view        59      0   100%   
    src/pyramid_weblayer/utils                  19      0   100%   
    src/pyramid_weblayer/view                   23      0   100%   
    ----------------------------------------------------------------------
    TOTAL                                      254      0   100%   
    ----------------------------------------------------------------------
    Ran 21 tests in 0.271s
    
    OK

[pyramid]: http://pypi.python.org/pypi/pyramid
[weblayer]: http://github.com/thruflo/weblayer
