const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
let created=0;
const context=vm.createContext({document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return []},getElementById(){return null}},window:{addEventListener(){}},Intl:{NumberFormat:class {constructor(...args){created++;return new Intl.NumberFormat(...args)}}},console});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
const format=vm.runInContext('({F,USD,MONEY})',context);
const values=[0,-0,1,-1,1234.56789,-1234.56789,.005,-.005,1e-12,1e21,Number.MAX_SAFE_INTEGER,Number.MAX_VALUE,NaN,Infinity,-Infinity,null,undefined,'100'];
let checks=0;
for(let digits=0;digits<=12;digits++)for(const value of values){
  assert.equal(format.F(value,digits),Number.isFinite(value)?value.toLocaleString('en-US',{maximumFractionDigits:digits}):'n/a');checks++;
}
const money=(value,currency)=>new Intl.NumberFormat('en-US',{style:'currency',currency,maximumFractionDigits:2}).format(Number.isFinite(value)?value:0);
for(const currency of ['USD','GBP','EUR','CAD','JPY','KWD'])for(const value of values){assert.equal(format.MONEY(value,currency),money(value,currency));checks++;}
for(const value of values){assert.equal(format.USD(value),money(value,'USD'));assert.equal(format.MONEY(value),format.USD(value));checks++;}
const before=created;
for(let i=0;i<1000;i++){format.F(i,2);format.USD(i);format.MONEY(i,'GBP');}
assert.equal(created,before);checks++;
assert.equal(vm.runInContext('NUMBER_FORMATTERS.size',context),13);assert.equal(vm.runInContext('CURRENCY_FORMATTERS.size',context),6);checks++;
for(const digits of [-1,101]){assert.throws(()=>format.F(1,digits));checks++;}
assert.throws(()=>format.MONEY(1,'not a currency'));checks++;
assert.equal(format.F(1234.567), '1,234.57');checks++;
console.log(`${checks} shared number-format output and reuse checks passed`);
