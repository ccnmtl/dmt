define([
    'jquery',
    'underscore',
    'backbone'
], function($, _, Backbone) {

    var Notify = Backbone.Model.extend({
        idAttribute: 'iid',
        defaults: function() {
            return {
                iid: null,
                username: null
            };
        },

        url: function() {
            return '/drf/notify/' + this.get('iid') + '/';
        },

        initialize: function() {
        },
    });

    return Notify;
});
