define([
    'jquery',
    'underscore',
    'bootstrap-datepicker'
], function($, _) {
    var FormUtils = function() {};

    FormUtils.prototype.refreshTargetDate = function($selectEl, targetDates) {
        if (!targetDates || targetDates.length <= 0) {
            return;
        }

        var idx = $selectEl.find('option:selected').index();
        var $datepickerInput = $selectEl.closest('form').find(
            '#actionitem_target_date,#bug_target_date');

        if (targetDates.length > idx) {
            $datepickerInput.val(targetDates[idx]);
            $datepickerInput.datepicker(
                'update', targetDates[idx]);
        }
    };

    /**
     * @param {jQuery} $form
     * @param {object} data
     * @param {string} status
     * @param {array} clearSelectors - An optional argument that can
     *   contain an array of selectors that the form clears on success.
     *   If this argument isn't used, onSuccess defaults to clearing
     *   every visible input in the form.
     */
    FormUtils.prototype.onSuccess = function(
        $form, data, status, clearSelectors
    ) {
        if (_.isArray(clearSelectors)) {
            $form.find(clearSelectors.join(', ')).val('');
        } else {
            $form.find('input:visible').val('');
        }

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
