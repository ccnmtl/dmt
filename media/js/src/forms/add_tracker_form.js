require([
    'domReady',
    'jquery',
    'forms/utils'
], function(domReady, $, formUtils) {
    domReady(function() {
        $('#add-tracker-form').submit(function(event) {
            var $form = $(event.target);
            var pid = $form.find('[name="project"]').val();
            var task = $form.find('#tracker-task-input').val();
            var time = $form.find('#tracker-time-input').val();
            var client = $form.find('#tracker-client-input').val();
            var completed = $form.find('#tracker-completed-input').val();

            $.ajax({
                type: 'POST',
                url: '/drf/trackers/add/',
                data: {
                    pid: pid,
                    task: task,
                    time: time,
                    client: client,
                    completed: completed
                },
                success: function(data, status) {
                    return formUtils.onSuccess($form, data, status, [
                        '#tracker-task-input', '#tracker-time-input'
                    ]);
                },
                error: function(xhr, status, error) {
                    return formUtils.onError($form, xhr, status, error);
                }
            });
            event.preventDefault();
        });
    });
});
