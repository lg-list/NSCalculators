const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const bundle = process.argv[2] || 'dist/assets/calculator.js';
const context = vm.createContext({
  document: { addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; }, getElementById() { return null; } },
  window: { addEventListener() {} }, console,
});
vm.runInContext(fs.readFileSync(bundle, 'utf8'), context, { filename: bundle });
const calculate = context.downPaymentAmounts;
assert.equal(typeof calculate, 'function');
const defaults = { mode: 'price', price: 500000, cash: 100000, downPercent: 20, includeClosing: true, closingValue: 3, closingUnit: 'percent', rate: 7.297, years: 30 };
const cases = [
  ['price to cash', {}, { price: 500000, down: 100000, closing: 15000, cashNeeded: 115000, loan: 400000 }],
  ['cash to price', { mode: 'cash' }, { price: 100000 / .23, down: 20000 / .23, closing: 3000 / .23, cashNeeded: 100000, loan: 80000 / .23 }],
  ['price and cash to down', { mode: 'both' }, { down: 85000, downPercent: 17, loan: 415000, cashNeeded: 100000 }],
  ['fixed closing cash mode', { mode: 'cash', closingUnit: 'dollars', closingValue: 10000 }, { price: 450000, closing: 10000, down: 90000, loan: 360000 }],
  ['fixed closing price mode', { closingUnit: 'dollars', closingValue: 10000 }, { cashNeeded: 110000, closing: 10000 }],
  ['fixed closing both mode', { mode: 'both', closingUnit: 'dollars', closingValue: 10000 }, { down: 90000, downPercent: 18 }],
  ['excluded closing', { includeClosing: false, closingValue: NaN, closingUnit: 'invalid' }, { cashNeeded: 100000, closing: 0 }],
  ['cash without closing', { mode: 'cash', includeClosing: false }, { price: 500000, loan: 400000 }],
  ['zero down known price', { downPercent: 0 }, { down: 0, loan: 500000, cashNeeded: 15000 }],
  ['zero down cash-based fees', { mode: 'cash', downPercent: 0 }, { price: 100000 / .03, down: 0, closing: 100000 }],
  ['zero interest', { rate: 0 }, { payment: 400000 / 360, totalInterest: 0 }],
  ['standard amortization', { rate: 6 }, { payment: 2398.202100611028 }],
  ['one month', { years: 1 / 12, rate: 0 }, { months: 1, payment: 400000 }],
  ['all cash purchase', { downPercent: 100 }, { loan: 0, payment: 0, cashNeeded: 515000 }],
  ['surplus cash', { mode: 'both', cash: 600000 }, { downPercent: 100, down: 500000, loan: 0, payment: 0, unusedCash: 85000, cashNeeded: 515000 }],
  ['cash covers only closing', { mode: 'both', cash: 15000 }, { down: 0, downPercent: 0, loan: 500000 }],
  ['zero purchase cash zero-down known price', { mode: 'both', cash: 0, includeClosing: false }, { down: 0, loan: 500000 }],
  ['ignore inactive price', { mode: 'cash', price: NaN }, { cashNeeded: 100000 }],
  ['ignore inactive cash', { cash: NaN }, { cashNeeded: 115000 }],
  ['ignore inactive percent', { mode: 'both', downPercent: NaN }, { downPercent: 17 }],
  ['tiny nonzero rate', { rate: 1e-12 }, { payment: 400000 / 360 }],
];
for (const [label, overrides, expected] of cases) {
  const result = calculate({ ...defaults, ...overrides });
  assert.equal(result.valid, true, label);
  for (const [key, value] of Object.entries(expected)) assert.ok(Math.abs(result[key] - value) < 1e-6, `${label}: ${key} ${result[key]} != ${value}`);
  assert.ok(Math.abs(result.loan + result.down - result.price) < 1e-6, label);
  assert.ok(Math.abs(result.down + result.closing - result.cashNeeded) < 1e-6, label);
  assert.ok(result.loan >= 0 && result.unusedCash >= 0, label);
}
// Independently observed reference outputs, rounded there to whole dollars.
for (const [mode, payment] of [['cash', 2384], ['price', 2741], ['both', 2844]]) {
  assert.equal(Math.round(calculate({ ...defaults, mode }).payment), payment, mode);
}
const invalid = [
  { mode: 'unknown' }, { includeClosing: 'true' }, { price: 0 }, { price: -1 }, { price: NaN },
  { price: '500000' }, { mode: 'cash', cash: -1 }, { mode: 'both', cash: NaN },
  { downPercent: -1 }, { downPercent: 101 }, { downPercent: NaN }, { rate: -1 }, { rate: 101 }, { rate: NaN },
  { years: 0 }, { years: 101 }, { years: .1 }, { years: NaN }, { years: '30' },
  { closingUnit: 'unknown' }, { closingValue: -1 }, { closingValue: NaN }, { closingValue: 101 },
  { mode: 'both', cash: 14999 }, { mode: 'cash', downPercent: 0, includeClosing: false },
  { mode: 'cash', downPercent: 0, closingUnit: 'dollars', closingValue: 1 },
  { mode: 'cash', cash: 10000, closingUnit: 'dollars', closingValue: 10000 },
  { mode: 'cash', cash: 9999, closingUnit: 'dollars', closingValue: 10000 },
  { mode: 'cash', cash: 0 }, { mode: 'cash', cash: Number.MAX_VALUE, downPercent: .001 },
];
for (const input of invalid) assert.equal(calculate({ ...defaults, ...input }).valid, false, JSON.stringify(input));
console.log(`Passed ${cases.length} down-payment cases, 3 reference outputs and ${invalid.length} invalid cases.`);
