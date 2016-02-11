define([
    '../../../src/utils/markdown_toolbar_controller'
], function(MarkdownToolbarController) {
    test('should render prefixes correctly', function() {
        var text = 'abcdefg';
        var rendered = '**abcdefg';
        var c = new MarkdownToolbarController();
        strictEqual(c.renderPrefix(0, 7, '**', text), rendered);
    });

    test('should render suffixes correctly', function() {
        var text = 'abcdefg';
        var rendered = 'abcdefg**';
        var c = new MarkdownToolbarController();
        strictEqual(c.renderSuffix(0, 7, 2, '**', text), rendered);
    });

    test('should render block prefixes correctly', function() {
        var text = 'abcc';
        var c = new MarkdownToolbarController();
        ok(c.renderBlockPrefix(0, 0, '#', text));
    });

    test('should render block suffixes correctly', function() {
        var text = 'abcc';
        var c = new MarkdownToolbarController();
        ok(c.renderBlockSuffix(0, 0, 1, '#', text));
    });

    test('should render bold selections correctly', function() {
        var text = 'abcdef';
        var rendered = 'abcdef****';
        var c = new MarkdownToolbarController();
        strictEqual(c.render('**', '**', null, null, 6, 6, text), rendered);

        text = 'abcdef';
        rendered = '**abcdef**';
        c = new MarkdownToolbarController();
        strictEqual(c.render('**', '**', null, null, 0, 6, text), rendered);

        text = 'abcdef\nabcdef\n';
        rendered = '**abcdef**\nabcdef\n';
        c = new MarkdownToolbarController();
        strictEqual(c.render('**', '**', null, null, 0, 6, text), rendered);

        text = 'abcdef\nabcdef\n';
        rendered = '**abcdef\nabcdef**\n';
        c = new MarkdownToolbarController();
        strictEqual(c.render('**', '**', null, null, 0, 13, text), rendered);
    });

    test('should render code selections correctly', function() {
        var text = 'abcdef';
        var rendered = 'abcdef``';
        var c = new MarkdownToolbarController();
        strictEqual(c.render('`', '`', '```', '```', 6, 6, text), rendered);

        text = 'abcdef';
        rendered = '`abcdef`';
        c = new MarkdownToolbarController();
        strictEqual(c.render('`', '`', '```', '```', 0, 6, text), rendered);

        text = 'abcdef\nabcdef\n';
        rendered = '`abcdef`\nabcdef\n';
        c = new MarkdownToolbarController();
        strictEqual(c.render('`', '`', '```', '```', 0, 6, text), rendered);

        text = 'abcdef\nabcdef\n';
        rendered = '```\nabcdef\nabcdef\n\n```';
        c = new MarkdownToolbarController();
        strictEqual(c.render('`', '`', '```', '```', 0, 13, text), rendered);
    });
});
