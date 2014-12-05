require([
    // libs
    '../libs/jquery/jquery-min',
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
