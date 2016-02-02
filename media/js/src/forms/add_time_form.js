require([
    'domReady',
    'jquery',
    'forms/utils'
], function(domReady, $, formUtils) {
    domReady(function() {
        $('#add-time-form').submit(function(event) {
            var $form = $(event.target);
            var time = $form.find('#tracker-time-input').val();
            var iid = $form.find('#item-iid-input').val();

            $.ajax({
                type: 'POST',
                url: '/drf/items/' + iid + '/hours/',
                data: {time: time},
                success: function(data, status) {
                    if (data && data.duration > 0) {
                        status = status + ' - Logged ' + data.simpleduration;
                        formUtils.onSuccess($form, data, status);
                        window.location.reload();
                    } else {
                        return formUtils.onError(
                            $form, null, null,
                            'Please enter a valid duration.');
                    }
                },
                error: function(xhr, status, error) {
                    return formUtils.onError($form, xhr, status, error);
                }
            });
            event.preventDefault();
        });
    });
});
