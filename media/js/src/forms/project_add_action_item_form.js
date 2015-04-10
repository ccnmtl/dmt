require([
    'domReady',
    'jquery',
    'bootstrap-datepicker',

    'utils/markdown_preview',
    'forms/utils'
], function(domReady, $, datepicker, MarkdownPreview, formUtils) {
    function setupDateSwitcher() {
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
    }

    domReady(function() {
        if (!$('#add-action-item-form')) {
            return;
        }

        var preview = new MarkdownPreview(
            $('textarea#dmt-project-new-item-desc'),
            $('.dmt-markdown-project-item-preview')
        );
        preview.startEventHandler();

        setupDateSwitcher();
    });
});
