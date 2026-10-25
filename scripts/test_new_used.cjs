const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),result={innerHTML:''},context=vm.createContext({document:{addEventListener(){},querySelector(s){return s==='#result'?result:null},querySelectorAll(){return[]},getElementById(id){return id==='genericSummary'?{}:values.has(id)?{value:values.get(id)}:null}},window:{addEventListener(){},devicePixelRatio:1},console});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
const car=(overrides={})=>({price:35000,down:5000,resale:20000,fees:2000,insurance:1500,maintenance:500,mpg:30,rate:0,months:60,...overrides});
const base=()=>({years:5,miles:12000,fuel:3.5,newCar:car(),usedCar:car({price:25000,resale:13000,fees:1500,insurance:1200,maintenance:1000,mpg:25})});
let count=0;
function near(actual,expected){assert.ok(Math.abs(actual-expected)<=Math.max(1e-7,Math.abs(expected)*1e-12),`${actual} != ${expected}`)}
function run(input){const p=context.newUsedAmounts(input);assert.equal(p.valid,true,p.message);for(const x of [p.newCar,p.usedCar]){near(x.cost,x.netCashCost);near(x.price-x.resale+x.interestPaid+x.fees+x.operating,x.cost);near(x.loan-x.balance,x.paid-x.interestPaid);assert.ok(x.balance>=0);assert.ok(x.interestPaid>=0)}count++;return p}
let p=run(base());near(p.newCar.cost,34000);near(p.usedCar.cost,32900);near(p.savings,1100);assert.equal(p.winner,'used');near(p.newCar.annualFuel,1400);near(p.usedCar.annualFuel,1680);
{
const i=base();i.years=1;i.newCar.resale=30000;i.usedCar.resale=23000;p=run(i);near(p.newCar.cost,10400);near(p.usedCar.cost,7380);near(p.newCar.balance,24000);near(p.usedCar.balance,16000);near(p.newCar.cashPaid,16400);near(p.newCar.saleEquity,6000);
i.newCar.resale=10000;p=run(i);near(p.newCar.saleEquity,-14000);near(p.newCar.cost,30400);
}
{
const i=base();for(const x of [i.newCar,i.usedCar]){x.down=x.price;x.rate=NaN;x.months=NaN}p=run(i);near(p.newCar.cost,34000);near(p.usedCar.cost,32900);near(p.newCar.payment,0);near(p.newCar.balance,0);
}
{
const i=base();i.newCar.rate=6;i.usedCar.rate=8;p=run(i);
// Independent Decimal reference values, not snapshots of this JavaScript implementation.
near(p.newCar.payment,579.9840458828376);near(p.usedCar.payment,405.52788576827365);
near(p.newCar.cost,38799.04275297025);near(p.usedCar.cost,37231.67314609642);
}
for(const years of [1,2,5,10])for(const months of [1,12,60,120])for(const rate of [0,1e-10,6,100]){const i=base();i.years=years;i.newCar.months=months;i.newCar.rate=rate;p=run(i);if(months<=years*12)near(p.newCar.balance,0)}
{
const i=base();i.usedCar={...i.newCar};p=run(i);assert.equal(p.winner,'tie');near(p.savings,0);
i.usedCar.maintenance=5000;p=run(i);assert.equal(p.winner,'new');
i.miles=0;i.newCar.mpg=NaN;i.usedCar.mpg=NaN;p=run(i);near(p.newCar.annualFuel,0);assert.equal(p.newCar.costPerMile,null);
i.newCar=car({resale:50000,fees:0,insurance:0,maintenance:0,down:35000});i.usedCar=car({down:35000,resale:35000,fees:0,insurance:0,maintenance:0});p=run(i);near(p.newCar.cost,-15000);assert.equal(p.winner,'new');
}
function invalid(i){assert.equal(context.newUsedAmounts(i).valid,false);count++}
for(const [key,bad] of [['years',0],['years',1.5],['years',11],['years',NaN],['miles',-1],['miles',1e6+1],['miles',Infinity],['fuel',-1],['fuel',1001],['fuel',NaN]])invalid({...base(),[key]:bad});
for(const side of ['newCar','usedCar']){
 for(const key of ['price','down','resale','fees','insurance','maintenance'])for(const bad of [-1,NaN,Infinity,1e9+1,'200']){const i=base();i[side][key]=bad;invalid(i)}
 for(const [key,bad] of [['price',0],['down',35001],['rate',-1],['rate',100.1],['rate',NaN],['months',0],['months',1.5],['months',121],['mpg',0],['mpg',-1],['mpg',Infinity],['mpg',1001],['mpg',1e-320]]){const i=base();i[side][key]=bad;invalid(i)}
}
// DOM projection uses complete Number parsing and does not silently replace blank inputs with zero.
const input=base();for(const [key,v] of Object.entries({years:5,miles:12000,fuel:3.5}))values.set('nu_'+key,String(v));
for(const [side,x] of [['new',input.newCar],['used',input.usedCar]])for(const [key,v] of Object.entries(x))values.set(`nu_${side}_${key}`,String(v));
let captured;context.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};
context.calc('new_used_cost');assert.match(result.innerHTML,/Used car is \$1,100.00 lower/);assert.equal(captured.bars.length,2);assert.equal(captured.bars[0].value,34000);assert.ok(captured.rows.some(r=>r[0]==='Reconciled net cash cost'&&r[1]==='$34,000.00'));count++;
for(const raw of ['', '6garbage']){values.set('nu_new_rate',raw);context.calc('new_used_cost');assert.match(result.innerHTML,/Check the comparison inputs/);assert.equal(captured.bars.length,0);assert.equal(captured.rows[0][0],'Validation');count++}
console.log(`${count} new-versus-used cost, cash-flow, financing and validation scenarios passed.`);
