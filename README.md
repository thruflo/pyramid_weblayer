A re-factor of some elements of [weblayer][] for use within a [Pyramid][] app.

Provides a `validate_against_csrf` subscriber to validate incoming requests
against cross site request forgeries and an `add_underscore_translation`
subscriber that extends the template namespace with a `_()` function for
translating message strings.

## Tests

The tests pass using Python2.6 and Python3.2, e.g.:

    $ nosetests --cover-package=pyramid_weblayer --cover-tests --with-doctest --with-coverage
    ............
    Name                                      Stmts   Miss  Cover   Missing
    -----------------------------------------------------------------------
    pyramid_weblayer                              6      0   100%   
    pyramid_weblayer.csrf                        26      0   100%   
    pyramid_weblayer.i18n                        12      0   100%   
    pyramid_weblayer.tests                        0      0   100%   
    pyramid_weblayer.tests.test_csrf             89      0   100%   
    pyramid_weblayer.tests.test_integration      58      0   100%   
    pyramid_weblayer.utils                       19      0   100%   
    -----------------------------------------------------------------------
    TOTAL                                       210      0   100%   
    ----------------------------------------------------------------------
    Ran 16 tests in 0.400s
    
    OK

[pyramid]: http://pypi.python.org/pypi/pyramid
[weblayer]: http://github.com/thruflo/weblayer
