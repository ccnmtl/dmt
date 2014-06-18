define([
    'jquery',
    'underscore',
    'backbone',
    'models/item'
], function($, _, Backbone, Entry, EntryList){
    var ItemView = Backbone.View.extend(
        {
            tagName: 'div',
            template: _.template($('#item-template').html()),
            events: {
                /*"click #save" : "updateFromForm",
                "click #activate" : "toggleActive",
                "click #edit-link": "toggleEditForm"*/
            },
            initialize: function () {
                //this.model.bind('change', this.render, this);
                //this.model.bind('remove', this.remove, this);
            },
            remove: function() {
                //$(this.el).remove();
            },
            render: function () {
                this.$el.html(this.template(this.model.toFullJSON()));
                return this;
            },
            toggleEditForm: function(e) {
                //this.$("#view").toggle();
                //this.$("#edit").toggle();
                e.preventDefault();
            },
            toggleActive: function() {
                /*this.model.set(
                    'status',
                    this.model.get('status') == 'active' ? 'inactive' : 'active');
                this.model.save();*/
            },
            updateFromForm: function(e) {
                //this.model.set('lastname', this.$(".lastname-input").val());
                this.model.save();
            }
        });
    return ItemView;
});
