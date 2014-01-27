define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone) {

    var Client = Backbone.Model.extend({
        idAttribute: "client_id",
        defaults: function() {
            return {
                lastname: "",
                firstname: "",
                status: "active",
                title: "Instructor",
                registration_date: "",
                email: "",
                department: "",
                school: "",
                add_affiliation: "",
                phone: "",
                comments: "",
                email_secondary: "",
                phone_mobile: "",
                phone_other: "",
                website_url: ""
            };
        },

        url: function() {
            return "/drf/clients/" + this.get('client_id') + "/";
        },

        initialize: function() {
        },

        toFullJSON: function() {
            var j = this.toJSON();
            j['active'] = j['status'] == 'active';
            return j;
        }
    });

  return Client;
});
