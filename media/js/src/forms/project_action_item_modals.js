/**
 * This adds the Markdown previewer to the optional comment in the
 * "Mark as In Progress" and "Resolve Item" modals.
 */
require([
    'domReady',
    'jquery',
    'utils/markdown_preview'
], function(domReady, $, MarkdownPreview) {
    domReady(function() {
        var preview = new MarkdownPreview(
            $('textarea#dmt-project-item-resolve-comment'),
            $('.dmt-markdown-project-item-resolve-preview')
        );
        preview.startEventHandler();

        preview = new MarkdownPreview(
            $('textarea#dmt-project-item-inprogress-comment'),
            $('.dmt-markdown-project-item-inprogress-preview')
        );
        preview.startEventHandler();
    });
});
