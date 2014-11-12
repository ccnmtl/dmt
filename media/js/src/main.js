require([
    // libs
    '../libs/jquery/jquery-min',
    '../libs/underscore/underscore-min',
    '../libs/backbone/backbone-min',
    '../libs/bootstrap-datepicker/bootstrap-datepicker.min',
    '../libs/remarkable/remarkable',

    // src
    'utils/markdown_preview',
    'client_edit',
    'forms/add_time_form',
    'forms/add_tracker_form',
    'forms/project_add_action_item_form',
    'forms/project_add_bug_form',
    'item'
], function() {
    $(document).ready(function() {
        if (typeof $().datepicker === 'function') {
            $('input[name=target_date]').datepicker({
                autoclose: true,
                format: 'yyyy-mm-dd',
                todayHighlight: true
            });
        }
    });
});
