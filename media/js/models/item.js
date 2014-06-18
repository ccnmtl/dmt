define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone) {

    var Item = Backbone.Model.extend({
        idAttribute: "iid",
        defaults: function() {
            return {
                title: null,
                type: null,
                owner: null,
                assigned_to: null,
                milestone: null,
                status: null,
                description: null,
                priority: null,
                r_status: null,
                last_mod: null,
                target_date: null,
                estimated_time: null,
                url: null,
                notifications_enabled: null
            };
        },

        url: function() {
            return "/drf/items/" + this.get('item_id') + "/";
        },

        initialize: function() {
        },

        toFullJSON: function() {
            var j = this.toJSON();
            //j['active'] = j['status'] == 'active';
            return j;
        }
    });

  return Item;
});
