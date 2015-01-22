require.config({
    paths: {
        // Major libraries
        jquery: '../libs/jquery/jquery-min',
        underscore: '../libs/underscore/underscore-min',
        backbone: '../libs/backbone/backbone-min',

        // Require.js plugins
        text: '../libs/require/text'
    },
    urlArgs: 'bust=' +  (new Date()).getTime()
});

require([
    // libs
    '../libs/jquery/jquery-min',
    '../libs/jquery.cookie.min',
    '../libs/underscore/underscore-min',
    '../libs/backbone/backbone-min',
    '../libs/bootstrap-datepicker/bootstrap-datepicker.min',
    '../libs/remarkable/remarkable',
    '../libs/typeahead/bloodhound.min',
    '../libs/typeahead/typeahead.jquery.min',

    // src
    'utils/markdown_preview',
    'client_edit',
    'forms/add_time_form',
    'forms/add_tracker_form',
    'forms/project_add_action_item_form',
    'forms/project_add_bug_form',
    'item'
], function() {
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
        prefetch: {
            url: '/drf/projects/',
            filter: function(projects) {
                return $.map(projects.results, function(data) {
                    return {
                        name: data.name,
                        pid: data.pid
                    };
                });
            }
        },
        remote: {
            url: '/drf/projects/?search=%QUERY',
            filter: function(projects) {
                return $.map(projects.results, function(data) {
                    return {
                        name: data.name,
                        pid: data.pid
                    };
                });
            }
        }
    });
    projects.initialize();

    $(document).ready(function() {
        if (typeof $().datepicker === 'function') {
            $('input[name=target_date]').datepicker({
                autoclose: true,
                format: 'yyyy-mm-dd',
                todayHighlight: true
            });
        }

        if (typeof $().typeahead === 'function') {
            $('#project-input').typeahead(null, {
                name: 'results',
                displayKey: 'name',
                source: projects.ttAdapter()
            });
            $('#project-input').on(
                'typeahead:selected',
                function(object, datum) {
                    $('#tracker-pid-input').val(datum.pid);
                });
        }
    });
});
