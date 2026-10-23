const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const bundle = process.argv[2] || 'dist/assets/calculator.js';
const context = vm.createContext({
  document: { addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; }, getElementById() { return null; } },
  window: { addEventListener() {}, devicePixelRatio: 1 }, console,
});
vm.runInContext(fs.readFileSync(bundle, 'utf8'), context, { filename: bundle });
const calculate = context.bodyFatAmounts;
assert.equal(typeof calculate, 'function');
const defaults = { units: 'us', method: 'tape', sex: 'male', age: 25, height: 70.5, weight: 152, neck: 19.5, waist: 37.5, hip: 34.5 };
const male = 15.27697422074079, female = 21.813093408181402;
const cases = [
  ['reference circumference', {}, { percent: male, fat: 23.221000815525998, lean: 128.778999184474, bmiFat: 15.351497173418373 }],
  ['female circumference coefficients', { sex: 'female' }, { percent: female, bmiFat: 26.15149717341837 }],
  ['BMI male', { method: 'bmi' }, { percent: 15.351497173418373 }],
  ['BMI female', { method: 'bmi', sex: 'female' }, { percent: 26.15149717341837 }],
  ['metric equivalent', { units: 'metric', height: 179.07, weight: 68.94604024, neck: 49.53, waist: 95.25, hip: 87.63 }, { percent: male, fatKg: 10.53286879368637 }],
  ['ignore male hip', { hip: NaN }, { percent: male }],
  ['ignore all tape fields in BMI mode', { method: 'bmi', neck: NaN, waist: -1, hip: NaN }, { percent: 15.351497173418373 }],
  ['age does not alter circumference', { age: 50 }, { percent: male, bmiFat: 21.10149717341837 }],
  ['weight changes mass not circumference', { weight: 200 }, { percent: male, fat: 200 * male / 100 }],
  ['BMI cross-check out of sample', { weight: 400 }, { percent: male, bmiFat: null }],
  ['youngest supported adult', { age: 18 }, { percent: male }],
  ['oldest supported adult', { age: 83 }, { percent: male }],
];
for (const [label, overrides, expected] of cases) {
  const input = { ...defaults, ...overrides }, result = calculate(input);
  assert.equal(result.valid, true, label);
  for (const [key, value] of Object.entries(expected)) {
    if (value === null) assert.equal(result[key], null, `${label}/${key}`);
    else assert.ok(Math.abs(result[key] - value) < 1e-6, `${label}/${key}: ${result[key]} != ${value}`);
  }
  assert.ok(Math.abs(result.fat + result.lean - input.weight) < 1e-7, label);
  assert.ok(Math.abs(result.fatKg + result.leanKg - input.weight * (input.units === 'us' ? .45359237 : 1)) < 1e-7, label);
}
const invalid = [{ units: 'other' }, { method: 'other' }, { sex: 'other' }, { age: 17 }, { age: 84 }, { age: 25.5 },
  { waist: 19.5 }, { waist: 10 }, { sex: 'female', hip: 0 }, { sex: 'female', neck: 100 },
  { waist: 1e100 }, { method: 'bmi', weight: 400 }, { method: 'bmi', weight: 50 }, { height: 1e-300 }];
for (const key of ['age', 'height', 'weight', 'neck', 'waist']) {
  for (const value of [-1, 0, NaN, Infinity, '25']) invalid.push({ [key]: value });
}
for (const input of invalid) assert.equal(calculate({ ...defaults, ...input }).valid, false, JSON.stringify(input));
// Capture chart text: percentages must not inherit a dollar or monthly-payment label.
for (const percent of [true, false]) {
  const texts = [], ctx = new Proxy({ fillText: text => texts.push(text) }, { get: (o, k) => k in o ? o[k] : () => {} });
  const canvas = { dataset: percent ? { valueFormat: 'percent', centerLabel: 'of body weight' } : {}, width: 320, height: 220, style: {}, getAttribute: key => key === 'width' ? '320' : '220', getContext: () => ctx };
  context.drawPie(canvas, percent ? [15.3, 84.7] : [100, 200], ['Fat', 'Fat-free']);
  if (percent) {
    assert.ok(texts.includes('100%') && texts.includes('15.3%'));
    assert.equal(texts.some(x => x.includes('$') || x.includes('per month')), false);
  } else assert.ok(texts.includes('$300') && texts.includes('$100.00') && texts.includes('per month'));
}
console.log(`Passed ${cases.length} body-fat scenarios, ${invalid.length} invalid cases and 2 chart-format checks.`);
