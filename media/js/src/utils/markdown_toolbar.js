define([
    'jquery',
    'utils/markdown_toolbar_controller'
], function($, MarkdownToolbarController) {
    var MarkdownToolbar = function($toolbar) {
        this.$toolbar = $toolbar;
        this.lastHotkey = null;
        this.lastText = null;
        this.init();
    };

    MarkdownToolbar.prototype.init = function() {
        var me = this;
        var $textarea = this.$toolbar.closest('.form-group').find('textarea');

        this.$toolbar.find('button.js-menu-target').on('click', function() {
            var $container = $(this).closest('.js-menu-container');
            $container.toggleClass('active');
        });

        this.$toolbar.find('button.js-toolbar-item').on('click', function() {
            var $this = $(this);
            var prefix = $this.data('prefix');
            var suffix = $this.data('suffix');
            var blockPrefix = $this.data('block-prefix');
            var blockSuffix = $this.data('block-suffix');
            var hotkey = $this.data('toolbar-hotkey');

            var selectionStart = $textarea[0].selectionStart;
            var selectionEnd = $textarea[0].selectionEnd;
            var text = $textarea.val();

            if (hotkey === me.lastHotkey && me.lastText) {
                var diff = text.length - me.lastText.length;
                selectionStart -= diff / 2;
                selectionEnd -= diff / 2;
                text = me.lastText;
                me.lastHotkey = null;
            } else {
                var mtc = new MarkdownToolbarController();
                me.lastText = text;
                text = mtc.render(
                    prefix, suffix, blockPrefix, blockSuffix,
                    selectionStart, selectionEnd, text);
                selectionStart += mtc.prefixLength;
                selectionEnd += mtc.prefixLength;
                me.lastHotkey = hotkey;
            }

            $textarea.val(text);

            // Reset cursor to original state
            $textarea[0].setSelectionRange(selectionStart, selectionEnd);
            $textarea.focus();
        });

        $textarea.on('keyup', function(e) {
            me.lastHotkey = null;
        });
    };

    return MarkdownToolbar;
});
