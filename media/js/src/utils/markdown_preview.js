define([
    '../../libs/remarkable/remarkable'
], function(Remarkable) {
    var MarkdownPreview = function($textarea, $previewArea) {
        // Strict CommonMark mode doesn't yet support linkify in Remarkable.js
        //   (https://github.com/jonschlinkert/remarkable/issues/149)
        // so just use the normal mode for now since I haven't seen any
        // differences between that and CommonMark.
        this.md = new Remarkable({
            linkify: true
        });
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
