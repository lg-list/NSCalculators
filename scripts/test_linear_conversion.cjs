const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const context=vm.createContext({document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return []},getElementById(){return null}},window:{addEventListener(){}},console});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
const {linearConversion,conversionNumber}=vm.runInContext('({linearConversion,conversionNumber})',context);
for(const [v,f,expected] of [[1500,.001,1.5],[0,.001,0],[-1500,.001,-1.5],[.000000001,.001,1e-12],[1,86400,86400],[1.5,1000,1500]]){const p=linearConversion(v,f);assert.equal(p.valid,true);assert.ok(Math.abs(p.result-expected)<=Math.max(1e-25,Math.abs(expected)*1e-12));}
for(const [v,f] of [['',.001],[' ',.001],['bad',1],[Infinity,1],[1,0],[1,-1],[1,Infinity],[1e308,1000],[1e-300,1e-100]])assert.equal(linearConversion(v,f).valid,false);
assert.equal(conversionNumber(1e-12),'1e-12');assert.equal(conversionNumber(-1e-12),'-1e-12');assert.equal(conversionNumber(0),'0');assert.equal(conversionNumber(1.5),'1.5');
console.log('Linear conversion: 19 numerical, validation and formatting checks passed');
