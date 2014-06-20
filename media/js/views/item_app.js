define([
    'jquery',
    'underscore',
    'backbone',
    'models/item',
    'models/notify'
], function($, _, Backbone, Item, Notify){
    var ItemView = Backbone.View.extend(
        {
            tagName: 'div',
            template: _.template($('#item-template').html()),
            events: {
                "change #input_notification": "updateNotificationStatus",
            },
            initialize: function () {
                this.notify = new Notify(
                    {item_id: this.model.attributes.item_id});

                $('#input_notification')
                    .on('change',
                        {notify: this.notify},
                        this.updateNotificationStatus);
            },
            render: function () {
                this.$el.html(this.template(this.model.attributes));
                return this;
            },
            updateNotificationStatus: function(e) {
                var isEnabled = e.target.checked;
                var notify = e.data.notify;
                if (isEnabled) {
                    // create a notify object
                    notify.save();
                } else {
                    // delete the notify
                    notify.destroy();
                }
            }
        });
    return ItemView;
});
