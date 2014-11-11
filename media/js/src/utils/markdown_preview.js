define([
    '../../libs/remarkable/remarkable'
], function(Remarkable) {
    var MarkdownPreview = function($textarea, $previewArea) {
        this.md = new Remarkable();
        this.$textarea = $textarea;
        this.$previewArea = $previewArea;
    };

    MarkdownPreview.prototype.startEventHandler = function() {
        var me = this;
        this.$textarea.on('change keyup', function(e) {
            var comment = $(e.target).val();
            var renderedHtml = me.md.render(comment);
            me.$previewArea.html(renderedHtml);
        });
    };

    return MarkdownPreview;
});
