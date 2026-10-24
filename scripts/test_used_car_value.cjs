const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8');
const values={};const context={document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return[]},getElementById(id){return id in values?{value:values[id]}:null}},window:{addEventListener(){}},console};
vm.createContext(context);vm.runInContext(source,context);
const base={benchmark:22000,condition:-5,mileage:-500,options:0,regional:0,spread:12};
let checks=0;
function verify(input,expected){const p=context.usedCarAmounts({...base,...input});assert.equal(p.valid,true);for(const [key,value]of Object.entries(expected))assert.ok(Math.abs(p[key]-value)<1e-8,`${key}: ${p[key]} vs ${value}`);checks++;}
verify({},{retail:20400,privateValue:19176,trade:17952});
verify({benchmark:6000,condition:0,mileage:0,options:-800},{retail:5200,privateValue:4888,trade:4576});
verify({condition:0,mileage:0},{retail:22000,privateValue:20680,trade:19360});
verify({condition:-100,mileage:0},{retail:0,privateValue:0,trade:0});
verify({regional:-100,mileage:0},{retail:0});
verify({benchmark:10000,condition:5,regional:10,mileage:100,options:-650},{retail:11000});
verify({spread:0},{privateValue:20400,trade:20400});
verify({spread:100},{privateValue:10200,trade:0});
verify({spread:75},{privateValue:12750,trade:5100});
for(const key of Object.keys(base))for(const value of [NaN,Infinity,-Infinity,'',null,'5']){assert.equal(context.usedCarAmounts({...base,[key]:value}).valid,false,`${key}=${value}`);checks++;}
for(const input of [{benchmark:0},{benchmark:-1},{condition:-101},{regional:-101},{spread:-1},{spread:101},{options:-30000},{mileage:-30000},{benchmark:1e308,condition:100},{benchmark:1.75e308,condition:0,mileage:0,regional:0}]){assert.equal(context.usedCarAmounts({...base,...input}).valid,false);checks++;}
Object.assign(values,{retail_benchmark:'22000',condition_adjustment:'-5',mileage_adjustment:'-500',options_adjustment:'0',regional_adjustment:'0',dealer_spread:'12'});
assert.equal(context.usedCarProjection().retail,20400);checks++;
for(const id of Object.keys(values)){const initial=values[id];for(const invalid of ['', ' ', 'Infinity','not a number']){values[id]=invalid;assert.equal(context.usedCarProjection().valid,false,id);checks++;}values[id]=initial;}
console.log(`${checks} used-car valuation cases passed`);
