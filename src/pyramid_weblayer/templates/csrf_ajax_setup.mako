<script type="text/javascript">
  (function (loc, $) {
    var origin = loc.origin;
    if (!origin) { // Patch `window.location.origin` in IE.
      origin = loc.protocol + "//" + loc.hostname + (loc.port ? ':' + loc.port : '');
    }
    // Configure jQuery.ajax to include an 'X-CSRFToken' header to requests
    // with side effects made to relative or same origin urls.
    $.ajaxSetup({
        'beforeSend': function(xhr, s) {
          if (${str(methods) | n}.indexOf(s.type) > -1) {
            if (!/^http(s)?:.*/.test(s.url) || s.url.indexOf() == 0) {
              xhr.setRequestHeader('X-CSRFToken', '${token}');
            }
          }
        }
    });
  })(window.location, jQuery);
</script>