casper.test.comment('Casper integration tests');

var helper = require('./support/djangocasper.js');

helper.scenario('/',
    function() {
        this.test.assertDoesntExist('.login-box',
                                    'There is no login box');

        this.test.assertElementCount('a[href="/client/"]', 1,
                                     'The homepage has a clients button');
    },
    function() {
        // Test that typeahead works
        this.click('a[data-target="#add-tracker"]');
        this.fill('form#add-tracker-form', {
            project: 'Test'
        });

        // FIXME: the navbar is getting in the way of casper seeing
        // typeahead here.
        //
        //this.captureSelector('/tmp/casper.png', 'body');
        /*
        this.test.assertElementCount(
                'form#add-tracker-form .tt-dataset-results div', 1,
                'typeahead populates the results div');
        this.test.assertSelectorHasText(
                'form#add-tracker-form .tt-dataset-results', 'Test Project',
                'typeahead gets the right project data');
        */
    }
);

helper.scenario('/client/',
    function() {
        this.click('a[href="/client/"]');
        helper.assertAbsUrl('/client/',
            'Clicking /client/ link navigates to clients page');
    }
);

helper.scenario('/my_projects/',
    function() {
        this.click('button.add-todo');

        // FIXME: figure out why this doesn't pass
        //this.test.assertVisible(
        //    '#add-todo-form .modal-dialog',
        //    'Clicking "Add TODO" opens a modal dialog');
    }
);

helper.run();
