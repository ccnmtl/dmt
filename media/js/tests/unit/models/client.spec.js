define(['../../../src/models/client'], function(Client) {
    QUnit.test('Client model tests', function(assert) {
        expect(2);

        var client = new Client({client_id: 7});
        assert.ok(client, 'Client instance is created');
        assert.equal(client.attributes.client_id, 7,
                     'Client gets the correct id');
    });

    QUnit.test('Client.url', function(assert) {
        expect(1);

        var client = new Client({client_id: 7});
        assert.equal(client.url(), '/drf/clients/7/',
                     'returns the correct url');
    });
});
