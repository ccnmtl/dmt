define([
    // libs
    'jquery',
    'underscore',
    'backbone',

    // src
    'models/notify'
], function($, _, Backbone, Notify) {
    if ($('#item-template').length === 0) {
        return;
    }

    var ItemView = Backbone.View.extend({
        tagName: 'div',
        template: _.template($('#item-template').html()),
        events: {
            'change #input_notification': 'updateNotificationStatus',
        },
        initialize: function() {
            this.notify = new Notify(
                {iid: this.model.get('iid')});

            $('#input_notification')
                .on('change',
                    {notify: this.notify},
                    this.updateNotificationStatus);
        },
        render: function() {
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
