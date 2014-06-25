define(['jquery',
        '../../../src/views/item',
        '../../../src/models/item',
       ], function($, ItemView, Item) {
    QUnit.test('Item view tests', function(assert) {
        expect(1);

        var item = new Item({iid: 7});
        var view = new ItemView({model: item, el: $('#item-container')});
        assert.ok(view, 'Item view instance is created');
    });
});
