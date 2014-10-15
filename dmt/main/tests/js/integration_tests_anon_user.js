casper.test.comment('Casper integration tests');

var helper = require('./support/djangocasper.js');

helper.scenario('/',
    function() {
        this.test.assertElementCount('.login-box', 1,
                                     'The homepage has a login button');

    }
);
helper.run();
