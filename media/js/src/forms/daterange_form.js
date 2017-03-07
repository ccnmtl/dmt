require([
    'domReady',
    'jquery',
    'utils/utils'
], function(domReady, $, Utils) {
    domReady(function() {
        var $daterange = $('.input-daterange');
        var $form = $daterange.closest('form');

        $daterange.on('change', function(e) {
            var start = $form.find('input[name="interval_start"]').val();
            var end = $form.find('input[name="interval_end"]').val();
            if (Utils.compareDates(start, end)) {
                $form.find('.daterange-invalid').addClass('hidden');
            }
        });

        $form.on('submit', function(e) {
            var start = $form.find('input[name="interval_start"]').val();
            var end = $form.find('input[name="interval_end"]').val();
            if (!Utils.compareDates(start, end)) {
                e.preventDefault();
                $form.find('.daterange-invalid').removeClass('hidden');
            } else {
                $form.find('.daterange-invalid').addClass('hidden');
            }
        });
    });
});
