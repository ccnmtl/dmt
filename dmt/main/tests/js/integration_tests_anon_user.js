casper.test.comment('Casper integration tests');

var helper = require('./support/djangocasper.js');

helper.scenario('/',
    function() {
        this.test.assertTitle('DMT:', 'The title is correct');
    },
    function() {
        var loginButton = this.evaluate(function() {
            var button = $('input[type="submit"]');
            return button[0].value.toLowerCase();
        });
        this.test.assertEqual(loginButton, 'log in',
                             'The homepage has a login button');

        var clientsButton = this.evaluate(function() {
            var button = $('a[href="/client/"]');
            return button[0].text.toLowerCase();
        });
        this.test.assertEqual(clientsButton, 'clients',
                             'The homepage has a clients button');
    }
);
helper.scenario('/client/',
    function() {
        this.test.assertTitle('DMT:',
            'The title remains the same when trying to navigate somewhere');
        helper.assertAbsUrl('/accounts/login/\?next=/client/',
            'After clicking Clients, we\'re redirected to login page');
    }
);
helper.run();
