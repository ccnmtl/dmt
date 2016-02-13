define([
    'jquery',
    'utils/markdown_toolbar_controller'
], function($, MarkdownToolbarController) {
    var MarkdownToolbar = function($toolbar, markdownPreview) {
        this.$toolbar = $toolbar;
        this.lastHotkey = null;
        this.lastText = null;
        this.markdownPreview = markdownPreview;
        this.init();
    };

    MarkdownToolbar.prototype.init = function() {
        var me = this;
        var $textarea = this.$toolbar.closest('.form-group').find('textarea');

        this.$toolbar.find('button.js-toolbar-item').on('click', function(e) {
            var $this = $(this);

            // Get data from button element
            var buttonData = $this.data();

            // Get cursor position and textarea's text
            var selectionStart = $textarea[0].selectionStart;
            var selectionEnd = $textarea[0].selectionEnd;
            var text = $textarea.val();

            if (buttonData.hotkey === me.lastHotkey && me.lastText) {
                var diff = text.length - me.lastText.length;
                selectionStart -= diff / 2;
                selectionEnd -= diff / 2;
                text = me.lastText;
                me.lastHotkey = null;
            } else {
                var mtc = new MarkdownToolbarController();
                me.lastText = text;
                text = mtc.render(
                    buttonData, selectionStart, selectionEnd, text);
                selectionStart += mtc.prefixLength;
                selectionEnd += mtc.prefixLength;
                me.lastHotkey = buttonData.hotkey;
            }

            $textarea.val(text);

            // Reset cursor to original state
            $textarea[0].setSelectionRange(selectionStart, selectionEnd);
            $textarea.focus();

            // Refresh the preview view if it exists.
            if (me.markdownPreview &&
                typeof me.markdownPreview.refresh === 'function'
               ) {
                me.markdownPreview.refresh($textarea.val());
            }
        });

        $textarea.on('keyup', function(e) {
            me.lastHotkey = null;
        });
    };

    return MarkdownToolbar;
});
