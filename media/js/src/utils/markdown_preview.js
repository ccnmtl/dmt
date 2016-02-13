define([
    '../../libs/commonmark.min',
    '../../libs/linkify/linkify.min',
    '../../libs/linkify/linkify-html.min'
], function(commonmark) {
    var MarkdownPreview = function($textarea, $previewArea) {
        this.reader = commonmark.Parser();
        this.writer = commonmark.HtmlRenderer();
        this.$textarea = $textarea;
        this.$previewArea = $previewArea;
    };

    /**
     * Refresh the markdown preview, given the source text.
     */
    MarkdownPreview.prototype.refresh = function(text) {
        var parsed = this.reader.parse(text);
        var rendered = this.writer.render(parsed);
        if (typeof window.linkifyHtml === 'function') {
            rendered = window.linkifyHtml(rendered);
        }
        this.$previewArea.html(rendered);
    };

    MarkdownPreview.prototype.startEventHandler = function() {
        var me = this;
        this.$textarea.on('change keyup', function(e) {
            var comment = $(e.target).val();
            me.refresh(comment);
        });
    };

    return MarkdownPreview;
});
