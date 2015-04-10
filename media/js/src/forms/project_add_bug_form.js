require([
    'domReady',
    'jquery',
    'bootstrap-datepicker',

    'utils/markdown_preview',
    'forms/utils'
], function(domReady, $, datepicker, MarkdownPreview, formUtils) {
    function setupDateSwitcher() {
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
    }

    domReady(function() {
        if (!$('#add-bug-form')) {
            return;
        }

        var preview = new MarkdownPreview(
            $('textarea#dmt-project-new-bug-desc'),
            $('.dmt-markdown-project-bug-preview')
        );
        preview.startEventHandler();

        setupDateSwitcher();
    });
});
