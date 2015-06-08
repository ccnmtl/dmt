require([
    'domReady',
    'jquery',
    'utils/markdown_preview'
], function(domReady, $, MarkdownPreview) {
    domReady(function() {
        if (!$('#pmt-add-comment-form')) {
            return;
        }
        var preview = new MarkdownPreview(
            $('#pmt-add-comment-form textarea[name="comment_src"]'),
            $('.dmt-markdown-preview')
        );
        preview.startEventHandler();
    });
});
