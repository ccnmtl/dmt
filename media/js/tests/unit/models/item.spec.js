define(['../../../src/models/item'], function(Item) {
    test('should be able to create an instance', function() {
        expect(2);

        var item = new Item({iid: 7});
        ok(item, 'Item instance is created');
        equal(item.get('iid'), 7, 'Item gets the correct id');
    });

    test('url() should return correct url', function() {
        expect(1);

        var item = new Item({iid: 7});
        equal(item.url(), '/drf/items/7/', 'returns the correct url');
    });
});
