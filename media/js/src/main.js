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

        typeahead: '../libs/typeahead/typeahead.jquery.min'
    },
    shim: {
        'bootstrap-datepicker': {
            'deps': ['jquery']
        },
        typeahead: {
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
    '../libs/typeahead/bloodhound.min',
    'typeahead',

    // src
    'utils/markdown_preview',
    'client_edit',
    'forms/add_time_form',
    'forms/add_tracker_form',
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

    var projects = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 10,
        remote: {
            url: '/drf/projects/?search=%QUERY',
            filter: function(projects) {
                return _.map(projects.results, function(data) {
                    return {
                        name: data.name,
                        pid: data.pid
                    };
                });
            }
        }
    });
    projects.initialize();

    domReady(function() {
        $('input[name=target_date]').datepicker({
            autoclose: true,
            format: 'yyyy-mm-dd',
            todayHighlight: true
        });

        $('#project-input,#add-trackers-form .field-project input').typeahead({
            hint: false,
            highlight: true
        }, {
            name: 'results',
            displayKey: 'name',
            source: projects.ttAdapter()
        });

        $('#project-input').on('typeahead:selected', function(object, datum) {
            $('#tracker-pid-input').val(datum.pid);
        });
        $('#add-trackers-form .field-project input').on(
            'typeahead:selected',
            function(e, datum) {
                var pid = datum.pid;
                var $input = $(e.target);
                var name = $input.attr('name');
                var $pidInput = $input.closest('tr')
                    .find('input[name="' + name + '_pid"]').first();
                $pidInput.val(pid);
            });
    });
});
