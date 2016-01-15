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

    MarkdownPreview.prototype.startEventHandler = function() {
        var me = this;
        this.$textarea.on('change keyup', function(e) {
            var comment = $(e.target).val();
            var parsed = me.reader.parse(comment);
            var rendered = me.writer.render(parsed);
            if (typeof window.linkifyHtml === 'function') {
                rendered = window.linkifyHtml(rendered);
            }
            me.$previewArea.html(rendered);
        });
    };

    return MarkdownPreview;
});
