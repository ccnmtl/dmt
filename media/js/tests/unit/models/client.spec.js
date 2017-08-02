/* eslint-env qunit */
/* global sinon */
define(
    ['jquery', '../../../src/models/client'],
    function($, Client) {
        QUnit.test('should be able to create an instance', function(assert) {
            assert.expect(2);

            var client = new Client({'client_id': 7});
            assert.ok(client, 'Client instance is created');
            assert.strictEqual(
                client.get('client_id'), 7, 'Client gets the correct id');
        });

        QUnit.test('should make correct ajax calls on save', function(assert) {
            assert.expect(3);

            sinon.spy($, 'ajax');

            var client = new Client({'client_id': 7});
            var email = 'test@columbia.edu';
            client.set('email', email);
            client.save();

            assert.ok($.ajax.calledOnce, 'made an ajax request');
            assert.strictEqual(
                $.ajax.getCall(0).args[0].url,
                '/drf/clients/7/',
                'called correct url');
            assert.ok(
                $.ajax.getCall(0).args[0].data.match(email),
                'has correct data in payload');
        });

        QUnit.test('url() should return correct url', function(assert) {
            assert.expect(1);

            var client = new Client({'client_id': 7});
            assert.strictEqual(
                client.url(), '/drf/clients/7/', 'returns the correct url');
        });
    });
