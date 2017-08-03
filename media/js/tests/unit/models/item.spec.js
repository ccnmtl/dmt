/* eslint-env qunit */
define(['../../../src/models/item'], function(Item) {
    QUnit.test('should be able to create an instance', function(assert) {
        assert.expect(2);

        var item = new Item({iid: 7});
        assert.ok(item, 'Item instance is created');
        assert.strictEqual(item.get('iid'), 7, 'Item gets the correct id');
    });

    QUnit.test('url() should return correct url', function(assert) {
        assert.expect(1);

        var item = new Item({iid: 7});
        assert.strictEqual(
            item.url(), '/drf/items/7/', 'returns the correct url');
    });
});
