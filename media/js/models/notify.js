define([
    'jquery',
    'underscore',
    'backbone'
], function($, _, Backbone) {

    var Notify = Backbone.Model.extend({
        idAttribute: "item_id",
        defaults: function() {
            return {
                item_id: null,
                username: null
            };
        },

        url: function() {
            return "/drf/notify/" + this.get('item_id') + "/";
        },

        initialize: function() {
        },
    });

  return Notify;
});
