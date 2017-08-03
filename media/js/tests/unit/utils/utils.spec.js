/* eslint-env qunit */
define([
    '../../../src/utils/utils'
], function(Utils) {
    QUnit.test('should be able to compare dates', function(assert) {
        assert.ok(Utils.compareDates('2015-06-25', '2015-06-29'));
        assert.ok(!Utils.compareDates('2015-06-25', '2015-06-24'));
        assert.ok(Utils.compareDates('2015-06-25', 'abc'));
        assert.ok(Utils.compareDates('2015-06-25', NaN));
        assert.ok(!Utils.compareDates(1, 0));
        assert.ok(Utils.compareDates(0, 1));
    });
});
