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
        if ($('#add-action-item-form').length === 0) {
            return;
        }

        var $textarea = $('textarea#dmt-project-new-item-desc');
        var preview = new MarkdownPreview(
            $textarea,
            $('.dmt-markdown-project-item-preview')
        );

        var $toolbar = $textarea.closest('.form-group')
            .find('.js-toolbar.toolbar-commenting');
        var toolbar = new MarkdownToolbar($toolbar, $textarea, preview);

        setupDateSwitcher();

        // set up "remind me" toggle
        $('.remind-me-toggle').on('change', function() {
            var $this = $(this);
            var $reminderInput = $this.closest('.form-group')
                .find('.remind-me-form');
            if ($this.is(':checked')) {
                $reminderInput.show();
            } else {
                $reminderInput.hide();
            }
        });

        // Set up multiple PMT notice
        $('select[name="assigned_to"]').on('change', function(e) {
            var numSelected = $(this).find(':selected').length;
            if (numSelected > 1) {
                $('#multiple-pmt-notice').text(
                    '(creating ' + numSelected + ' PMTs)');
            } else {
                $('#multiple-pmt-notice').text('');
            }
        });
    });
});
