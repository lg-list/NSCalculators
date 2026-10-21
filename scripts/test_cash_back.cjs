const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const bundle = process.argv[2] || 'dist/assets/calculator.js';
const context = vm.createContext({
  document: { addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; }, getElementById() { return null; } },
  window: { addEventListener() {} }, console,
});
vm.runInContext(fs.readFileSync(bundle, 'utf8'), context, { filename: bundle });
const calculate = context.cashBackAmounts;
assert.equal(typeof calculate, 'function');
const defaults = { price: 50000, rebate: 1000, highRate: 5, lowRate: 2, months: 60, down: 10000, trade: 0, fees: 2000, financeFees: false, taxMode: 'calculated', taxRate: 7, rebateReducesTax: false, tradeReducesTax: true, quotedCashTax: 3500, quotedLowTax: 3500 };
const close = (actual, expected, label) => assert.ok(Math.abs(actual - expected) < .005, `${label}: ${actual} != ${expected}`);
const cases = [
  ['reference inputs', {}, { winner: 'low', savings: 2092.06, cash: { loan: 39000, tax: 3500, upfront: 15500, payment: 735.98, totalPayments: 44158.69, interest: 5158.69, cost: 59658.69 }, low: { loan: 40000, payment: 701.11, totalPayments: 42066.62, interest: 2066.62, cost: 57566.62 } }],
  ['large rebate', { rebate: 5000 }, { winner: 'cash', cash: { loan: 35000 } }],
  ['no rebate identical rates', { rebate: 0, highRate: 2 }, { winner: 'tie', savings: 0 }],
  ['zero rates', { highRate: 0, lowRate: 0 }, { winner: 'cash', savings: 1000, cash: { payment: 650, interest: 0, cost: 54500 }, low: { cost: 55500 } }],
  ['zero promo', { lowRate: 0 }, { winner: 'low', low: { payment: 40000 / 60, interest: 0, cost: 55500 } }],
  ['finance tax and fees at zero rates', { financeFees: true, highRate: 0, lowRate: 0 }, { savings: 1000, cash: { loan: 44500, upfront: 10000, cost: 54500 }, low: { loan: 45500, upfront: 10000, cost: 55500 } }],
  ['finance fees with interest', { financeFees: true }, { winner: 'low', cash: { loan: 44500, upfront: 10000 }, low: { loan: 45500 } }],
  ['debt-free trade credit', { trade: 10000, highRate: 0, lowRate: 0 }, { cash: { loan: 29000, tax: 2800, upfront: 14800, cost: 53800 }, low: { cost: 54800 } }],
  ['trade does not reduce tax', { trade: 10000, tradeReducesTax: false, highRate: 0, lowRate: 0 }, { cash: { tax: 3500, cost: 54500 } }],
  ['rebate reduces tax', { rebateReducesTax: true }, { savings: 2022.06, cash: { tax: 3430 }, low: { tax: 3500 } }],
  ['quote replaces tax, not adds', { taxMode: 'quoted', quotedCashTax: 0, quotedLowTax: 3500 }, { winner: 'cash', savings: 1407.94, cash: { tax: 0 }, low: { tax: 3500 } }],
  ['inactive calculated tax ignored', { taxMode: 'quoted', taxRate: NaN, rebateReducesTax: undefined, tradeReducesTax: undefined }, { winner: 'low', savings: 2092.06 }],
  ['inactive quotes ignored', { quotedCashTax: NaN, quotedLowTax: NaN }, { winner: 'low', savings: 2092.06 }],
  ['cash purchase surplus', { down: 100000 }, { winner: 'cash', savings: 1000, cash: { loan: 0, payment: 0, downUsed: 49000, unusedDown: 51000, upfront: 54500, cost: 54500 }, low: { unusedDown: 50000, cost: 55500 } }],
  ['all costs paid from down budget', { down: 100000, financeFees: true }, { cash: { loan: 0, unusedDown: 45500, upfront: 54500 }, low: { unusedDown: 44500 } }],
  ['no taxes or fees', { taxRate: 0, fees: 0, highRate: 0, lowRate: 0 }, { cash: { cost: 49000 }, low: { cost: 50000 } }],
  ['one monthly payment', { months: 1 }, { winner: 'cash', cash: { payment: 39162.5, interest: 162.5 } }],
  ['maximum modeled term', { months: 600 }, { winner: 'low' }],
  ['rebate plus trade equals price', { trade: 49000, highRate: 0, lowRate: 0 }, { cash: { loan: 0, downUsed: 0, unusedDown: 10000, cost: 51070 }, low: { loan: 0, downUsed: 1000, cost: 52070 } }],
  ['higher promo rate is not presumed cheaper', { rebate: 0, lowRate: 10 }, { winner: 'cash' }],
  ['very small rate', { highRate: 1e-12, lowRate: 0 }, { cash: { payment: 650, interest: 0 } }],
];
for (const [label, overrides, expected] of cases) {
  const input = { ...defaults, ...overrides }, result = calculate(input);
  assert.equal(result.valid, true, label);
  for (const [key, value] of Object.entries(expected)) {
    if (typeof value === 'object') for (const [metric, amount] of Object.entries(value)) close(result[key][metric], amount, `${label}/${key}/${metric}`);
    else if (typeof value === 'number') close(result[key], value, `${label}/${key}`);
    else assert.equal(result[key], value, `${label}/${key}`);
  }
  for (const offer of [result.cash, result.low]) {
    close(offer.cost, input.price - offer.rebate + offer.tax + input.fees + offer.interest, `${label}/cost identity`);
    close(offer.loan + offer.downUsed, input.price - offer.rebate - input.trade + (input.financeFees ? offer.tax + input.fees : 0), `${label}/funding identity`);
    assert.ok(offer.loan >= 0 && offer.unusedDown >= 0, label);
  }
}
const invalid = [
  { price: 0 }, { rebate: 50001 }, { trade: 49001 }, { months: 0 }, { months: 601 }, { months: 60.5 },
  { highRate: 101 }, { lowRate: 101 }, { financeFees: 'yes' }, { taxMode: 'unknown' },
  { taxRate: 101 }, { rebateReducesTax: 'yes' }, { tradeReducesTax: undefined },
  { taxMode: 'quoted', quotedCashTax: NaN }, { taxMode: 'quoted', quotedLowTax: -1 },
  { price: Number.MAX_VALUE, fees: Number.MAX_VALUE, financeFees: true },
];
for (const key of ['price', 'rebate', 'highRate', 'lowRate', 'months', 'down', 'trade', 'fees', 'taxRate']) {
  for (const value of [-1, NaN, Infinity, '10']) invalid.push({ [key]: value });
}
for (const input of invalid) assert.equal(calculate({ ...defaults, ...input }).valid, false, JSON.stringify(input));
console.log(`Passed ${cases.length} rebate-comparison scenarios and ${invalid.length} invalid cases.`);
