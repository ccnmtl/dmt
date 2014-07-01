define(
    [
        'jquery',
        '../../../src/views/client',
        '../../../src/models/client',
    ], function($, ClientView, Client) {
        test('should create an instance', function() {
            expect(1);

            var client = new Client({'client_id': 7});
            var view = new ClientView({model: client,
                                       el: $('#client-container')});
            ok(view, 'Client view instance is created');
        });
    });
