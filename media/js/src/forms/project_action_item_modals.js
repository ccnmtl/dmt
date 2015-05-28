/**
 * This adds the Markdown previewer to the optional comment in the
 * "Mark as In Progress" and "Resolve Item" modals.
 */
require([
    'domReady',
    'jquery',
    'utils/markdown_preview'
], function(domReady, $, MarkdownPreview) {
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
            var preview = new MarkdownPreview(
                $('textarea#dmt-project-item-' + modal + '-comment'),
                $('.dmt-markdown-project-item-' + modal + '-preview')
            );
            preview.startEventHandler();
        });
    });
});
