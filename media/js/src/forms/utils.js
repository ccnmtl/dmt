define([], function() {
    var FormUtils = function() {};

    FormUtils.prototype.refreshTargetDate = function($selectEl, targetDates) {
        if (
            typeof $().datepicker === 'undefined' ||
                !targetDates ||
                targetDates.length <= 0
        ) {
            return;
        }

        var idx = $selectEl.find('option:selected').index();
        var $datepickerInput =
            $selectEl.closest('form').find('#id_target_date');

        if (targetDates.length > idx) {
            $datepickerInput.val(targetDates[idx]);
            $datepickerInput.datepicker(
                'update', targetDates[idx]);
        }
    };

    FormUtils.prototype.onSuccess = function($form, data, status) {
        $form.find('input:visible').val('');

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
