const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2] || 'dist/assets/calculator.js', 'utf8');
const match = source.match(/function calculateOnEnter\(event\)\{[\s\S]*?\n\}/);
assert.ok(match, 'Keyboard handler exists in the shipped bundle');
const context = {};
vm.runInNewContext(match[0], context);
let checks = 0;
function run(overrides = {}, inputOverrides = {}, buttonOverrides = {}, panel = false) {
  let clicks = 0, prevented = 0;
  const button = {disabled: false, getClientRects: () => [1], click: () => clicks++, ...buttonOverrides};
  const scope = {querySelector: selector => {assert.equal(selector, '.calc-btn[data-engine]'); return button;}};
  const input = {tagName: 'INPUT', type: 'number', getClientRects: () => [1],
    closest: selector => selector === 'form' ? null : selector === '.loan-mode-input' ? (panel ? scope : null) : scope,
    ...inputOverrides};
  const event = {key: 'Enter', target: input, preventDefault: () => prevented++, ...overrides};
  context.calculateOnEnter(event);
  checks++;
  return {clicks, prevented};
}
const ignored = {clicks: 0, prevented: 0}, submitted = {clicks: 1, prevented: 1};
assert.deepEqual(run(), submitted);
assert.deepEqual(run({}, {type: 'text'}), submitted);
assert.deepEqual(run({}, {}, {}, true), submitted);
for (const key of ['defaultPrevented', 'isComposing', 'repeat', 'ctrlKey', 'altKey', 'metaKey', 'shiftKey']) assert.deepEqual(run({[key]: true}), ignored);
assert.deepEqual(run({keyCode: 229}), ignored);
assert.deepEqual(run({key: 'Escape'}), ignored);
for (const tagName of ['SELECT', 'TEXTAREA', 'BUTTON', 'DIV']) assert.deepEqual(run({}, {tagName}), ignored);
for (const type of ['checkbox', 'radio', 'date', 'month', 'time', 'range', 'file', 'hidden', 'search', 'submit']) assert.deepEqual(run({}, {type}), ignored);
assert.deepEqual(run({}, {disabled: true}), ignored);
assert.deepEqual(run({}, {readOnly: true}), ignored);
assert.deepEqual(run({}, {getClientRects: () => []}), ignored);
assert.deepEqual(run({}, {}, {getClientRects: () => []}), ignored);
assert.deepEqual(run({}, {}, {disabled: true}), ignored);
assert.deepEqual(run({}, {closest: () => null}), ignored);
assert.deepEqual(run({}, {closest: () => ({})}), ignored);
assert.deepEqual(run({target: null}), ignored);
assert.ok(source.includes("document.addEventListener('keydown',calculateOnEnter)"));
console.log(`${checks} calculator keyboard cases passed`);
