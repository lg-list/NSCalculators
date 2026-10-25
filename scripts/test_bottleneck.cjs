const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const inputs=new Map(),result={innerHTML:''},title={textContent:''},groupFlags={};
const group=key=>({classList:{toggle:(cls,hidden)=>{groupFlags[key+'Hidden']=hidden}},querySelectorAll:()=>[{set disabled(value){groupFlags[key+'Disabled']=value}}]});
const groups={'[data-bn-measured]':[group('measured')],'[data-bn-planning]':[group('planning')]};
const context=vm.createContext({document:{addEventListener(){},querySelector(s){return s==='#result'?result:null},querySelectorAll(s){return groups[s]||[]},getElementById(id){return id==='genericSummary'?{}:id==='bottleneckChartTitle'?title:inputs.has(id)?{value:String(inputs.get(id))}:null}},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
const base=()=>({mode:'measured',fps:110,target:144,gpuUsage:78,cpuUsage:96,cpuMs:9.1,gpuMs:7,cpuCap:180,gpuCap:120,uncertaintyPercent:10});let cases=0;
function run(input){const p=context.bottleneckAmounts(input);assert.equal(p.valid,true,p.message);assert.ok(Object.values(p).filter(x=>typeof x==='number').every(Number.isFinite));cases++;return p}
let p=run(base());assert.equal(p.verdict,'Likely CPU-bound');assert.ok(Math.abs(p.frameCeiling-1000/9.1)<1e-10);assert.ok(Math.abs(p.targetBudget-1000/144)<1e-10);
for(const [values,verdict] of [[{cpuMs:7,gpuMs:9.1},'Likely GPU-bound'],[{cpuMs:7,gpuMs:7,cpuUsage:50,gpuUsage:50},'Mixed or inconclusive'],[{cpuMs:7,gpuMs:7,cpuUsage:50,gpuUsage:96},'Likely GPU-bound'],[{cpuMs:7,gpuMs:7},'Likely CPU-bound'],[{fps:144},'Target reached'],[{fps:200},'Target reached'],[{fps:136.8},'Near target'],[{fps:136.79},'Likely CPU-bound']]){p=run({...base(),...values});assert.equal(p.verdict,verdict);if(p.targetReached||p.nearTarget)assert.match(p.reason,/does not establish a frame cap/);if(values.fps===200)assert.equal(p.reason.includes('within 5%'),false);}
for(const uncertaintyPercent of [0,10,50]){p=run({...base(),mode:'planning',uncertaintyPercent});assert.equal(p.estimate,120);assert.equal(p.low,120*(1-uncertaintyPercent/100));assert.equal(p.high,120*(1+uncertaintyPercent/100));assert.equal(p.verdict,'Likely GPU-bound');}
for(const [cpuCap,gpuCap,verdict] of [[100,180,'Likely CPU-bound'],[120,120,'Closely balanced'],[108,120,'Closely balanced'],[120,108,'Closely balanced']]){p=run({...base(),mode:'planning',cpuCap,gpuCap});assert.equal(p.verdict,verdict);}
run({...base(),mode:'planning',fps:NaN,cpuUsage:NaN,gpuUsage:NaN,cpuMs:NaN,gpuMs:NaN});run({...base(),cpuCap:NaN,gpuCap:NaN,uncertaintyPercent:NaN});
run({...base(),mode:'planning',cpuCap:1e-300,gpuCap:2e-300});run({...base(),cpuMs:1e308,gpuMs:1.7e308});
function invalid(input){assert.equal(context.bottleneckAmounts(input).valid,false);cases++;}
invalid({...base(),mode:'unknown'});
for(const mode of ['measured','planning'])for(const target of [0,-1,.5,NaN,Infinity,'144',null])invalid({...base(),mode,target});
for(const key of ['fps','cpuMs','gpuMs'])for(const bad of [0,-1,NaN,Infinity,'7'])invalid({...base(),[key]:bad});
for(const key of ['cpuUsage','gpuUsage'])for(const bad of [-1,100.1,NaN,Infinity,'50'])invalid({...base(),[key]:bad});
for(const key of ['cpuCap','gpuCap'])for(const bad of [0,-1,NaN,Infinity,'120'])invalid({...base(),mode:'planning',[key]:bad});
for(const uncertaintyPercent of [-1,50.1,80,NaN,Infinity,'10'])invalid({...base(),mode:'planning',uncertaintyPercent});
invalid({...base(),mode:'planning',cpuCap:1.7e308,gpuCap:1.7e308,uncertaintyPercent:50});invalid({...base(),mode:'planning',cpuCap:Number.MIN_VALUE,gpuCap:Number.MIN_VALUE,uncertaintyPercent:50});invalid({...base(),cpuMs:Number.MIN_VALUE});
assert.match(context.bottleneckNumber(1e-10,2),/e-10/);assert.equal(context.bottleneckNumber(1e20,1),'1.0e+20');assert.equal(context.bottleneckNumber(0,1),'0');cases++;
for(const [key,value] of Object.entries({bn_mode:'measured',bn_fps:200,bn_target:144,bn_gpu_usage:78,bn_cpu_usage:96,bn_cpu_ms:9.1,bn_gpu_ms:7,bn_cpu_cap:180,bn_gpu_cap:120,bn_plan_target:144,bn_uncertainty:10}))inputs.set(key,value);
let captured;context.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};
context.calc('bottleneck_advanced');assert.match(result.innerHTML,/Target reached/);assert.equal(result.innerHTML.includes('within 5%'),false);assert.ok(captured.bars.every(b=>b.display.endsWith('ms')));assert.equal(groupFlags.planningDisabled,true);cases++;
inputs.set('bn_mode','planning');inputs.set('bn_uncertainty',80);context.calc('bottleneck_advanced');assert.match(result.innerHTML,/0% through 50%/);assert.equal(captured.bars.length,0);assert.equal(captured.rows[0][0],'Validation');cases++;
inputs.set('bn_uncertainty',10);inputs.set('bn_fps','bad');context.calc('bottleneck_advanced');assert.match(result.innerHTML,/108-132 FPS/);assert.ok(captured.bars.every(b=>b.display.endsWith('FPS')));assert.equal(groupFlags.measuredDisabled,true);assert.equal(title.textContent,'Benchmark FPS Ceilings');cases++;
inputs.set('bn_gpu_cap','120junk');context.calc('bottleneck_advanced');assert.match(result.innerHTML,/Unable to analyze/);assert.equal(captured.bars.length,0);cases++;
console.log(`${cases} bottleneck evidence, target wording, range and validation scenarios passed.`);
