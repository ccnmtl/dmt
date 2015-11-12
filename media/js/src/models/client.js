define([
    'jquery',
    'underscore',
    'backbone'
], function($, _, Backbone) {

    var Client = Backbone.Model.extend({
        idAttribute: 'client_id',
        defaults: function() {
            return {
                lastname: null,
                firstname: null,
                status: 'active',
                title: 'Instructor',
                'registration_date': null,
                email: null,
                department: null,
                school: null,
                'add_affiliation': null,
                phone: null,
                comments: null,
                'email_secondary': null,
                'phone_mobile': null,
                'phone_other': null,
                'website_url': null
            };
        },

        url: function() {
            return '/drf/clients/' + this.get('client_id') + '/';
        },

        initialize: function() {
        },

        toFullJSON: function() {
            var j = this.toJSON();
            j.active = j.status === 'active';
            return j;
        }
    });

    return Client;
});
