Common / shared utilities for a [Pyramid][] web application.  (Some originally
re-factored from the depreciated [weblayer][] micro-framework).

I generally use this package as a home for simple bits of code that are reusable
across Pyramid applications, i.e.: stuff I've written once for a project and
then extracted for use across multiple projects.

Highlights include:

* a subscriber to validate incoming requests against cross site request forgeries
* a subscriber that extends the template namespace with a `_()` function for 
  translating message strings
* an `hsts.force_https` configuration flag to force incoming requests to https
* a `join_to_transaction` function to hang function calls off an after commit hook
* a whole bunch of other request properties and utility functions

Read the source for more info.

## Tests

I tend to add things too fast to keep 100% coverage and test against multiple
Python versions. So expect code to be tested against python2.7 and to have
decent but not exhaustive coverage. Patches to increase compatibility and
coverage are very welcome.

To run the tests, `pip install mock nose coverage WebTest` and e.g.:

    $ nosetests pyramid_weblayer --with-doctest --with-coverage --cover-tests --cover-package pyramid_weblayer
    ...
    Ran 40 tests in 0.297s
    
    OK

[pyramid]: http://pypi.python.org/pypi/pyramid
[weblayer]: http://github.com/thruflo/weblayer
