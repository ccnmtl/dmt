require.config({
    map: {
        // This configures jquery to not export the $ and jQuery global
        // variables.
        '*': {
            'jquery': 'jquery-private'
        },
        'jquery-private': {
            'jquery': 'jquery'
        }
    },
    paths: {
        // Major libraries
        jquery: '../libs/jquery/jquery-min',
        'jquery-private': '../libs/jquery/jquery-private',

        underscore: '../libs/underscore/underscore-min',
        backbone: '../libs/backbone/backbone-min',

        // Require.js plugins
        text: '../libs/require/text',
        domReady: '../libs/require/domReady',

        'bootstrap-datepicker':
            '../libs/bootstrap-datepicker/bootstrap-datepicker.min',

        select2: '../libs/select2/select2.min'
    },
    shim: {
        'bootstrap-datepicker': {
            'deps': ['jquery']
        },
        'select2': {
            'deps': ['jquery']
        },
        backbone: {
            'deps': ['underscore', 'jquery'],
            'exports': 'Backbone'
        },
        underscore: {
            'exports': '_'
        }
    },
    urlArgs: 'bust=' +  (new Date()).getTime()
});

require([
    // libs
    'domReady',
    'jquery',
    'underscore',
    '../libs/jquery.cookie.min',
    'backbone',
    'bootstrap-datepicker',
    '../libs/remarkable/remarkable',
    'select2',

    // src
    'utils/markdown_preview',
    'client_edit',
    'forms/add_time_form',
    'forms/add_tracker_form',
    'forms/comment_form',
    'forms/project_add_action_item_form',
    'forms/project_add_bug_form',
    'forms/project_action_item_modals',
    'item'
], function(domReady, $, _) {
    var csrftoken = $.cookie('csrftoken');

    // The following is from
    // https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/#ajax
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var srOrigin = '//' + host;
        var origin = protocol + srOrigin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin ||
                url.slice(0, origin.length + 1) == origin + '/') ||
            (url == srOrigin ||
             url.slice(0, srOrigin.length + 1) == srOrigin + '/') ||
            // or any other URL that isn't scheme relative or absolute
            // i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        }
    });

    var selectSorter = function(results) {
        var query = $('.select2-search__field').val().toLowerCase();
        return results.sort(function(a, b) {
            return a.text.toLowerCase().indexOf(query) -
                b.text.toLowerCase().indexOf(query);
        });
    };

    domReady(function() {
        $('input[name=target_date]').datepicker({
            autoclose: true,
            format: 'yyyy-mm-dd',
            todayHighlight: true
        });

        $('#project-input').select2({
            placeholder: 'Project',
            width: '100%',
            sorter: selectSorter
        });
        $('#add-trackers-form .field-project select,' +
          'select#project-personnel-input').select2({
              width: '280px',
              sorter: selectSorter
          });
    });
});
