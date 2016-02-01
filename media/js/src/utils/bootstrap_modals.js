// This file is loaded with a <script> tag, not with requirejs
// because it needs the Bootstrap-aware jQuery object.

$(document).ready(function() {
    $('#add-hours').on('shown.bs.modal', function(e) {
        $(this).find('input[name="time"]').focus();
    });
});
