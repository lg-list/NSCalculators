const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const inputs=new Map(),result={innerHTML:''},schedule={innerHTML:''};let captured;
const c=vm.createContext({document:{addEventListener(){},querySelector:s=>s==='#result'?result:s==='#iraSchedule tbody'?schedule:null,querySelectorAll:()=>[],getElementById:id=>id==='genericSummary'?{}:inputs.get(id)||null},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const base={age:30,retire:65,balance:30000,annual:7500,rate:6,currentTax:25,retireTax:15};let count=0,referenceCells=0;
const near=(a,b)=>assert.ok(Math.abs(a-b)<=Math.max(1e-7,Math.abs(b)*2e-12),`${a} != ${b}`);
function fv(p,a,r,n){if(r===0)return p+a*n;const log=Math.log1p(r);return p*Math.exp(n*log)+a*Math.expm1(n*log)/r}
function run(x){const p=c.iraAmounts(x);assert.equal(p.valid,true,p.message);assert.equal(p.schedule.length,x.retire-x.age);near(p.pretax,fv(x.balance,x.annual,x.rate/100,p.years));near(p.pretaxNet,p.pretax*(1-x.retireTax/100));near(p.roth,fv(x.balance*(1-x.currentTax/100),x.annual*(1-x.currentTax/100),x.rate/100,p.years));const netRate=x.rate>=0?x.rate/100*(1-x.currentTax/100):x.rate/100;near(p.taxable,fv(x.balance*(1-x.currentTax/100),p.afterTaxAnnual,netRate,p.years));if(x.currentTax===x.retireTax)near(p.pretaxNet,p.roth);if(x.rate>=0)assert.ok(p.taxable<=p.roth+1e-6);else assert.equal(p.totalAnnualTax,0);for(const [i,row] of p.schedule.entries()){assert.equal(row.age,x.age+i);near(row.pretaxEnd,row.pretaxStart*(1+x.rate/100)+x.annual);near(row.taxableEnd,row.taxableStart*(1+x.rate/100)-row.annualTax+p.afterTaxAnnual);if(i)near(row.taxableStart,p.schedule[i-1].taxableEnd);assert.ok(Object.values(row).every(Number.isFinite))}count++;return p}
let p=run(base);assert.equal(p.years,35);assert.equal(p.schedule[0].pretaxEnd,39300);assert.equal(p.schedule[0].annualTax,337.5);assert.equal(p.schedule[0].taxableEnd,29137.5);
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'../exports/ira-reference-benchmarks-2026-10-27.json'),'utf8'));
for(const [key,value] of Object.entries(fixture.retirement_balances)){assert.equal(Math.round(p[key]),value);referenceCells++}
for(const observed of fixture.annual_rows){const row=p.schedule.find(s=>s.age===observed.age);for(const [key,value] of Object.entries(observed)){assert.equal(Math.round(row[key]),value);referenceCells++}}
for(const rate of [-20,0,1e-9,6,15])for(const currentTax of [0,15,25,50,100])for(const retireTax of [0,15,25,50,100])for(const years of [1,10,35])run({...base,rate,currentTax,retireTax,retire:base.age+years});
p=run({...base,rate:0});assert.equal(p.pretax,292500);assert.equal(p.roth,219375);assert.equal(p.taxable,219375);
p=run({...base,balance:0,annual:0});assert.equal(p.pretaxNet,0);assert.equal(p.roth,0);assert.equal(p.taxable,0);
p=run({...base,annual:0});assert.ok(p.pretax>base.balance);p=run({...base,balance:0});assert.ok(p.pretax>0);
const futureTax=run({...base,retireTax:40});near(futureTax.roth,run(base).roth);assert.ok(futureTax.pretaxNet<run(base).pretaxNet);
const currentTax=run({...base,currentTax:50});near(currentTax.pretaxNet,run(base).pretaxNet);assert.ok(currentTax.roth<run(base).roth);
p=run({...base,rate:-99});assert.ok(p.pretax>0);assert.equal(p.totalAnnualTax,0);
function invalid(x){assert.equal(c.iraAmounts(x).valid,false);count++}
for(const key of Object.keys(base))for(const value of [NaN,Infinity,null,undefined,'30'])invalid({...base,[key]:value});
for(const patch of [{age:-1},{age:30.5},{retire:65.5},{retire:30},{retire:121},{age:120,retire:121},{balance:-1},{annual:-1},{balance:1e13},{annual:1e13},{rate:-100},{rate:101},{currentTax:-1},{currentTax:101},{retireTax:-1},{retireTax:101},{age:0,retire:120,rate:100}])invalid({...base,...patch});
const dom={ira_age:30,ira_retire:65,ira_balance:30000,ira_annual:7500,ira_return:6,ira_current_tax:25,ira_retire_tax:15};Object.entries(dom).forEach(([id,value])=>inputs.set(id,{value:String(value)}));c.renderGeneric=(cards,bars,rows)=>captured={cards,bars,rows};
c.calc('ira_compare');assert.match(result.innerHTML,/906,391.93/);assert.match(result.innerHTML,/qualified withdrawals/);assert.equal(captured.bars.length,3);assert.match(schedule.innerHTML,/799,757.59/);count++;
inputs.get('ira_age').value='30.5';c.calc('ira_compare');assert.match(result.innerHTML,/Check the IRA inputs/);assert.equal(schedule.innerHTML,'');assert.equal(captured.bars.length,0);count++;
inputs.get('ira_age').value='30';inputs.get('ira_retire').value='50';c.calc('ira_compare');assert.match(result.innerHTML,/Early-distribution taxes are excluded/);count++;
inputs.get('ira_return').value='';c.calc('ira_compare');assert.match(result.innerHTML,/Check the IRA inputs/);assert.equal(schedule.innerHTML,'');count++;
for(const input of inputs.values())input.value='';c.calc('ira_compare');assert.match(result.innerHTML,/Check the IRA inputs/);assert.equal(captured.bars.length,0);count++;
console.log(`${count} IRA equal-budget, annual cash-flow, tax-assumption and validation scenarios; ${referenceCells} public reference numeric checkpoints passed.`);
