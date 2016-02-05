define([
    '../../../src/utils/utils'
], function(Utils) {
    test('should be able to compare dates', function() {
        ok(Utils.compareDates('2015-06-25', '2015-06-29'));
        ok(!Utils.compareDates('2015-06-25', '2015-06-24'));
        ok(Utils.compareDates('2015-06-25', 'abc'));
        ok(Utils.compareDates('2015-06-25', NaN));
        ok(!Utils.compareDates(1, 0));
        ok(Utils.compareDates(0, 1));
    });
});
