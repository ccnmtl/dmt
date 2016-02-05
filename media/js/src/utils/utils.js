define([
    'jquery'
], function($) {
    var Utils = {};

    /**
     * Compare two date strings, returning true if start is before end,
     * otherwise returns false.
     */
    Utils.compareDates = function(start, end) {
        var startDate = Date.parse(start);
        var endDate = Date.parse(end);
        if ($.isNumeric(startDate) && $.isNumeric(endDate)) {
            return startDate <= endDate;
        } else {
            // If we can't parse the dates for some reason, just
            // return true and let the server deal with it.
            return true;
        }
    };

    return Utils;
});
