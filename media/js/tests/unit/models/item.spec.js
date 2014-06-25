define(['../../../src/models/item'], function(Item) {
    QUnit.test('Item model tests', function(assert) {
        expect(2);

        var item = new Item({iid: 7});
        assert.ok(item, 'Item instance is created');
        assert.equal(item.attributes.iid, 7,
                     'Item gets the correct id');
    });

    QUnit.test('Item.url', function(assert) {
        expect(1);

        var item = new Item({iid: 7});
        assert.equal(item.url(), '/drf/items/7/',
                     'returns the correct url');
    });
});
