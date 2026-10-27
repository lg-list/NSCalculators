const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const c=vm.createContext({document:{addEventListener(){},querySelector(){return null}},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const base={mode:'lump',age:65,lump:800000,monthly:5000,rate:5,cola:3.5,life:77,spouse:62,spouseLife:82,single:5000,joint:3000,survivor:100,earlyAge:60,lateAge:65,earlyPay:2500,latePay:3800};
let count=0;const near=(a,b)=>assert.ok(Math.abs(a-b)<=Math.max(1e-7,Math.abs(b)*1e-11),`${a} != ${b}`);
// Closed-form annuity-due value, independently derived geometric series.
function pv(payment,years,rate,cola){const q=(1+cola/100)/(1+rate/100);return payment*(q===1?years:(1-q**years)/(1-q))}
function run(x){const p=c.pensionAmounts(x);assert.equal(p.valid,true,p.message);assert.equal(p.schedule.length,p.stop-p.start+(x.mode==='survivor'?1:0));assert.ok(p.schedule.every(s=>[s.pv1,s.pv2,s.pay1,s.pay2].every(Number.isFinite)));count++;return p}
let p=run(base);assert.equal(p.crossover,81);
p=run({...base,mode:'later'});assert.equal(p.crossover,87);
assert.equal(Math.round(p.schedule.find(s=>s.age===86).pv1),639608);
assert.equal(Math.round(p.schedule.find(s=>s.age===86).pv2),636503);
p=run({...base,mode:'survivor'});near(p.immediate,657172.6484872102);near(p.accumulated,514708.93115160626);near(p.replacement,428530.4744144155);
assert.equal(Math.round(p.immediate),657173);assert.equal(Math.round(p.accumulated),514709);assert.equal(Math.round(p.replacement),428530);
for(const rate of [-2,0,3.5,5,10])for(const cola of [0,3.5,5])for(const monthly of [1,1000,5000]){
  p=run({...base,rate,cola,monthly});
  for(const row of p.schedule)near(row.pv2,pv(monthly*12,row.age-base.age,rate,cola)/Math.sqrt(1+rate/100));
  const expected=p.schedule.find(s=>s.pv2>=base.lump)?.age??null;assert.equal(p.crossover,expected);
  p=run({...base,mode:'later',rate,cola,earlyPay:monthly});near(p.pv1,pv(monthly*12,60,rate,cola)/Math.sqrt(1+rate/100));near(p.pv2,pv(base.latePay*12,55,rate,cola)/(1+rate/100)**5.5);
}
for(const rate of [0,3.5,5])for(const cola of [0,3.5])for(const survivor of [50,75,100])for(const spouseLife of [65,74,82]){
  p=run({...base,mode:'survivor',rate,cola,survivor,spouseLife});
  near(p.pv1,pv(base.single*12,13,rate,cola));
  const remaining=Math.max(0,spouseLife-base.spouse-12);
  const remainingPV=pv(base.joint*12*(1+cola/100)**13*survivor/100,remaining,rate,cola);
  near(p.replacement,remainingPV);near(p.pv2,pv(base.joint*12,13,rate,cola)+remainingPV/(1+rate/100)**13);
  near(p.immediate,pv(base.joint*12*survivor/100,spouseLife-base.spouse+1,rate,cola));
  near(p.accumulated,24000*(rate===cola?13*(1+rate/100)**12:((1+rate/100)**13-(1+cola/100)**13)/((rate-cola)/100)));
}
p=run({...base,lump:120000,monthly:1000,rate:0,cola:0});assert.equal(p.crossover,75);
p=run({...base,lump:1e12,monthly:1,rate:0,cola:0});assert.equal(p.crossover,null);
p=run({...base,mode:'later',earlyAge:60,lateAge:65,earlyPay:1000,latePay:2000,rate:0,cola:0});assert.equal(p.crossover,70);
p=run({...base,mode:'survivor',life:65,spouse:62,spouseLife:62,rate:0,cola:0});assert.equal(p.replacement,0);assert.equal(p.pv1,60000);assert.equal(p.pv2,36000);
p=run({...base,mode:'survivor',single:1000,joint:3000});assert.ok(p.accumulated<0);
function invalid(x){assert.equal(c.pensionAmounts(x).valid,false);count++}
for(const mode of ['lump','survivor','later'])for(const key of ['rate','cola'])for(const value of [NaN,Infinity,null,'5',undefined])invalid({...base,mode,[key]:value});
for(const age of [-1,65.5,120,NaN])invalid({...base,age});
for(const mode of ['lump','survivor','later'])for(const key of mode==='lump'?['lump','monthly']:mode==='survivor'?['single','joint']:['earlyPay','latePay'])for(const value of [0,-1,NaN,Infinity,'1000',null,1e13])invalid({...base,mode,[key]:value});
for(const patch of [{mode:'bad'},{rate:-100},{rate:101},{cola:-1},{cola:101},{mode:'survivor',life:64},{mode:'survivor',spouseLife:61},{mode:'survivor',spouseLife:120},{mode:'survivor',survivor:60},{mode:'survivor',life:77.5},{mode:'later',lateAge:60},{mode:'later',earlyAge:65.5},{rate:-99},{cola:100}])invalid({...base,...patch});
// Inactive mode inputs must not alter the calculation or block it.
p=run({...base,life:NaN,single:NaN,earlyAge:NaN});assert.equal(p.crossover,81);
p=run({...base,mode:'later',age:NaN,lump:NaN,life:NaN});assert.equal(p.crossover,87);
const fixture=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../exports/pension-reference-benchmarks-2026-10-27.json'),'utf8'));
for(const record of fixture.cases.filter(x=>x.chartPoints.length)){
  p=run({...base,mode:record.inputs.ctype==='1'?'lump':'later'});
  for(const point of record.chartPoints){const row=p.schedule.find(s=>s.age===point.age);assert.equal(Math.round(row[point.series===1?'pv1':'pv2']),point.pvDollars);count++}
}
const drawContext={setTransform(){},clearRect(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},fillText(){}};
for(const width of [250,320,620])for(const dpr of [1,2,3]){const canvas={clientWidth:width,style:{},getContext:()=>drawContext};c.window.devicePixelRatio=dpr;c.drawPensionLine(canvas,p);assert.equal(canvas.width,width*dpr);assert.equal(canvas.height,220*dpr);assert.equal(canvas.style.height,'220px');assert.equal(drawContext.font,'12px system-ui');}
console.log(`${count} pension present-value, crossover, survivor, timing and validation scenarios passed.`);
console.log('9 pension responsive canvas width and pixel-density checks passed.');
