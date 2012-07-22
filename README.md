Common / shared utilities for a [Pyramid][] web application.  (Some originally
re-factored from the depreciated [weblayer][] micro-framework).

Provides:

* a subscriber to validate incoming requests against cross site request forgeries
* a subscriber that extends the template namespace with a `_()` function for 
  translating message strings
* an `hsts.force_https` configuration flag to force incoming requests to https
* a `join_to_transaction` function to hang function calls off an after commit hook
* some misc. request properties and utility functions

## Tests

The tests pass using Python2.6 and Python3.2, e.g.:

    $ nosetests --with-coverage --with-doctest --cover-package pyramid_weblayer pyramid_weblayer
    ............................
    Name                       Stmts   Miss  Cover   Missing
    --------------------------------------------------------
    pyramid_weblayer              15      0   100%   
    pyramid_weblayer.csrf         26      0   100%   
    pyramid_weblayer.hsts         35      0   100%   
    pyramid_weblayer.i18n         12      0   100%   
    pyramid_weblayer.seen         10      0   100%   
    pyramid_weblayer.session      12      0   100%   
    pyramid_weblayer.tx           33      0   100%   
    pyramid_weblayer.utils        37      0   100%   
    --------------------------------------------------------
    TOTAL                        180      0   100%   
    ----------------------------------------------------------------------
    Ran 28 tests in 0.430s

    OK

[pyramid]: http://pypi.python.org/pypi/pyramid
[weblayer]: http://github.com/thruflo/weblayer
