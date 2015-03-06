
## 0.14

Fix CSRF validation for CORS requests using `withCredentials`.

## 0.13.2

Allow configuration `registry` to be passed into `main.make_wsgi_app`.

## 0.13

Noop tracking in `development` and `testing` modes.

## 0.12.5

Update the mako monkey patching in `patch.py` to work with both the old
`pyramid.mako_templating` module and the new `pyramid_mako` library
introduced with Pyramid 1.5.

## 0.12

Breaking change: update CSRF machinery to also protect AJAX requests, as per
[this security advice][].

Previously, requests with an `X-Requested-With` header value of `XMLHttpRequest`
were not validated against a CSRF token. Now, they are. This will break existing
applications that rely on the previous behaviour: they will see `403 Forbidden`
responses to XHR requests that were previously working -- when those requests
use methods that can have side effects, i.e.: `POST`, `PUT` and `DELETE`.

The new CSRF validator for `XMLHttpRequest`s first looks for a `_csrf` token in
the request params (as per normal requests). If this is not found, it looks for
a token in the `X-CSRFToken` header.

If you use jQuery (or Zepto, etc.) and server side templating through Pyramid,
you can use the [pyramid_layout][] panel provided to add this header to all
appropriate AJAX requests. Add it to your base template, e.g. just below your
jQuery / Zepto script:

    <script src="your/jquery.js"></script>
    ${panel('csrf-ajax-setup')}

This adds a script element with code along these lines:

    $.ajaxSetup({
      'beforeSend': function(xhr, s) {
        if (can_have_side_effects && is_relative_or_same_origin) {
          xhr.setRequestHeader('X-CSRFToken', '<csrf token>');
        }
      }
    });

[this security advice]: https://www.djangoproject.com/weblog/2011/feb/08/security/
[pyramid_layout]: http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/

## 0.11.4

Use the extracted `pyramid_hsts` package for the HSTS implementation.

## 0.11.3

Hack in a horrible `use dogpile.cache as mako backed` integration.

## 0.11.2

Fix import error in `0.11.1`.

## 0.11.1

Provide ``request.track_page`` method to track a virtual page view with a server
side call to google analytics.

## 0.11

Fix a major bug in the HSTS url -> secure url parsing logic that was squishing
redirect responses in Chrome and IE.

## 0.10.2

Add a tween to secure all relative redirect responses when HSTS is enabled. This
fixes redirects in chrome, for apps running behind a proxy.

## 0.10.1

And complete the set with a secured `request.resource_url` when HSTS is enabled.

## 0.10

Secure the `request.application_url` property, in the same way we secure the
`request.route_url` method, when HSTS is enabled.

## 0.9.2

0.9.1 was a brown bag: the sdist was missing the form.mako template.

## 0.9 / 0.9.1

Improved docs.

## 0.8.5

Added ``snip_text`` and ``snip_html`` functions to template namespace.

## 0.8.4

Added Redis ``queue.QueueProcessor``.

## 0.8.3

Added `fileupload` template def.

## 0.8.2

Override ``request.route_url`` to force urls to use a secure protocol when
force https is enabled.

## 0.8

Provide `nav` module to add `is_active` to the template namespace.

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