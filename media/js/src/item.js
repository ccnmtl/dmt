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

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// Let's kick off the application

require([
    'jquery',
    'backbone',
    'models/item',
    'views/item'
], function($, Backbone, Item, AppView) {
    if ($('#item-id').length === 0) {
        return;
    }

    var csrftoken = getCookie('csrftoken');
    var oldSync = Backbone.sync;

    Backbone.sync = function(method, model, options) {
        options.beforeSend = function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        };
        return oldSync(method, model, options);
    };

    var itemId = $('#item-id').html();
    var item = new Item({iid: itemId});
    item.fetch();
    var app = new AppView({model: item, el: $('#item-container')});
    app.render();
});
