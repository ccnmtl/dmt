require([
    '../libs/bootstrap-datepicker/bootstrap-datepicker.min',
    'forms/utils'
], function(datepicker, formUtils) {
    $(document).ready(function() {
        var $selectEl = $('#add-bug-form #bug-milestone');

        // Get target dates from a global :-/
        if (typeof milestoneBugTargets === 'undefined') {
            return;
        }
        var targetDates = milestoneBugTargets;

        // Refresh target date when page loads
        formUtils.refreshTargetDate($selectEl, targetDates);

        // Refresh target date when on select element change
        $selectEl.change(function(e) {
            formUtils.refreshTargetDate($(e.target), targetDates);
        });
    });
});
