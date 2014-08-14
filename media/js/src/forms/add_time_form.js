require([
    'forms/utils'
], function(formUtils) {
    $(document).ready(function() {
        $('#add-time-form').submit(function(event) {
            var $form = $(event.target);
            var time = $form.find('#tracker-time-input').val();
            var iid = $form.find('#item-iid-input').val();

            $.ajax({
                type: 'POST',
                url: '/api/1.0/items/' + iid + '/hours/',
                data: {time: time},
                success: function(data, status) {
                    formUtils.onSuccess($form, data, status);
                    window.location.reload();
                },
                error: function(xhr, status, error) {
                    return formUtils.onError($form, xhr, status, error);
                }
            });
            event.preventDefault();
        });
    });
});
