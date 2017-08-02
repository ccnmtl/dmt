/* eslint-env qunit */
define(['../../../src/models/notify'], function(Notify) {
    QUnit.test('should be able to create an instance', function(assert) {
        assert.expect(2);

        var notify = new Notify({iid: 7});
        assert.ok(notify, 'Notify instance is created');
        assert.strictEqual(
            notify.attributes.iid, 7, 'Notify gets the correct id');
    });

    QUnit.test('url() should return correct url', function(assert) {
        assert.expect(1);

        var notify = new Notify({iid: 7});
        assert.strictEqual(
            notify.url(), '/drf/notify/7/', 'returns the correct url');
    });
});
