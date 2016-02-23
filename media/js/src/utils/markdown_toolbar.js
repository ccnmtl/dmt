define([
    'jquery',
    'utils/markdown_toolbar_controller'
], function($, MarkdownToolbarController) {
    var MarkdownToolbar = function($toolbar, $textarea, markdownPreview) {
        this.$toolbar = $toolbar;
        this.$textarea = $textarea;
        this.markdownPreview = markdownPreview;
        this.lastHotkey = null;
        this.lastText = null;
        this.init();
    };

    /**
     * Given the state of the toolbar+textarea, perform necessary
     * actions when a toolbar button is clicked.
     */
    MarkdownToolbar.prototype.handleButtonClick = function(
        $button, selectionStart, selectionEnd, text
    ) {
        // Get data from button element
        var buttonData = $button.data();
        if (buttonData.hotkey === this.lastHotkey && this.lastText) {
            var diff = text.length - this.lastText.length;
            selectionStart -= diff / 2;
            selectionEnd -= diff / 2;
            text = this.lastText;
            this.lastHotkey = null;
        } else {
            var mtc = new MarkdownToolbarController();
            this.lastText = text;
            text = mtc.render(
                buttonData, selectionStart, selectionEnd, text);
            selectionStart += mtc.prefixLength;
            selectionEnd += mtc.prefixLength;
            this.lastHotkey = buttonData.hotkey;
        }

        return {
            text: text,
            selectionStart: selectionStart,
            selectionEnd: selectionEnd
        };
    };

    MarkdownToolbar.prototype.init = function() {
        var me = this;

        this.$toolbar.find('button.js-toolbar-item').on('click', function(e) {
            var $this = $(this);

            // Get cursor position and textarea's text
            var selectionStart = me.$textarea[0].selectionStart;
            var selectionEnd = me.$textarea[0].selectionEnd;
            var text = me.$textarea.val();

            var result = me.handleButtonClick(
                $this, selectionStart, selectionEnd, text);

            me.$textarea.val(result.text);

            // Reset cursor to original state
            me.$textarea[0].setSelectionRange(
                result.selectionStart,
                result.selectionEnd);
            me.$textarea.focus();

            // Refresh the preview view if it exists.
            if (me.markdownPreview &&
                typeof me.markdownPreview.refresh === 'function'
               ) {
                me.markdownPreview.refresh(me.$textarea.val());
            }
        });

        this.$textarea.on('keyup', function(e) {
            me.lastHotkey = null;
        });
    };

    return MarkdownToolbar;
});
