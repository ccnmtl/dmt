define([
    'jquery',
    'underscore',
    'backbone'
], function($, _, Backbone) {

    var Item = Backbone.Model.extend({
        idAttribute: 'iid',
        defaults: function() {
            return {
                iid: null,
                title: null,
                type: null,
                'owner_user': null,
                'assigned_user': null,
                milestone: null,
                status: null,
                description: null,
                priority: null,
                'r_status': null,
                'last_mod': null,
                'target_date': null,
                'estimated_time': null,
                url: null,
                notifies: []
            };
        },

        url: function() {
            return '/drf/items/' + this.get('iid') + '/';
        },

        initialize: function() {
        },
    });

    return Item;
});
