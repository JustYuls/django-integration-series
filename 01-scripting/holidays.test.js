const test = require("node:test");
const assert = require("node:assert");
const { isWeekday, formatHoliday } = require("./holidays.js");

test("a Friday is a weekday", () => {
  assert.strictEqual(isWeekday({ date: "2027-01-01" }), true);
});

test("a Saturday is not a weekday", () => {
  assert.strictEqual(isWeekday({ date: "2027-02-06" }), false);
});

test("a holiday is formatted for printing", () => {
  assert.strictEqual(formatHoliday({ date: "2027-01-01", name: "New Year's Day" }), "2027-01-01  New Year's Day");
});
