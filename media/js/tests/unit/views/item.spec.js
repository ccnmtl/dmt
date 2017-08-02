/* eslint-env qunit */
define(
    [
        'jquery',
        '../../../src/utils/markdown_preview',
        '../../../src/views/item',
        '../../../src/models/item'
    ], function($, MarkdownPreview, ItemView, Item) {
        QUnit.test('should create an instance', function(assert) {
            assert.expect(1);

            var iid = 7;
            var item = new Item({iid: iid});
            var view = new ItemView({model: item, el: $('#item-container')});
            assert.ok(view, 'Item view instance is created');
        });
    });
