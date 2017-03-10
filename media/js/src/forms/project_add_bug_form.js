require([
    'domReady',
    'jquery',
    'bootstrap-datepicker',

    'utils/markdown_preview',
    'utils/markdown_toolbar',
    'forms/utils'
], function(
    domReady, $, datepicker, MarkdownPreview, MarkdownToolbar, formUtils
) {
    function setupDateSwitcher() {
        var $selectEl = $('#add-bug-form #bug-milestone');

        // Get target dates from a global :-/
        if (typeof window.milestoneBugTargets === 'undefined') {
            return;
        }
        var targetDates = window.milestoneBugTargets;

        // Refresh target date when page loads
        formUtils.refreshTargetDate($selectEl, targetDates);

        // Refresh target date when on select element change
        $selectEl.change(function(e) {
            formUtils.refreshTargetDate($(e.target), targetDates);
        });
    }

    domReady(function() {
        if ($('#add-bug-form').length === 0) {
            return;
        }

        var $textarea = $('textarea#dmt-project-new-bug-desc');
        var preview = new MarkdownPreview(
            $textarea,
            $('.dmt-markdown-project-bug-preview')
        );

        var $toolbar = $textarea.closest('.form-group')
            .find('.js-toolbar.toolbar-commenting');
        new MarkdownToolbar($toolbar, $textarea, preview);

        setupDateSwitcher();
    });
});
