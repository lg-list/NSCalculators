const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const bundle = process.argv[2] || 'dist/assets/calculator.js';
const context = vm.createContext({
  document: { addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; }, getElementById() { return null; } },
  window: { addEventListener() {} }, console,
});
vm.runInContext(fs.readFileSync(bundle, 'utf8'), context, { filename: bundle });
const calculate = context.k401EmployerMatch;
assert.equal(typeof calculate, 'function');
const defaults = { salary: 75000, age: 35, enteredRate: .06, rate1: 1, limit1: .03, rate2: .5, limit2: .02 };
const cases = [
  ['two-tier default', {}, { employee: 4500, employer: 3000, fullRate: 5, fullMatchPossible: true }],
  ['partial second tier', { enteredRate: .04 }, { employee: 3000, employer: 2625, captured: 87.5 }],
  ['first tier only', { rate2: 0 }, { employer: 2250, fullRate: 3, requiredEmployee: 2250 }],
  ['zero-width second tier', { limit2: 0 }, { employer: 2250, fullRate: 3 }],
  ['no employer match', { rate1: 0, rate2: 0 }, { employer: 0, fullRate: 0, captured: 100 }],
  ['unpaid first band before paid second', { rate1: 0 }, { employer: 750, fullRate: 5 }],
  ['zero contributions', { enteredRate: 0 }, { employee: 0, employer: 0, captured: 0 }],
  ['compensation ceiling', { salary: 500000, enteredRate: .1, rate2: 0 }, { employee: 24500, eligibleSalary: 360000, employer: 10800, fullRate: 2.16 }],
  ['unreachable deferral requirement', { salary: 360000, limit1: .1, rate2: 0 }, { employee: 21600, employer: 21600, fullRate: 10, fullMatchPossible: false }],
  ['annual additions cap', { salary: 360000, enteredRate: .1, rate1: 3, limit1: .1, rate2: 0 }, { employee: 24500, formulaEmployer: 73500, employer: 47500, combined: 72000, fullMatchPossible: false }],
  ['age 50 catch-up excluded from additions', { salary: 360000, age: 50, enteredRate: .1, rate1: 3, limit1: .1, rate2: 0 }, { employee: 32500, employer: 47500, combined: 80000 }],
  ['age 60 enhanced catch-up', { salary: 360000, age: 60, enteredRate: .1, rate1: 3, limit1: .1, rate2: 0 }, { employee: 35750, employer: 47500, combined: 83250 }],
  ['age 63 enhanced catch-up', { salary: 100000, age: 63, enteredRate: .5 }, { employee: 35750 }],
  ['age 64 general catch-up', { salary: 100000, age: 64, enteredRate: .5 }, { employee: 32500 }],
  ['compensation limits total additions', { salary: 10000, enteredRate: 1, rate1: 2, limit1: .1, rate2: 0 }, { employee: 10000, employer: 0, combined: 10000, annualAdditionsLimit: 10000 }],
  ['100 percent threshold', { salary: 10000, enteredRate: .5, rate1: .5, limit1: 1, rate2: 0, limit2: 0 }, { employee: 5000, employer: 2500, fullRate: 100, fullMatchPossible: false }],
];
for (const [label, overrides, expected] of cases) {
  const result = calculate({ ...defaults, ...overrides });
  assert.equal(result.valid, true, label);
  for (const [key, value] of Object.entries(expected)) {
    if (typeof value === 'number') assert.ok(Math.abs(result[key] - value) < 1e-7, `${label}: ${key}: ${result[key]} != ${value}`);
    else assert.equal(result[key], value, `${label}: ${key}`);
  }
  assert.ok(result.employee <= result.employeeCeiling + 1e-8, label);
  assert.ok(Math.min(result.employee, 24500) + result.employer <= result.annualAdditionsLimit + 1e-8, label);
}
const invalid = [{ salary: 0 }, { salary: -1 }, { age: 17 }, { age: 101 }, { enteredRate: 1.01 },
  { enteredRate: -.01 }, { rate1: -1 }, { limit1: .99, limit2: .02 }, { rate2: NaN }, { salary: Infinity }];
for (const overrides of invalid) assert.equal(calculate({ ...defaults, ...overrides }).valid, false);
console.log(`Passed ${cases.length} employer-match cases and ${invalid.length} validation cases.`);
