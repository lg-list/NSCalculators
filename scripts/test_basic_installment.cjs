const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const fields=new Map(),result={innerHTML:''},c=vm.createContext({document:{addEventListener(){},querySelector:s=>s==='#result'?result:null,querySelectorAll:()=>[],getElementById:id=>id==='genericSummary'?{}:fields.has(id)?{value:String(fields.get(id))}:null},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const near=(a,b,t=1e-6)=>assert.ok(Math.abs(a-b)<=Math.max(t,Math.abs(b)*1e-11),`${a} != ${b}`);let count=0;
function run(input){const p=c.basicInstallmentAmounts(input);assert.equal(p.valid,true,p.message);assert.ok(p.payment>0&&p.interest>=0);near(p.total,p.amount+p.interest);near(p.payment*p.months,p.total,.005);count++;return p}
let p=run({amount:10000,rate:10,months:60});near(p.payment,212.470447112682744);near(p.interest,2748.226826760964668);
for(const amount of [.01,10000,1e9])for(const rate of [0,1e-15,1e-10,10,100])for(const months of [1,12,60,600])run({amount,rate,months});
p=run({amount:10000,rate:1e-15,months:60});near(p.payment,10000/60);near(p.total,10000);assert.ok(p.payment>166);p=run({amount:10000,rate:0,months:60});near(p.interest,0);
for(const [key,bad] of [['amount',0],['amount',-1],['amount',.001],['amount',1e9+1],['amount',NaN],['amount',Infinity],['amount','10000'],['rate',-1],['rate',100.1],['rate',NaN],['rate',Infinity],['rate','10'],['months',0],['months',-1],['months',1.5],['months',601],['months',NaN],['months','60']]){assert.equal(c.basicInstallmentAmounts({amount:10000,rate:10,months:60,[key]:bad}).valid,false);count++;}
function project(v){fields.clear();for(const [k,x] of Object.entries(v))fields.set(k,x);return c.basicInstallmentProjection()}
const defaults={amount:'10000',apr:'10',years:'5',months_extra:'0'};
for(const [years,extra,months] of [[5,0,60],[5.5,0,66],[.5,2,8],[1/3,0,4],[0,1,1],[49,11,599],[50,0,600]]){p=project({...defaults,years,months_extra:extra});assert.equal(p.valid,true,p.message);assert.equal(p.months,months);count++;}
for(const [key,bad] of [['amount',''],['apr',''],['years',''],['months_extra',''],['years',-1],['years',NaN],['years',50.1],['years',5.51],['months_extra',.5],['months_extra',12],['months_extra',-1],['amount','10000oops']]){assert.equal(project({...defaults,[key]:bad}).valid,false);count++;}
assert.equal(project({...defaults,years:0}).valid,false);count++;
assert.equal(project({amount:10000,apr:10,months:60}).valid,true);assert.equal(project({amount:10000,apr:10,months:60.5}).valid,false);count+=2;
let captured;c.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};
project(defaults);c.calc('loan');assert.match(result.innerHTML,/\$212.47/);assert.equal(captured.bars.length,2);near(captured.bars.reduce((sum,b)=>sum+b.value,0),c.basicInstallmentProjection().total);assert.equal(captured.rows.some(r=>r[0]==='APR'),false);count++;
fields.set('amount','-10000');c.calc('loan');assert.match(result.innerHTML,/Check the loan inputs/);assert.equal(captured.bars.length,0);count++;
fields.set('amount','10000');fields.set('apr','0.000000000000001');c.calc('loan');assert.match(result.innerHTML,/\$166.67/);assert.match(result.innerHTML,/\$10,000.00/);assert.match(captured.rows.find(r=>r[0]==='Annual note rate')[1],/e-15%/);count++;
console.log(`${count} shared fixed-installment payment, term, validation and breakdown scenarios passed.`);
