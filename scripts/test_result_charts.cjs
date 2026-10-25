const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const inputs = new Map();
const windowListeners = new Map(), frames = new Map();
let frameId = 0;
const context = vm.createContext({
  document: { addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; },
    getElementById(id) { return id === 'genericSummary' ? {} : inputs.has(id) ? { value: String(inputs.get(id)) } : null; } },
  window: { addEventListener(name, handler) { windowListeners.set(name, handler); }, devicePixelRatio: 1 },
  requestAnimationFrame(handler) { frames.set(++frameId, handler); return frameId; },
  cancelAnimationFrame(id) { frames.delete(id); }, console,
});
const bundle = process.argv[2] || 'dist/assets/calculator.js';
vm.runInContext(fs.readFileSync(bundle, 'utf8'), context, { filename: bundle });

// Inspect drawn geometry, not just displayed strings: negatives must extend left of zero.
let drawingCases = 0;
for (const values of [[150, 30, 120], [-100, 50, 0], [-100, -50], [0, 0], [0.001, 0.002], [NaN, Infinity, 10], [-1e308, 1e308], [1, 2, 3, 4, 5, 6]]) {
  const texts = [], fills = [], baselines = [];
  const ctx = new Proxy({ fillText: text => texts.push(String(text)), measureText: text => ({ width: String(text).length * 7 }),
    fillRect: (x, y, w, h) => fills.push({ x, y, w, h }), moveTo: x => baselines.push(x) },
  { get: (o, k) => k in o ? o[k] : () => {} });
  context.drawGenericBars({ width: 620, height: 180, getContext: () => ctx }, values.map((value, i) => ({ label: `Item ${i}`, value })));
  const finite = values.filter(Number.isFinite);
  assert.equal(baselines.length, finite.length);
  assert.equal(texts.some(text => text.includes('%')), false);
  finite.forEach((value, i) => {
    const bar = fills[i * 2 + 1], zero = baselines[i];
    assert.ok(Number.isFinite(bar.w) && bar.w >= 0);
    assert.ok(bar.y + bar.h <= 180);
    if (value < 0) assert.ok(bar.x < zero && Math.abs(bar.x + bar.w - zero) < 1e-8);
    else if (value > 0) assert.ok(Math.abs(bar.x - zero) < 1e-8 && bar.w > 0);
    else assert.equal(bar.w, 0);
  });
  drawingCases++;
}
for (const dpr of [1, 2]) {
  const canvas = { clientWidth: 262, width: 620, height: 230, dataset: {}, style: {}, getAttribute: () => '230',
    getContext: () => new Proxy({ measureText: text => ({ width: String(text).length * 8 }) }, { get: (o, k) => k in o ? o[k] : () => {} }) };
  context.window.devicePixelRatio = dpr;
  context.drawGenericBars(canvas, [{ label: 'Daily calories', value: 2000, display: '2,000 kcal/day' }]);
  assert.equal(canvas.width, 262 * dpr);
  assert.equal(canvas.height, 62 * dpr);
  assert.equal(canvas.style.height, '62px');
  assert.equal(canvas.dataset.barHeight, '230');
  drawingCases++;
}
context.window.devicePixelRatio = 1;
// A real percent-valued metric keeps its own unit, without a fabricated second percentage.
{
  const texts = [], ctx = new Proxy({ fillText: text => texts.push(text), measureText: () => ({ width: 42 }) }, { get: (o, k) => k in o ? o[k] : () => {} });
  context.drawGenericBars({ width: 620, height: 230, getContext: () => ctx }, [{ label: 'Rate', value: 25, display: '25%' }]);
  assert.ok(texts.includes('25%'));
  assert.equal(texts.some(text => /\(.*%\)/.test(text)), false);
  drawingCases++;
}
let captured;
context.renderGeneric = (cards, bars, rows) => { captured = { cards, bars, rows }; };
function render(engine, values) {
  inputs.clear();
  for (const [id, value] of Object.entries(values)) inputs.set(id, value);
  context.renderGenericFromEngine(engine);
  return captured;
}
const percentageCases = [
  ['percent_of', { pct_percent: 20, pct_value: 150 }, [150, 30, 120]],
  ['what_percent', { pct_part: 30, pct_whole: 150 }, [30, 150]],
  ['find_whole', { pct_known_part: 30, pct_known_percent: 20 }, [30, 150]],
  ['change', { pct_old: 100, pct_new: 80 }, [100, 80, -20]],
  ['difference', { pct_value_one: 80, pct_value_two: 120 }, [80, 120, 40]],
  ['adjust', { pct_base: 100, pct_adjust: 20, pct_direction: 'decrease' }, [100, -20, 80]],
];
for (const [mode, values, expected] of percentageCases) {
  const result = render('percent_advanced', { percent_mode: mode, ...values });
  assert.deepEqual(Array.from(result.bars, bar => bar.value), expected, mode);
  assert.equal(result.bars.some(bar => bar.display.includes('%')), false, mode);
}
for (const [mode, values] of [['what_percent', { pct_part: 30, pct_whole: 0 }], ['find_whole', { pct_known_part: 30, pct_known_percent: 0 }]]) {
  assert.equal(render('percent_advanced', { percent_mode: mode, ...values }).bars.length, 0);
}
const arithmetic = render('fraction_advanced', { fraction_mode: 'arithmetic', frac_a_whole: 0, frac_a_num: 1, frac_a_den: 2, frac_b_whole: 0, frac_b_num: 1, frac_b_den: 3, fraction_operation: 'subtract' });
assert.deepEqual(Array.from(arithmetic.bars, bar => bar.value), [1 / 2, 1 / 3, 1 / 6]);
for (const values of [{ fraction_mode: 'simplify', frac_simple_num: 8, frac_simple_den: 12 }, { fraction_mode: 'decimal', fraction_decimal: .75 }, { fraction_mode: 'simplify', frac_simple_num: 8, frac_simple_den: 0 }]) {
  assert.equal(render('fraction_advanced', values).bars.length, 0);
}
const energy = render('cn_calorie', { weight: 175, feet: 5, inches: 10, age: 35, sex: 'male', activity: 1.2 });
assert.equal(energy.bars.length, 2);
assert.ok(energy.bars.every(bar => bar.display.endsWith('kcal/day')));
assert.ok(energy.cards.some(card => card[0] === 'Protein range'));
const weight = render('cn_body_metric', { weight: 175, feet: 5, inches: 10 });
assert.equal(weight.bars.length, 3);
assert.ok(weight.bars.every(bar => bar.display.endsWith('lb')));
assert.ok(weight.cards.some(card => card[0] === 'BMI'));
// Height-only viewport changes must not rebuild result cards/tables or rerun projections.
let resizeCalls = 0;
const card = { hidden: false };
const resizeCanvas = { clientWidth: 262, width: 620, height: 230, dataset: {}, style: {},
  getAttribute: () => '230', closest: () => card,
  getContext: () => new Proxy({ measureText: () => ({ width: 30 }) }, { get: (o, k) => k in o ? o[k] : () => {} }) };
