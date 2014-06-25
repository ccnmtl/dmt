casper.test.comment('Casper integration tests');

var helper = require('./support/djangocasper.js');

helper.scenario('/',
    function() {
        this.test.assertTitle('DMT: Home', 'The title is correct');
    },
    function() {
        this.test.assertDoesntExist('input[type="submit"]',
                                    'There is no login button');

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
        this.click('a[href="/client/"]');
        this.test.assertTitle('DMT: Clients List',
            'Title changes to Clients List on navigation');
        helper.assertAbsUrl('/client/',
            'Clicking /client/ link navigates to clients page');
    }
);
helper.run();
