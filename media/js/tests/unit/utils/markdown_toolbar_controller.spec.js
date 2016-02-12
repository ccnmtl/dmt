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
        var rendered = '```\nabcc';
        var c = new MarkdownToolbarController();
        strictEqual(c.renderBlockPrefix(0, 0, '```', text), rendered);
    });

    test('should render block suffixes correctly', function() {
        var text = 'abcc';
        var rendered = 'abcc\n```';
        var c = new MarkdownToolbarController();
        strictEqual(c.renderBlockSuffix(0, 0, 3, '```', text), rendered);
    });

    test('should render bold selections correctly', function() {
        var text = 'abcdef';
        var data = {
            'prefix': '**',
            'suffix': '**'
        };
        var rendered = 'abcdef****';
        var c = new MarkdownToolbarController();
        strictEqual(c.render(data, 6, 6, text), rendered);

        text = 'abcdef';
        rendered = '**abcdef**';
        c = new MarkdownToolbarController();
        strictEqual(c.render(data, 0, 6, text), rendered);

        text = 'abcdef\nabcdef\n';
        rendered = '**abcdef**\nabcdef\n';
        c = new MarkdownToolbarController();
        strictEqual(c.render(data, 0, 6, text), rendered);

        text = 'abcdef\nabcdef\n';
        rendered = '**abcdef\nabcdef**\n';
        c = new MarkdownToolbarController();
        strictEqual(c.render(data, 0, 13, text), rendered);
    });

    test('should render code selections correctly', function() {
        var text = 'abcdef';
        var data = {
            'prefix': '`',
            'suffix': '`',
            'block-prefix': '```',
            'block-suffix': '```'
        };
        var rendered = 'abcdef``';
        var c = new MarkdownToolbarController();
        strictEqual(c.render(data, 6, 6, text), rendered);

        text = 'abcdef';
        rendered = '`abcdef`';
        c = new MarkdownToolbarController();
        strictEqual(c.render(data, 0, 6, text), rendered);

        text = 'abcdef\nabcdef\n';
        rendered = '`abcdef`\nabcdef\n';
        c = new MarkdownToolbarController();
        strictEqual(c.render(data, 0, 6, text), rendered);

        text = 'abcdef\nabcdef\n';
        rendered = '```\nabcdef\nabcdef\n\n```';
        c = new MarkdownToolbarController();
        strictEqual(c.render(data, 0, 13, text), rendered);
    });
});
