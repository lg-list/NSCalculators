const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),result={innerHTML:''},table={innerHTML:''},costGroups=[];
const context=vm.createContext({document:{addEventListener(){},querySelector(s){return s==='#result'?result:s==='#personalSchedule tbody'?table:null},querySelectorAll(s){return s==='[data-pl-cost]'?costGroups:[]},getElementById(id){return id==='genericSummary'?{}:values.get(id)||null}},window:{addEventListener(){},devicePixelRatio:1},console});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
const base=()=>({amount:10000,rate:10,years:5,months:0,startMonth:'2026-10',addCosts:false,fee:5,feeUnit:'percent',feeMethod:'deducted',insurance:0});
let cases=0;
const near=(actual,expected,tolerance=1e-7)=>assert.ok(Math.abs(actual-expected)<=Math.max(tolerance,Math.abs(expected)*1e-11),`${actual} != ${expected}`);
// Subtracting billion-dollar cash flows is checked to half a cent; reference outputs below use tighter tolerances.
function run(input){const p=context.personalLoanAmounts(input);assert.equal(p.valid,true,p.message);assert.equal(p.schedule.length,p.term);near(p.schedule.at(-1).balance,0);near(p.totalCash-p.disbursement,p.borrowingCost,.005);near(p.loanPayments,p.amount+p.totalInterest);near(p.schedule.reduce((s,r)=>s+r.principal,0),p.amount);for(const row of p.schedule){assert.ok(row.balance>=0);assert.ok(row.principal>=0);assert.ok(row.interest>=0);near(row.payment,row.principal+row.interest)}cases++;return p}
let p=run(base());near(p.payment,212.4704471126837);near(p.totalInterest,2748.226826761022);assert.equal(p.payoff,'Sep 2031');near(p.costRate,10);near(p.netCash,10000);
for(const method of ['deducted','upfront']){p=run({...base(),addCosts:true,feeMethod:method});near(p.origination,500);near(p.netCash,9500);near(p.borrowingCost,3248.226826761022);near(p.costRate,12.238801890827607);assert.equal(p.upfront,method==='upfront'?500:0);near(p.disbursement,method==='upfront'?10000:9500);}
for(const amount of [.01,10000,1e9])for(const rate of [0,1e-10,10,100])for(const term of [1,12,60,600]){p=run({...base(),amount,rate,years:Math.floor(term/12),months:term%12});assert.ok(p.schedule.at(-1).payment<=p.payment*1.000001+.000001,'no spurious last-payment balloon')}
p=run({...base(),addCosts:true,insurance:10});near(p.totalInsurance,600);near(p.monthlyCash,p.payment+10);near(p.borrowingCost,3848.226826761022);near(p.costRate,14.288214484529073);
// Independently verify the rate by discounting each actual cash flow, not using the solver's annuity shortcut.
for(const i of [{...base(),addCosts:true},{...base(),addCosts:true,feeUnit:'dollars',fee:500,insurance:10},{...base(),amount:.01,rate:100,years:50,addCosts:true,fee:99.99,insurance:1000000}]){p=run(i);assert.ok(p.costRate!==null);const r=p.costRate/1200,pv=p.schedule.reduce((sum,row)=>sum+(row.payment+row.insurance)*Math.exp(-row.month*Math.log1p(r)),0);near(pv,p.netCash,1e-10);}
p=run({...base(),addCosts:false,fee:NaN,feeUnit:'bad',feeMethod:'bad',insurance:NaN});near(p.netCash,10000);near(p.origination,0);
for(const startMonth of ['0001-01','0099-12','9999-12']){p=run({...base(),years:0,months:1,startMonth});assert.equal(p.payoff,context.personalMonthLabel(Number(startMonth.slice(0,4))*12+Number(startMonth.slice(5))-1));}
function invalid(input){assert.equal(context.personalLoanAmounts(input).valid,false);cases++;}
for(const [key,bad] of [['amount',0],['amount',-.01],['amount',NaN],['amount',1e9+1],['rate',-1],['rate',100.1],['rate',Infinity],['years',-1],['years',1.5],['years',NaN],['years',51],['months',-1],['months',12],['months',.5],['startMonth',''],['startMonth','0000-01'],['startMonth','2026-13'],['startMonth','2026-1'],['startMonth','2026-01-01'],['addCosts','true']])invalid({...base(),[key]:bad});
invalid({...base(),years:0,months:0});invalid({...base(),startMonth:'9999-12'});
for(const [key,bad] of [['fee',-1],['fee',NaN],['fee',100],['feeUnit','x'],['feeMethod','x'],['insurance',-1],['insurance',NaN],['insurance',1e6+1]])invalid({...base(),addCosts:true,[key]:bad});
invalid({...base(),addCosts:true,feeUnit:'dollars',fee:10000});
// DOM cost toggle ignores hidden invalid values and disables its controls.
for(const [key,value] of Object.entries({amount:10000,rate:10,years:5,months:0,start:'2026-10',fee:5,fee_unit:'percent',fee_method:'deducted',insurance:10}))values.set('pl_'+key,{value:String(value)});
values.set('pl_add_costs',{checked:true});const flags=[];costGroups.push({classList:{toggle:(name,value)=>flags.push(value)},querySelectorAll:()=>[{set disabled(v){flags.push(v)}}]});
let captured;context.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};
context.calc('personal_loan_advanced');assert.match(result.innerHTML,/\$222.47/);assert.ok(table.innerHTML.includes('Sep 2031'));near(captured.bars.reduce((sum,b)=>sum+b.value,0),context.personalLoanProjection().totalCash);cases++;
values.get('pl_fee').value='';context.calc('personal_loan_advanced');assert.match(result.innerHTML,/Check the loan inputs/);assert.equal(captured.bars.length,0);assert.equal(table.innerHTML,'');cases++;
values.get('pl_add_costs').checked=false;context.calc('personal_loan_advanced');assert.match(result.innerHTML,/\$212.47/);assert.equal(flags.at(-1),true);cases++;
values.get('pl_amount').value='-10000';context.calc('personal_loan_advanced');assert.match(result.innerHTML,/Check the loan inputs/);assert.equal(table.innerHTML,'');cases++;
console.log(`${cases} personal-loan fee, cash-flow, amortization and validation scenarios passed.`);
