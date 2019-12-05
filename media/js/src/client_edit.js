require.config({
    paths: {
        // Major libraries
        jquery: '../libs/jquery/jquery-min',
        underscore: '../libs/underscore/underscore-min',
        backbone: '../libs/backbone/backbone-min',

        // Require.js plugins
        text: '../libs/require/text'
    },
    urlArgs: 'bust=' +  (new Date()).getTime()
});

// Let's kick off the application

require([
    'jquery',
    'backbone',
    'models/client',
    'views/client'
], function($, Backbone, Client, AppView) {
    if ($('#client-id').length === 0) {
        return;
    }

    var oldSync = Backbone.sync;

    Backbone.sync = function(method, model, options) {
        options.beforeSend = function(xhr) {
            var token = $('meta[name="csrf-token"]').attr('content');
            xhr.setRequestHeader('X-CSRFToken', token);
        };
        return oldSync(method, model, options);
    };

    var clientId = $('#client-id').html();
    var client = new Client({'client_id': clientId});
    client.fetch();
    var app = new AppView({model: client, el: $('#client-container')});
    app.render();
});
