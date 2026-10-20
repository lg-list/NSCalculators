const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const bundle = process.argv[2] || 'dist/assets/calculator.js';
const context = vm.createContext({
  document: { addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; }, getElementById() { return null; } },
  window: { addEventListener() {} }, console,
});
vm.runInContext(fs.readFileSync(bundle, 'utf8'), context, { filename: bundle });
const calculate = context.vehicleSaleComparison;
assert.equal(typeof calculate, 'function');
const defaults = { tradeValue: 19000, payoff: 12000, salePrice: 21000, sellingCosts: 500, taxSavings: 1140 };
const cases = [
  ['worked example', {}, { privateNet: 8500, effectiveTrade: 8140, breakEven: 20640, difference: 360, winner: 'private' }],
  ['no tax benefit', { taxSavings: 0 }, { breakEven: 19500, difference: 1500, winner: 'private' }],
  ['trade ahead', { salePrice: 20000 }, { privateNet: 7500, difference: -640, winner: 'trade' }],
  ['break-even tie', { salePrice: 20640 }, { difference: 0, winner: 'tie' }],
  ['negative equity on both routes', { payoff: 25000 }, { privateNet: -4500, effectiveTrade: -4860, difference: 360 }],
  ['payoff-independent comparison', { payoff: 0 }, { privateNet: 20500, effectiveTrade: 20140, difference: 360 }],
  ['no selling costs', { sellingCosts: 0 }, { breakEven: 20140, difference: 860 }],
  ['costs exceed proceeds', { sellingCosts: 22000 }, { privateNet: -13000, breakEven: 42140, winner: 'trade' }],
  ['explicit zero-value sale', { salePrice: 0 }, { privateNet: -12500, winner: 'trade' }],
  ['no replacement tax credit', { taxSavings: 0, salePrice: 19500 }, { difference: 0, winner: 'tie' }],
  ['decimal cents', { salePrice: 20640.25 }, { difference: .25, winner: 'private' }],
];
for (const [label, overrides, expected] of cases) {
  const input = { ...defaults, ...overrides };
  const result = calculate(input);
  assert.equal(result.valid, true, label);
  for (const [key, value] of Object.entries(expected)) {
    if (typeof value === 'number') assert.ok(Math.abs(result[key] - value) < 1e-7, `${label}: ${key}`);
    else assert.equal(result[key], value, `${label}: ${key}`);
  }
  assert.ok(Math.abs(result.difference - (input.salePrice - result.breakEven)) < 1e-7, label);
}
let invalidCount = 0;
for (const key of Object.keys(defaults)) {
  for (const value of [-1, NaN, Infinity]) {
    assert.equal(calculate({ ...defaults, [key]: value }).valid, false, `${key}: ${value}`);
    invalidCount++;
  }
}
assert.equal(context.tradeSaleComparison({}), null);
console.log(`Passed ${cases.length} vehicle-sale comparison cases and ${invalidCount} validation cases.`);
