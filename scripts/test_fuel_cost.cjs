const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const values = new Map();
const context = vm.createContext({ document: { addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; }, getElementById(id) { return values.has(id) ? { value: values.get(id) } : null; } }, window: { addEventListener() {} }, console });
const bundle = process.argv[2] || 'dist/assets/calculator.js';
vm.runInContext(fs.readFileSync(bundle, 'utf8'), context, { filename: bundle });
const calculate = context.fuelCostAmounts;
assert.equal(typeof calculate, 'function');
const defaults = { oneWay: 650, distanceUnit: 'miles', tripType: 1, trips: 1, extraDistance: 0, efficiency: 28, efficiencyUnit: 'us_mpg', price: 3.6, priceUnit: 'us_gallon', currency: 'USD', reservePercent: 10, otherCosts: 0, people: 1 };
function near(actual, expected, label) { assert.ok(Math.abs(actual - expected) <= 1e-9 * Math.max(1, Math.abs(expected)), `${label}: ${actual} != ${expected}`); }
const scenarios = [
  ['default', {}, { fuelCost: 650 / 28 * 3.6, totalBudget: 650 / 28 * 3.6 * 1.1 }],
  ['round trip', { tripType: 2 }, { totalDistance: 1300, fuelCost: 1300 / 28 * 3.6 }],
  ['repeated trips and one detour', { tripType: 2, trips: 2, extraDistance: 40, people: 4 }, { totalDistance: 2640, fuelCost: 339.42857142857144, totalBudget: 373.37142857142857, perPerson: 93.34285714285714 }],
  ['zero fuel price is explicit', { price: 0, otherCosts: 12, people: 3 }, { fuelCost: 0, totalBudget: 12, perPerson: 4 }],
  ['zero budget', { price: 0, reservePercent: 0 }, { fuelCost: 0, totalBudget: 0, perPerson: 0 }],
  ['buffer and shared costs', { oneWay: 100, efficiency: 20, price: 4, tripType: 2, trips: 3, extraDistance: 20, otherCosts: 10, people: 4 }, { totalDistance: 620, fuelCost: 124, totalBudget: 146.4, perPerson: 36.6 }],
  ['maximum supported buffer', { reservePercent: 200 }, { fuelBudget: 650 / 28 * 3.6 * 3 }],
];
for (const [label, overrides, expected] of scenarios) {
  const result = calculate({ ...defaults, ...overrides });
  assert.equal(result.valid, true, label);
  for (const [key, value] of Object.entries(expected)) near(result[key], value, `${label}/${key}`);
}
// Same physical trip: 100 km at 10 km/L, fuel at 1.5 currency units/L.
// Exercise every independent distance, efficiency, pump-price and currency choice.
let combinations = 0;
const usL = 3.785411784, impL = 4.54609, mileKm = 1.609344;
for (const distanceUnit of ['miles', 'kilometers']) {
  for (const [efficiencyUnit, efficiency] of Object.entries({ us_mpg: 10 * usL / mileKm, imperial_mpg: 10 * impL / mileKm, km_l: 10, l_100km: 10 })) {
    for (const [priceUnit, price] of Object.entries({ us_gallon: 1.5 * usL, imperial_gallon: 1.5 * impL, liter: 1.5 })) {
      for (const currency of ['USD', 'GBP', 'EUR', 'CAD']) {
        const p = calculate({ ...defaults, oneWay: distanceUnit === 'miles' ? 100 / mileKm : 100, distanceUnit, efficiencyUnit, efficiency, priceUnit, price, currency, reservePercent: 0, people: 2 });
        assert.equal(p.valid, true);
        near(p.liters, 10, 'liters'); near(p.fuelCost, 15, 'fuel cost'); near(p.perPerson, 7.5, 'share');
        near(p.km, 100, 'km'); near(p.l100, 10, 'L/100km');
        near(p.usGallons * usL, p.imperialGallons * impL, 'gallon equivalence');
        assert.equal(p.currency, currency);
        combinations++;
      }
    }
  }
}
const invalid = [{ distanceUnit: 'other' }, { efficiencyUnit: 'other' }, { priceUnit: 'other' }, { currency: 'JPY' }, { tripType: 3 }, { tripType: '1' }, { trips: 1.5 }, { trips: 0 }, { people: 1.5 }, { people: 0 }, { reservePercent: 201 }, { trips: Number.MAX_SAFE_INTEGER + 1 }, { people: Number.MAX_SAFE_INTEGER + 1 }, { oneWay: 1e308, trips: 10 }, { efficiency: 1e-320 }, { efficiency: 1e308, oneWay: 1e-308 }, { price: 1e308 }, { oneWay: 1e-320, efficiency: 1e300 }];
for (const key of ['oneWay', 'efficiency']) for (const value of [0, -1, NaN, Infinity, '10', null]) invalid.push({ [key]: value });
for (const key of ['price', 'extraDistance', 'reservePercent', 'otherCosts']) for (const value of [-1, NaN, Infinity, '10', null]) invalid.push({ [key]: value });
for (const key of ['trips', 'people']) for (const value of [-1, NaN, Infinity, '10', null]) invalid.push({ [key]: value });
for (const input of invalid) assert.equal(calculate({ ...defaults, ...input }).valid, false, JSON.stringify(input));

const domDefaults = { distance: '650', distance_unit: 'miles', trip_type: '1', trips: '1', extra_distance: '0', efficiency: '28', efficiency_unit: 'us_mpg', fuelprice: '3.60', price_unit: 'us_gallon', currency: 'USD', reserve_percent: '10', other_costs: '0', people: '1' };
function project(overrides) { values.clear(); for (const [id, value] of Object.entries({ ...domDefaults, ...overrides })) values.set(id, value); return context.fuelCostProjection(); }
for (const id of ['distance', 'efficiency', 'fuelprice', 'trips', 'people']) assert.equal(project({ [id]: '' }).valid, false, `blank ${id}`);
const optionalBlank = project({ extra_distance: '', reserve_percent: '', other_costs: '' });
assert.equal(optionalBlank.valid, true); near(optionalBlank.totalBudget, 650 / 28 * 3.6, 'blank optional values');
assert.equal(project({ fuelprice: '0' }).valid, true);
assert.equal(project({ trips: '1.5' }).valid, false);
assert.equal(project({ people: '1.5' }).valid, false);
console.log(`Passed ${scenarios.length} trip scenarios, ${combinations} unit/currency combinations, ${invalid.length} invalid cases and 9 DOM input checks.`);
