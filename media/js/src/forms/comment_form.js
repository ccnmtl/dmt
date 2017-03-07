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

        var $textarea = $(
            '#pmt-add-comment-form textarea[name="comment_src"]');
        var preview = new MarkdownPreview(
            $textarea, $('.dmt-markdown-preview'));

        new MarkdownToolbar(
            $('#pmt-add-comment-form .js-toolbar.toolbar-commenting'),
            $textarea,
            preview
        );
    });
});
