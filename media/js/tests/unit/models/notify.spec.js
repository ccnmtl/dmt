define(['../../../src/models/notify'], function(Notify) {
    QUnit.test('Notify model tests', function(assert) {
        expect(2);

        var notify = new Notify({iid: 7});
        assert.ok(notify, 'Notify instance is created');
        assert.equal(notify.attributes.iid, 7,
                     'Notify gets the correct id');
    });

    QUnit.test('Notify.url', function(assert) {
        expect(1);

        var notify = new Notify({iid: 7});
        assert.equal(notify.url(), '/drf/notify/7/',
                     'returns the correct url');
    });
});
