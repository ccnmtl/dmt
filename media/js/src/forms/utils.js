define([], function() {
    var FormUtils = function() {};

    FormUtils.prototype.onSuccess = function($form, data, status) {
        $form.find('input').val('');

        $form.find('.form-ajax-response').remove();
        $form.append(
            '<div class="form-ajax-response">' +
                '<div class="text-success">' + status + '</div>' +
                '</div>'
        );
    };

    FormUtils.prototype.onError = function($form, xhr, status, error) {
        $form.find('.form-ajax-response').remove();
        $form.append(
            '<div class="form-ajax-response">' +
                '<div class="text-danger">An error occurred: ' +
                error + '</div>' +
                '</div>'
        );
    };

    return new FormUtils();
});
