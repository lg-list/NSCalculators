const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const inputs=new Map(),result={innerHTML:''};let captured;
const c=vm.createContext({document:{addEventListener(){},querySelector:s=>s==='#result'?result:null,querySelectorAll:()=>[],getElementById:id=>id==='genericSummary'?{}:inputs.get(id)||null},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const base={rating:10000,hitchRating:10000,gcwr:16000,gvwr:7200,curb:5200,people:400,cargo:200,tonguePercent:12,tongueRating:null};
let count=0;const near=(a,b)=>assert.ok(Math.abs(a-b)<=Math.max(1e-9,Math.abs(b)*1e-12),`${a} != ${b}`);
function run(x){const p=c.towingAmounts(x);assert.equal(p.valid,true,p.message);assert.ok(Number.isInteger(p.planningLimit)&&p.planningLimit>=0);for(const limit of p.limits)assert.ok(p.planningLimit<=limit.value+Math.max(1,limit.value)*Number.EPSILON*16);near(p.loaded,x.curb+x.people+x.cargo);near(p.vehicleAtLimit,p.loaded+p.tongueLoad);near(p.combinationAtLimit,p.loaded+p.planningLimit);near(p.payloadAfterTongue,x.gvwr-p.vehicleAtLimit);if(!p.overGvwr)assert.ok(p.payloadAfterTongue>=-1e-8);if(!p.overGcwr)assert.ok(p.combinationAtLimit<=x.gcwr+1e-8);if(x.tongueRating!==null)assert.ok(p.tongueLoad<=x.tongueRating+1e-8);assert.ok(p.controlling.length>=1);assert.ok(p.limits.every(l=>Number.isFinite(l.value)));count++;return p}
let p=run(base);assert.equal(p.planningLimit,10000);assert.equal(p.loaded,5800);assert.equal(p.tongueLoad,1200);assert.equal(p.payloadAfterTongue,200);assert.equal(p.combinationAtLimit,15800);assert.equal(p.controlling.length,2);
p=run({...base,tongueRating:900});assert.equal(p.planningLimit,7500);assert.equal(p.tongueLoad,900);assert.equal(p.vehicleAtLimit,6700);assert.equal(p.payloadAfterTongue,500);assert.equal(p.combinationAtLimit,13300);assert.equal(p.controlling[0].label,'Hitch tongue-load limit');
for(const [patch,label,ceiling] of [[{rating:4000},'Vehicle tow rating',4000],[{hitchRating:3000},'Hitch trailer rating',3000],[{gcwr:9000},'GCWR headroom',3200],[{gvwr:6400},'Payload for tongue weight',5000]]){p=run({...base,...patch});assert.equal(p.planningLimit,ceiling);assert.equal(p.controlling[0].label,label)}
p=run({...base,gvwr:6450});assert.equal(p.planningLimit,5416);near(p.tongueLoad,649.92);
p=run({...base,tonguePercent:14});assert.equal(p.planningLimit,10000,'machine-roundoff at an exact whole-pound boundary must not remove a pound');
p=run({...base,gvwr:5800+650-.000000001});assert.equal(p.planningLimit,5416);
for(const people of [0,400,800,1600])for(const cargo of [0,200,600])for(const tonguePercent of [1,5,10,12,15,25,100])for(const tongueRating of [null,0,500,900])run({...base,people,cargo,tonguePercent,tongueRating});
for(const key of ['rating','hitchRating']){p=run({...base,[key]:0});assert.equal(p.planningLimit,0)}
p=run({...base,people:3000});assert.equal(p.planningLimit,0);assert.equal(p.overGvwr,true);assert.ok(p.remainingPayload<0);
p=run({...base,gcwr:5000});assert.equal(p.planningLimit,0);assert.equal(p.overGcwr,true);assert.equal(p.gcwrHeadroom,-800);
for(let cargo=0;cargo<=2000;cargo+=50){const a=run({...base,cargo}),b=run({...base,cargo:cargo+50});assert.ok(b.planningLimit<=a.planningLimit,'more cargo cannot increase modeled towing capacity')}
function invalid(x){assert.equal(c.towingAmounts(x).valid,false);count++}
for(const key of ['rating','hitchRating','gcwr','gvwr','curb','people','cargo','tonguePercent'])for(const value of [NaN,Infinity,null,undefined,'100',-1])invalid({...base,[key]:value});
for(const key of ['gcwr','gvwr','curb'])invalid({...base,[key]:0});
for(const key of ['rating','hitchRating','gcwr','gvwr','curb','people','cargo','tongueRating'])invalid({...base,[key]:1e10});
for(const value of [-1,NaN,Infinity,undefined,'900'])invalid({...base,tongueRating:value});
for(const value of [0,101,Number.MIN_VALUE,1e-200])invalid({...base,tonguePercent:value});
const dom={rating:10000,hitch_rating:10000,gcwr:16000,gvwr:7200,curb:5200,people:400,cargo:200,tongue_pct:12,hitch_tongue_rating:''};Object.entries(dom).forEach(([id,value])=>inputs.set(id,{value:String(value)}));c.renderGeneric=(cards,bars,rows)=>captured={cards,bars,rows};
c.calc('towing');assert.match(result.innerHTML,/10,000 lb modeled trailer ceiling/);assert.match(result.innerHTML,/unknown/);assert.equal(captured.bars.length,4);count++;
inputs.get('hitch_tongue_rating').value='900';c.calc('towing');assert.match(result.innerHTML,/7,500 lb/);assert.equal(captured.bars.length,5);assert.ok(captured.bars.every(b=>b.display.endsWith(' lb')));count++;
inputs.get('people').value='-1000';c.calc('towing');assert.match(result.innerHTML,/Check the towing inputs/);assert.equal(captured.bars.length,0);assert.equal(captured.rows[0][0],'Validation');count++;
inputs.get('people').value='';c.calc('towing');assert.match(result.innerHTML,/Check the towing inputs/);count++;
inputs.get('people').value='400';inputs.get('hitch_tongue_rating').value='-1';c.calc('towing');assert.match(result.innerHTML,/Check the towing inputs/);count++;
for(const input of inputs.values())input.value='';c.calc('towing');assert.match(result.innerHTML,/Check the towing inputs/);assert.equal(captured.bars.length,0);count++;
console.log(`${count} towing constraint, whole-pound rounding, load accounting, monotonicity and validation scenarios passed.`);
