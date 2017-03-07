require([
    'domReady',
    'jquery',

    'utils/markdown_preview',
    'utils/markdown_toolbar'
], function(domReady, $, MarkdownPreview, MarkdownToolbar) {
    domReady(function() {
        if ($('#add-node').length === 0) {
            return;
        }

        var $textarea = $('#add-node textarea.form-control');
        var preview = new MarkdownPreview(
            $textarea,
            $('.dmt-markdown-project-node-preview')
        );

        var $toolbar = $textarea.closest('.form-group')
            .find('.js-toolbar.toolbar-commenting');
        new MarkdownToolbar($toolbar, $textarea, preview);
    });
});
