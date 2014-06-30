define(['../../../src/models/notify'], function(Notify) {
    test('should be able to create an instance', function() {
        expect(2);

        var notify = new Notify({iid: 7});
        ok(notify, 'Notify instance is created');
        equal(notify.attributes.iid, 7, 'Notify gets the correct id');
    });

    test('url() should return correct url', function() {
        expect(1);

        var notify = new Notify({iid: 7});
        equal(notify.url(), '/drf/notify/7/', 'returns the correct url');
    });
});
