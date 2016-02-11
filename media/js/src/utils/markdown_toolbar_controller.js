define([
    'jquery'
], function($) {
    var MarkdownToolbarController = function() {
    };

    MarkdownToolbarController.prototype.render = function(
        prefix, suffix, blockPrefix, blockSuffix,
        selectionStart, selectionEnd, text
    ) {
        var selectedText = text.substr(selectionStart, selectionEnd);
        if (selectedText.match(/\n/) && blockPrefix && blockSuffix) {
            if (blockPrefix) {
                text = this.renderBlockPrefix(
                    selectionStart, selectionEnd, blockSuffix, text);
            }

            if (blockSuffix) {
                text = this.renderBlockSuffix(
                    selectionStart, selectionEnd, this.prefixLength,
                    blockSuffix, text);
            }
        } else {
            if (prefix) {
                text = this.renderPrefix(
                    selectionStart, selectionEnd, prefix, text);
            }

            if (suffix) {
                text = this.renderSuffix(
                    selectionStart, selectionEnd, this.prefixLength,
                    suffix, text);
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
