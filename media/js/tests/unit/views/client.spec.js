/* eslint-env qunit */
define(
    [
        'jquery',
        '../../../src/views/client',
        '../../../src/models/client',
    ], function($, ClientView, Client) {
        // eslint-disable-next-line no-undef
        QUnit.test('should create an instance', function(assert) {
            assert.expect(1);

            var client = new Client({'client_id': 7});
            var view = new ClientView({
                model: client,
                el: $('#client-container')
            });
            assert.ok(view, 'Client view instance is created');
        });
    });
