define([
    '../../../src/utils/markdown_toolbar_controller',
    '../../../src/utils/markdown_toolbar'
], function(MarkdownToolbar) {
    test('should initialize', function() {
        var mt = new MarkdownToolbar();
        ok(mt);
    });
});
