define([
    'jquery',
    'underscore',
    'backbone',
    'models/client'
], function($, _, Backbone, Entry, EntryList){
    var ClientView = Backbone.View.extend({
        tagName: 'div',
        template: _.template($('#client-template').html()),
        events: {
            "keypress input" : "updateOnEnter"
        },
        initialize: function () {
            this.model.bind('change', this.render, this);
            this.model.bind('remove', this.remove, this);
        },
        remove: function() {
            $(this.el).remove();
        },
        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        },
        updateOnEnter: function(e) {
            if (e.keyCode == 13) {
                console.log("updating");
                this.model.set('status', this.$(".status-input").val());
                this.model.set('lastname', this.$(".lastname-input").val());
                this.model.set('firstname', this.$(".lastname-input").val());
                this.model.set('title', this.$(".title-input").val());
                this.model.set('department', this.$(".department-input").val());
                this.model.set('school', this.$(".school-input").val());
                this.model.set('email', this.$(".email-input").val());
                this.model.set('phone', this.$(".phone-input").val());
                this.model.set('phone_mobile', this.$(".phone_mobile-input").val());
                this.model.set('phone_other', this.$(".phone_other-input").val());
                this.model.set('email_secondary', this.$(".email_secondary-input").val());
                this.model.set('registration_date', this.$(".registration_date-input").val());
                this.model.set('website_url', this.$(".website_url-input").val());
                this.model.save();
            }
        }
    });
    return ClientView;
});
