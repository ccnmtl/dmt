// This file is loaded with a <script> tag, not with requirejs
// because it needs the Bootstrap-aware jQuery object.

$(document).ready(function() {
    // Fix the problem where the window's scroll is below the top
    // of the page when navigating to a tab via anchor tag and click.
    $('ul.nav a').on('shown.bs.tab', function() {
        $(window).scrollTop(0);
    });

    var hash = window.location.hash;
    if (hash) {
        var $el = $('ul.nav a[href="' + hash + '"]');
        $el.tab('show');
    }

    $('.nav-tabs a').click(function(e) {
        $(this).tab('show');
        window.location.hash = this.hash;
    });
});
