
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