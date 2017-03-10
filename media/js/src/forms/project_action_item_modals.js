/**
 * This adds the Markdown previewer to the optional comment in the
 * "Mark as In Progress" and "Resolve Item" modals.
 */
require([
    'domReady',
    'jquery',
    'utils/markdown_preview',
    'utils/markdown_toolbar',
], function(domReady, $, MarkdownPreview, MarkdownToolbar) {
    var modals = [
        'addcomment',
        'resolve',
        'inprogress',
        'changeowner',
        'reassign',
        'addattachment',
        'verify',
        'reopen'
    ];

    domReady(function() {
        modals.forEach(function(modal) {
            var $textarea = $(
                'textarea#dmt-project-item-' + modal + '-comment');
            if ($textarea.length === 0) {
                return;
            }

            var preview = new MarkdownPreview(
                $textarea,
                $('.dmt-markdown-project-item-' + modal + '-preview')
            );

            var $toolbar = $textarea.closest('.form-group')
                .find('.js-toolbar.toolbar-commenting');
            new MarkdownToolbar($toolbar, $textarea, preview);
        });
    });
});
