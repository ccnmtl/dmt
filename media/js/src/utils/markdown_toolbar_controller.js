define([
    'jquery'
], function($) {
    var MarkdownToolbarController = function() {
    };

    MarkdownToolbarController.prototype.render = function(
        d, selectionStart, selectionEnd, text
    ) {
        var selectedText = text.substr(selectionStart, selectionEnd);
        if (selectedText.match(/\n/) &&
            d['block-prefix'] &&
            d['block-suffix']
           ) {
            if (d['block-prefix']) {
                text = this.renderBlockPrefix(
                    selectionStart, selectionEnd, d['block-suffix'], text);
            }

            if (d['block-suffix']) {
                text = this.renderBlockSuffix(
                    selectionStart, selectionEnd, this.prefixLength,
                    d['block-suffix'], text);
            }
        } else {
            if (d.prefix) {
                text = this.renderPrefix(
                    selectionStart, selectionEnd, d.prefix, text);
            }

            if (d.suffix) {
                text = this.renderSuffix(
                    selectionStart, selectionEnd, this.prefixLength,
                    d.suffix, text);
            }
        }

        return text;
    };

    MarkdownToolbarController.prototype.renderPrefix = function(
        selectionStart, selectionEnd, prefix, text
    ) {
        this.prefixLength = prefix.length;
        var s = text.substr(0, selectionStart);
        s += prefix;
        s += text.substr(selectionStart, text.length);
        return s;
    };

    MarkdownToolbarController.prototype.renderSuffix = function(
        selectionStart, selectionEnd, prefixLength, suffix, text
    ) {
        selectionEnd += prefixLength;
        var s = text.substr(0, selectionEnd);
        s += suffix;
        s += text.substr(selectionEnd, text.length);
        return s;
    };

    MarkdownToolbarController.prototype.renderBlockPrefix = function(
        selectionStart, selectionEnd, blockPrefix, text
    ) {
        this.prefixLength = blockPrefix.length + 1;
        var s = text.substr(0, selectionStart);
        s += blockPrefix + '\n';
        s += text.substr(selectionStart, text.length);
        return s;
    };

    MarkdownToolbarController.prototype.renderBlockSuffix = function(
        selectionStart, selectionEnd, blockPrefixLength, blockSuffix, text
    ) {
        selectionEnd += blockPrefixLength + 1;
        var s = text.substr(0, selectionEnd);
        s += '\n' + blockSuffix;
        s += text.substr(selectionEnd, text.length);
        return s;
    };

    return MarkdownToolbarController;
});
