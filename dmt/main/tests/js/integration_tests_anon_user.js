casper.test.comment('Casper integration tests');

var helper = require('./support/djangocasper.js');

helper.scenario('/',
    function() {
        this.test.assertTitle('DMT: Welcome! Please log in', 'The title is correct');
    },
    function() {
        this.test.assertElementCount('a[href="/accounts/login/?next=/"]', 1,
                                     'The homepage has a login button');

        this.test.assertElementCount('a[href="/client/"]', 1,
                                     'The homepage has a clients button');
    }
);
helper.scenario('/client/',
    function() {
        this.test.assertTitle('DMT: Welcome! Please log in',
            'The title remains the same when trying to navigate somewhere');
        helper.assertAbsUrl('/accounts/login/\?next=/client/',
            'After clicking Clients, we\'re redirected to login page');
    }
);
helper.run();
