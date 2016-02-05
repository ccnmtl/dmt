require([
    'domReady',
    'jquery'
], function(domReady, $) {
    /**
     * Compare two date strings, returning true if start is before end,
     * otherwise returns false.
     */
    var compareDates = function(start, end) {
        var startDate = new Date(start);
        var endDate = new Date(end);
        return startDate <= endDate;
    };

    domReady(function() {
        $('.input-daterange').on('change', function(e) {
            var $el = $(this);
            var $form = $el.closest('form');
            var $submitButton = $form.find('button[type="submit"]');
            var start = $el.find('input[name="interval_start"]').val();
            var end = $el.find('input[name="interval_end"]').val();
            if (compareDates(start, end)) {
                $form.find('.daterange-invalid').addClass('hidden');
                $submitButton.prop('disabled', false);
                $submitButton.removeClass('disabled');
            } else {
                $form.find('.daterange-invalid').removeClass('hidden');
                $submitButton.prop('disabled', true);
                $submitButton.addClass('disabled');
            }
        });
    });
});
