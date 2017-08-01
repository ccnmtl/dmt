define([
    'jquery',
    'underscore',
    'backbone'
], function($, _, Backbone) {
    if ($('#client-template').length === 0) {
        return;
    }

    var ClientView = Backbone.View.extend(
        {
            tagName: 'div',
            template: _.template($('#client-template').html()),
            events: {
                'click #save': 'updateFromForm',
                'click #activate': 'toggleActive',
                'click #edit-link': 'toggleEditForm'
            },
            initialize: function() {
                this.model.bind('change', this.render, this);
                this.model.bind('remove', this.remove, this);
            },
            remove: function() {
                $(this.el).remove();
            },
            render: function() {
                this.$el.html(this.template(this.model.toFullJSON()));
                this.$('#edit').hide();
                return this;
            },
            toggleEditForm: function(e) {
                this.$('#view').toggle();
                this.$('#edit').toggle();
                e.preventDefault();
            },
            toggleActive: function() {
                this.model.set(
                    'status',
                    this.model.get('status') === 'active' ?
                        'inactive' : 'active');
                this.model.save();
            },
            updateFromForm: function(e) {
                this.model.set('lastname', this.$('.lastname-input').val());
                this.model.set('firstname', this.$('.firstname-input').val());
                this.model.set('title', this.$('.title-input').val());
                this.model.set('department', this.$('.department-input').val());
                this.model.set('school', this.$('.school-input').val());
                this.model.set('email', this.$('.email-input').val());
                this.model.set('phone', this.$('.phone-input').val());
                this.model.set(
                    'phone_mobile',
                    this.$('.phone_mobile-input').val());
                this.model.set(
                    'phone_other',
                    this.$('.phone_other-input').val());
                this.model.set(
                    'email_secondary',
                    this.$('.email_secondary-input').val());
                this.model.set(
                    'registration_date',
                    this.$('.registration_date-input').val());
                this.model.set(
                    'website_url',
                    this.$('.website_url-input').val());
                this.model.save();
            }
        });
    return ClientView;
});