context.document.querySelector = () => resizeCanvas;
context.renderGenericFromEngine = () => { resizeCalls++; drawResizeChart(); };
function drawResizeChart() { context.drawGenericBars(resizeCanvas, [{ label: 'Area', value: 240, display: '240 ft2' }]); }
drawResizeChart();
context.resizeGenericBars();
assert.equal(resizeCalls, 0, 'unchanged canvas dimensions do no work');
context.window.innerHeight = 500;
context.resizeGenericBars();
assert.equal(resizeCalls, 0, 'height-only resize leaves results untouched');
resizeCanvas.clientWidth = 320;
context.resizeGenericBars();
assert.equal(resizeCalls, 1, 'width change rebuilds the chart');
context.resizeGenericBars();
assert.equal(resizeCalls, 1, 'new width is remembered after drawing');
context.window.devicePixelRatio = 2;
context.resizeGenericBars();
assert.equal(resizeCalls, 2, 'pixel-density change redraws at the same CSS width');
assert.equal(resizeCanvas.width, 640);
card.hidden = true;
resizeCanvas.clientWidth = 360;
context.resizeGenericBars();
assert.equal(resizeCalls, 2, 'hidden charts do not rebuild result tables');
card.hidden = false;
context.resizeGenericBars();
assert.equal(resizeCalls, 3, 'visible chart catches up after a hidden resize');
resizeCanvas.clientWidth = 0;
context.resizeGenericBars();
assert.equal(resizeCalls, 3, 'zero-width chart is not redrawn');
resizeCanvas.clientWidth = 400;
const resize = windowListeners.get('resize');
resize(); resize(); resize();
assert.equal(frames.size, 1, 'resize burst coalesces to one frame');
const pending = [...frames.values()][0]; frames.clear(); pending();
assert.equal(resizeCalls, 4);
context.document.querySelector = () => null;
context.resizeGenericBars();
assert.equal(resizeCalls, 4, 'pages without a bar chart remain untouched');
console.log(`Passed ${drawingCases} chart geometry/label cases, 8 percentage cases, 4 fraction cases, 2 matching-unit cases and 12 resize checks.`);
