define(
    ['jquery', '../../../src/models/client'],
    function($, Client) {
        test('should be able to create an instance', function() {
            expect(2);

            var client = new Client({'client_id': 7});
            ok(client, 'Client instance is created');
            equal(client.get('client_id'), 7, 'Client gets the correct id');
        });

        test('should make correct ajax calls on save', function() {
            expect(3);

            sinon.spy($, 'ajax');

            var client = new Client({'client_id': 7});
            var email = 'test@columbia.edu';
            client.set('email', email);
            client.save();

            ok($.ajax.calledOnce, 'made an ajax request');
            equal($.ajax.getCall(0).args[0].url, '/drf/clients/7/',
                  'called correct url');
            ok($.ajax.getCall(0).args[0].data.match(email),
               'has correct data in payload');
        });

        test('url() should return correct url', function() {
            expect(1);

            var client = new Client({'client_id': 7});
            equal(client.url(), '/drf/clients/7/', 'returns the correct url');
        });
    });
