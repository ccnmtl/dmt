define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone){

    var Client = Backbone.Model.extend({
        idAttribute: "client_id",
        defaults: function() {
            return {
                lastname: "",
                firstname: "",
                status: "active",
                email: "@columbia.edu",
                title: "Instructor",
                registration_date: "2000-09-01",
                department: "",
                school: "",
                add_affiliation: "",
                phone: "",
                contact: "/drf/users/dbeeby/",
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
        }
    });

  return Client;
});
