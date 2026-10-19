const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const bundle = process.argv[2] || 'dist/assets/calculator.js';
const context = vm.createContext({
  document: {
    addEventListener() {},
    querySelector() { return null; },
    querySelectorAll() { return []; },
    getElementById() { return null; },
  },
  window: { addEventListener() {} },
  console,
});
vm.runInContext(fs.readFileSync(bundle, 'utf8'), context, { filename: bundle });
const difference = context.timeDurationDifference;
assert.equal(typeof difference, 'function');

const cases = [
  ['reference default', ['08:30:00', '17:30:00'], 32400],
  ['overnight', ['22:00:00', '06:00:00'], 28800],
  ['identical times', ['08:30', '08:30'], 0],
  ['seconds borrowing', ['08:30:45', '09:31:05'], 3620],
  ['midnight to noon', ['00:00', '12:00'], 43200],
  ['one second across midnight', ['23:59:59', '00:00:00'], 1],
  ['full day with dates', ['08:30', '08:30', '2026-01-01', '2026-01-02'], 86400],
  ['date example', ['08:30', '17:30', '2026-01-01', '2026-01-02'], 118800],
  ['leap year', ['00:00', '00:00', '2024-02-28', '2024-03-01'], 172800],
  ['non-leap year', ['00:00', '00:00', '2025-02-28', '2025-03-01'], 86400],
  ['year boundary', ['23:59:59', '00:00:00', '2025-12-31', '2026-01-01'], 1],
  ['civil-clock DST convention', ['01:30', '03:30', '2026-03-08', '2026-03-08'], 7200],
  ['early Gregorian year', ['00:00', '00:00', '0001-01-01', '0001-01-02'], 86400],
];
for (const [label, inputs, seconds] of cases) {
  const result = difference(...inputs);
  assert.equal(result.valid, true, label);
  assert.equal(result.totalSeconds, seconds, label);
  assert.equal(result.totalHours, seconds / 3600, label);
  assert.equal(result.totalMinutes, seconds / 60, label);
  assert.equal(result.days * 86400 + result.hours * 3600 + result.minutes * 60 + result.seconds, seconds, label);
}
assert.equal(difference('22:00', '06:00').overnight, true);
assert.equal(difference('08:30', '17:30').overnight, false);

const invalid = [
  ['', '17:30'],
  ['08:30', ''],
  ['24:00', '12:00'],
  ['08:60', '12:00'],
  ['08:30:60', '12:00'],
  ['08:30', '17:30', '2026-02-30', '2026-03-01'],
  ['08:30', '17:30', '2025-02-29', '2025-03-01'],
  ['08:30', '17:30', '0000-01-01', '0001-01-01'],
  ['08:30', '17:30', '', '2026-01-01'],
  ['17:30', '08:30', '2026-01-01', '2026-01-01'],
  ['08:30', '17:30', '2026-01-02', '2026-01-01'],
];
for (const inputs of invalid) {
  assert.equal(difference(...inputs).valid, false, JSON.stringify(inputs));
}
console.log(`Passed ${cases.length} duration cases and ${invalid.length} validation cases.`);
