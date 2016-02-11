define([
    'domReady',
    'jquery'
], function(domReady, $) {
    domReady(function() {
        var $toolbar = $('.js-toolbar.toolbar-commenting');

        $toolbar.find('button.js-menu-target').on('click', function() {
            var $container = $(this).closest('.js-menu-container');
            $container.toggleClass('active');
        });

        $toolbar.find('button.js-toolbar-item').on('click', function() {
            var $this = $(this);
            var prefix = $this.data('prefix');
            var suffix = $this.data('suffix');
            var blockPrefix = $this.data('block-prefix');
            var blockSuffix = $this.data('block-suffix');
            var $textarea = $this.closest('.form-group').find('textarea');

            var startPos = $textarea[0].selectionStart;
            var endPos = $textarea[0].selectionEnd;

            if (prefix) {
                var v = $textarea.val();
                var textBefore = v.substring(0,  startPos);
                var textAfter = v.substring(endPos, v.length);
                $textarea.val(textBefore + prefix + textAfter);
            }

            $textarea[0].setSelectionRange(startPos, endPos);
            $textarea.focus();
        })
    });
});
