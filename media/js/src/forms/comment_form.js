require([
    'domReady',
    'jquery',
    'utils/markdown_preview',
    'utils/markdown_toolbar'
], function(domReady, $, MarkdownPreview, MarkdownToolbar) {
    domReady(function() {
        if (!$('#pmt-add-comment-form')) {
            return;
        }

        var preview = new MarkdownPreview(
            $('#pmt-add-comment-form textarea[name="comment_src"]'),
            $('.dmt-markdown-preview')
        );
        preview.startEventHandler();

        var toolbar = new MarkdownToolbar(
            $('#add-comment .js-toolbar.toolbar-commenting'),
            preview
        );
    });
});
