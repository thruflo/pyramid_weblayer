
## 0.7

* hsts support to add force https
* tx module with `join_to_transaction` function
* `had_been_seen` and `session_id` request properties
* `generate_random_digest`, `get_stamp` and `datetime_to_float` utility functions

## 0.6

Remove the `.auth` module (having implemented 
[pyramid_simpleauth](http://github.com/thruflo/pyramid_simple_auth)).

Removed the `passlib` and `setuptools_git` dependencies.

## 0.5

Renamed `_csrf_token` request parameter to `_csrf` (a more widely used default).

## 0.4

Added `.auth` module with password `encrypt()` and `verify()` functions.  

(n.b.: This introduces a dependency on 
[passlib](http://pypi.python.org/pypi/passlib/), which atm requires a 
`python setup.py install` from source to work under Python 3).

## 0.3

Remove the ``BaseView`` class and the method selecting functionality, as it
just doesn't work with Pyramid's view configuration.

Re-factored the CSRF validation into a subscriber as a consequence.

## 0.2.1

Fixed the `.i18n.add_underscore_translation` subscriber.

## 0.2

Added i18n features.

## 0.1

Initial version.