const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),result={innerHTML:''},table={innerHTML:''},groups=[];
const c=vm.createContext({document:{addEventListener(){},querySelector:s=>s==='#result'?result:s==='#boatSchedule tbody'?table:null,querySelectorAll:s=>s==='[data-bl-cost]'?groups:[],getElementById:id=>id==='genericSummary'?{}:values.get(id)||null},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const base=()=>({price:50000,down:20,downUnit:'percent',rate:7.5,years:10,months:0,startMonth:'2026-10',addCosts:false,fees:3000,feeMethod:'financed',insurance:0,storage:0,operating:0});
const near=(a,b,t=.00001)=>assert.ok(Math.abs(a-b)<=Math.max(t,Math.abs(b)*1e-11),`${a} != ${b}`);let count=0;
function run(input){const p=c.boatLoanAmounts(input);assert.equal(p.valid,true,p.message);near(p.totalCash,p.price+p.purchaseCosts+p.totalInterest+p.periodReserve,.005);near(p.loanPayments,p.principal+p.totalInterest,.005);if(p.principal){assert.equal(p.schedule.length,p.term);near(p.schedule.at(-1).balance,0);near(p.schedule.reduce((s,r)=>s+r.principal,0),p.principal,.005);assert.ok(p.schedule.at(-1).payment<=p.payment*1.000001+.000001);for(const r of p.schedule){assert.ok(r.balance>=0&&r.principal>=0&&r.interest>=0);near(r.payment,r.principal+r.interest)}}else assert.equal(p.schedule.length,0);count++;return p}
let p=run(base());near(p.principal,40000);near(p.payment,474.807076543416908);near(p.totalInterest,16976.849185210029);near(p.cashDue,10000);assert.equal(p.payoff,'Sep 2036');
p=run({...base(),addCosts:true});near(p.principal,43000);near(p.payment,510.417607284173176);near(p.cashDue,10000);
p=run({...base(),addCosts:true,feeMethod:'upfront'});near(p.principal,40000);near(p.payment,474.807076543416908);near(p.cashDue,13000);
p=run({...base(),downUnit:'dollars',down:10000,insurance:1200,storage:2400,operating:600});near(p.monthlyReserve,350);near(p.periodReserve,42000);near(p.monthlyBudget,p.payment+350);
p=run({...base(),down:100,rate:NaN,insurance:1200});assert.equal(p.rate,null);near(p.payment,0);near(p.cashDue,50000);near(p.monthlyBudget,100);near(p.totalCash,62000);
p=run({...base(),down:100,addCosts:true});near(p.principal,3000);assert.ok(p.payment>0);
for(const price of [0.051094890510948905,0.0948905109489051,0.10218978102189781]){p=run({...base(),price,down:100});assert.equal(p.principal,0);assert.equal(p.cashDown,price);}
run({...base(),addCosts:false,fees:NaN,feeMethod:'unknown'});
for(const price of [.01,50000,1e9])for(const rate of [0,1e-10,7.5,100])for(const term of [1,12,120,600])for(const down of [0,20,100]){const input={...base(),price,rate,down,years:Math.floor(term/12),months:term%12};if(price===.01&&down===20){assert.equal(c.boatLoanAmounts(input).valid,false);count++;}else run(input);}
for(const startMonth of ['0001-01','0099-12','9999-12'])run({...base(),years:0,months:1,startMonth});
function invalid(input){assert.equal(c.boatLoanAmounts(input).valid,false);count++;}
for(const [key,bad] of [['price',0],['price',-1],['price',1e9+1],['price',NaN],['price','50000'],['down',-1],['down',101],['down',Infinity],['downUnit','x'],['rate',-1],['rate',100.1],['rate',NaN],['years',-1],['years',1.5],['years',51],['months',12],['months',-.1],['months',NaN],['startMonth','0000-01'],['startMonth','2026-13'],['startMonth','2026-1'],['startMonth',''],['startMonth','2026-10-01'],['addCosts','true'],['insurance',-1],['storage',NaN],['operating',1e7+1]])invalid({...base(),[key]:bad});
invalid({...base(),years:0,months:0});invalid({...base(),startMonth:'9999-12'});invalid({...base(),downUnit:'dollars',down:50001});invalid({...base(),price:.01,down:99});
for(const [key,bad] of [['fees',-1],['fees',1e9+1],['fees',NaN],['feeMethod','x']])invalid({...base(),addCosts:true,[key]:bad});
invalid({...base(),price:1e9,down:0,addCosts:true,fees:1});
for(const [key,value] of Object.entries({price:50000,down:20,down_unit:'percent',rate:7.5,years:10,months:0,start:'2026-10',fees:3000,fee_method:'financed',insurance:1200,storage:2400,operating:0}))values.set('bl_'+key,{value:String(value)});
values.set('bl_add_costs',{checked:true});const flags=[];groups.push({classList:{toggle:(name,value)=>flags.push(value)},querySelectorAll:()=>[{set disabled(value){flags.push(value)}}]});let captured;c.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};
c.calc('boat_loan_advanced');assert.match(result.innerHTML,/\$510.42/);assert.match(result.innerHTML,/\$810.42/);near(captured.bars.reduce((s,b)=>s+b.value,0),c.boatLoanProjection().loanPayments);assert.match(table.innerHTML,/Sep 2036/);count++;
values.get('bl_fees').value='';c.calc('boat_loan_advanced');assert.match(result.innerHTML,/Check the boat inputs/);assert.equal(captured.bars.length,0);assert.equal(table.innerHTML,'');count++;
values.get('bl_add_costs').checked=false;c.calc('boat_loan_advanced');assert.match(result.innerHTML,/\$474.81/);assert.equal(flags.at(-1),true);count++;
values.get('bl_price').value='-50000';c.calc('boat_loan_advanced');assert.match(result.innerHTML,/Check the boat inputs/);assert.equal(table.innerHTML,'');count++;
console.log(`${count} boat purchase, payment, operating-budget, cash reconciliation and validation scenarios passed.`);
