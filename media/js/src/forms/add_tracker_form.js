require([
    'forms/utils'
], function(formUtils) {
    $(document).ready(function() {
        $('#add-tracker-form').submit(function(event) {
            var $form = $(event.target);
            var pid = $form.find('#tracker-pid-input').val();
            var task = $form.find('#tracker-task-input').val();
            var time = $form.find('#tracker-time-input').val();
            var client = $form.find('#tracker-client-input').val();

            $.ajax({
                type: 'POST',
                url: '/api/1.0/trackers/add/',
                data: {pid: pid, task: task, time: time, client: client},
                success: function(data, status) {
                    return formUtils.onSuccess($form, data, status);
                },
                error: function(xhr, status, error) {
                    return formUtils.onError($form, xhr, status, error);
                }
            });
            event.preventDefault();
        });
    });
});
