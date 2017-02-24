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
    '../libs/js.cookie',
    'backbone',
    'bootstrap-datepicker',
    '../libs/commonmark.min',
    '../libs/linkify/linkify.min',
    '../libs/linkify/linkify-html.min',
    '../libs/js-emoji/emoji.min',
    'select2',

    // src
    'utils/markdown_renderer',
    'utils/markdown_preview',
    'utils/markdown_toolbar_controller',
    'utils/markdown_toolbar',
    'utils/utils',
    'client_edit',
    'forms/add_time_form',
    'forms/add_tracker_form',
    'forms/comment_form',
    'forms/daterange_form',
    'forms/add_action_item_form',
    'forms/project_add_bug_form',
    'forms/project_add_node_form',
    'forms/project_action_item_modals',
    'item'
], function(domReady, $, _, Cookies) {
    var csrftoken = Cookies.get('csrftoken');

    // The following is from
    // https://docs.djangoproject.com/en/1.9/ref/csrf/
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
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
            todayHighlight: true,
            zIndexOffset: 1040
        });

        $('.input-daterange input').datepicker({
            autoclose: true,
            format: 'yyyy-mm-dd',
            todayHighlight: true,
            zIndexOffset: 1040
        });

        $('#project-input').select2({
            placeholder: 'Project',
            width: '100%',
            sorter: selectSorter
        });

        $('#add-trackers-form .field-project select').select2({
            width: '280px',
            sorter: selectSorter
        });
    });
});
