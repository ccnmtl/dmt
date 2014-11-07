require([
    '../libs/bootstrap-datepicker/bootstrap-datepicker.min',
    'forms/utils'
], function(datepicker, formUtils) {
    $(document).ready(function() {
        var $selectEl = $('#add-action-item-form #action_item-milestone');

        // Get target dates from a global :-/
        if (typeof milestoneActionItemTargets === 'undefined') {
            return;
        }
        var targetDates = milestoneActionItemTargets;

        // Refresh target date when page loads
        formUtils.refreshTargetDate($selectEl, targetDates);

        // Refresh target date when on select element change
        $selectEl.change(function(e) {
            formUtils.refreshTargetDate($(e.target), targetDates);
        });
    });
});
