const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),flags={},result={innerHTML:''};
const group=key=>({classList:{toggle:(_,hidden)=>flags[key+'Hidden']=hidden},querySelectorAll:()=>[{set disabled(v){flags[key+'Disabled']=v}}]});
const groups={'[data-roof-pitch]':[group('pitch')],'[data-roof-rise-run]':[group('riseRun')],'[data-roof-angle]':[group('angle')]};
const c=vm.createContext({document:{addEventListener(){},querySelector:s=>s==='#result'?result:null,querySelectorAll:s=>groups[s]||[],getElementById:id=>id==='genericSummary'?{}:values.has(id)?{value:String(values.get(id))}:null},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const base=()=>({mode:'pitch',pitch:6,rise:6,run:12,angle:26.56505117707799,rafterRun:12,overhangInches:12,planArea:1200});let count=0;
const near=(a,b)=>assert.ok(Math.abs(a-b)<=Math.max(1e-12,Math.abs(b)*1e-12),`${a} != ${b}`);
function valid(input){const p=c.roofPitchAmounts(input);assert.equal(p.valid,true,p.message);assert.ok(Object.values(p).filter(x=>typeof x==='number').every(Number.isFinite));count++;return p}
function invalid(input){assert.equal(c.roofPitchAmounts(input).valid,false);count++}
for(const mode of ['pitch','rise_run','angle']){const p=valid({...base(),mode});near(p.factor,Math.sqrt(1.25));near(p.rafter,Math.hypot(13,6.5));near(p.rise,6);near(p.slopedArea,1341.6407864998738);near(p.squares,13.416407864998739);near(p.angle,26.56505117707799);}
for(const pitch of [0,.001,3,6,12,48,1e-10]){const p=valid({...base(),pitch});near(p.factor,Math.hypot(1,pitch/12));near(p.slopedArea,1200*Math.hypot(1,pitch/12));}
for(const mode of ['pitch','rise_run','angle']){const p=valid({...base(),mode,pitch:0,rise:0,angle:0,overhangInches:0});assert.equal(p.slope,0);assert.equal(p.factor,1);assert.equal(p.rafter,12);assert.equal(p.slopedArea,1200)}
let p=valid({...base(),planArea:null});assert.equal(p.slopedArea,null);assert.equal(p.squares,null);
const first=valid(base()),tail=valid({...base(),overhangInches:24});assert.equal(first.slopedArea,tail.slopedArea);near(tail.rafter-first.rafter,first.factor);
valid({...base(),mode:'rise_run',pitch:NaN,angle:NaN});valid({...base(),mode:'angle',pitch:NaN,rise:NaN,run:NaN});valid({...base(),rise:NaN,run:NaN,angle:NaN});
valid({...base(),mode:'angle',angle:89.999999});valid({...base(),rafterRun:1e100,planArea:1e100});valid({...base(),rafterRun:1e-100,planArea:1e-100});
invalid({...base(),mode:'unknown'});
for(const bad of [-1,NaN,Infinity,-Infinity,'6',null,undefined]){
 invalid({...base(),pitch:bad});invalid({...base(),mode:'rise_run',rise:bad});invalid({...base(),mode:'angle',angle:bad});invalid({...base(),overhangInches:bad});
}
for(const key of ['rafterRun','planArea'])for(const bad of [0,-1,NaN,Infinity,'12',undefined])invalid({...base(),[key]:bad});
for(const bad of [0,-1,NaN,Infinity,'12',null])invalid({...base(),mode:'rise_run',run:bad});
for(const angle of [90,90.1,180,360])invalid({...base(),mode:'angle',angle});
invalid({...base(),mode:'rise_run',rise:1e308,run:1e-308});invalid({...base(),mode:'rise_run',rise:Number.MIN_VALUE,run:1e308});invalid({...base(),pitch:Number.MIN_VALUE});invalid({...base(),mode:'angle',angle:Number.MIN_VALUE});invalid({...base(),rafterRun:1e308,overhangInches:1e308, pitch:48});invalid({...base(),planArea:1e308,pitch:48});invalid({...base(),planArea:Number.MIN_VALUE});invalid({...base(),pitch:1e-100,rafterRun:1e-300});
assert.match(c.roofNumber(1e-12),/e-12/);assert.match(c.roofNumber(1e100),/e\+100/);assert.equal(c.roofNumber(0),'0');assert.notEqual(c.roofAngleNumber(89.999999999),'90');count++;
const dom={roof_input_mode:'pitch',roof_pitch:6,roof_rise:6,roof_run:12,roof_angle:26.56505117707799,roof_rafter_run:12,roof_overhang:12,roof_plan_area:1200};for(const [key,value] of Object.entries(dom))values.set(key,value);
let captured;c.renderGeneric=(cards,bars,rows)=>captured={cards,bars,rows};
c.calc('roof_pitch_advanced');assert.match(result.innerHTML,/6:12/);assert.equal(captured.bars.length,3);assert.ok(captured.bars.every(x=>x.display.endsWith(' ft')));assert.equal(flags.riseRunDisabled,true);assert.equal(flags.angleDisabled,true);assert.equal(flags.pitchDisabled,false);count++;
values.set('roof_plan_area','');values.set('roof_overhang','');c.calc('roof_pitch_advanced');assert.match(result.innerHTML,/roof pitch/);assert.ok(captured.rows.some(x=>x[0]==='Sloped roof area'&&x[1]==='Not entered'));assert.ok(captured.rows.some(x=>x[0]==='Roofing squares'&&x[1]==='Not calculated'));count++;
values.set('roof_plan_area',0);c.calc('roof_pitch_advanced');assert.match(result.innerHTML,/Check the roof inputs/);assert.equal(captured.bars.length,0);assert.equal(captured.rows[0][0],'Validation');count++;
values.set('roof_plan_area',1200);values.set('roof_input_mode','angle');values.set('roof_angle',90);c.calc('roof_pitch_advanced');assert.match(result.innerHTML,/not including/);assert.equal(captured.bars.length,0);count++;
values.set('roof_angle',26.56505117707799);values.set('roof_pitch',-6);c.calc('roof_pitch_advanced');assert.match(result.innerHTML,/roof pitch/);assert.equal(flags.pitchDisabled,true);assert.equal(flags.angleDisabled,false);count++;
for(const key of ['roof_pitch','roof_rise','roof_run','roof_angle','roof_rafter_run','roof_overhang','roof_plan_area'])values.set(key,'');values.set('roof_input_mode','pitch');c.calc('roof_pitch_advanced');assert.match(result.innerHTML,/Check the roof inputs/);assert.equal(captured.bars.length,0);count++;
console.log(`${count} roof pitch geometry, validation, optional area, active-mode and length-only chart scenarios passed.`);
