<script type="text/javascript">
  (function ($) {
    var data = window.weblayer || {},
        loc = window.location,
        origin = loc.origin;
    // Patch `window.location.origin` in IE.
    if (!origin) {
      origin = loc.protocol + "//" + loc.hostname + (loc.port ? ':' + loc.port : '');
    }
    // Provide ``window.weblayer`` csrf data to any js that needs it.
    data.csrf_token = '${token}';
    data.dangerous_methods = ${str(methods) | n};
    window.weblayer = data;
    // Configure jQuery.ajax to include an 'X-CSRFToken' header to requests
    // with side effects made to relative or same origin urls.
    $.ajaxSetup({
        'beforeSend': function(xhr, s) {
          if (data.dangerous_methods.indexOf(s.type) > -1) {
            if (!/^http(s)?:.*/.test(s.url) || s.url.indexOf() == 0) {
              xhr.setRequestHeader('X-CSRFToken', data.csrf_token);
            }
          }
        }
    });
  })(jQuery);
</script>