const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),c=vm.createContext({document:{addEventListener(){},querySelectorAll:()=>[],getElementById:id=>values.has(id)?{value:String(values.get(id))}:null},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const defaults={roof_input_mode:'pitch',roof_pitch:6,roof_rise:6,roof_run:12,roof_angle:26.56505117707799,roof_rafter_run:12,roof_overhang:12,roof_plan_area:1200};
const near=(a,b)=>assert.ok(Math.abs(a-b)<=Math.max(1e-9,Math.abs(b)*1e-12),`${a} != ${b}`);let count=0;
function project(overrides={}){values.clear();for(const [key,value] of Object.entries({...defaults,...overrides}))values.set(key,value);const p=c.roofPitchProjection();assert.ok([p.factor,p.slopedArea,p.squares,p.rafter].every(Number.isFinite));count++;return p}
for(const mode of ['pitch','rise_run','angle']){const p=project({roof_input_mode:mode});near(p.factor,Math.sqrt(1.25));near(p.slopedArea,1341.6407864998738);near(p.squares,13.416407864998739);near(p.slopedArea,p.planArea*p.factor);}
for(const pitch of [0,3,6,12]){const p=project({roof_pitch:pitch});near(p.slopedArea,1200*Math.sqrt(1+(pitch/12)**2));near(p.squares,p.slopedArea/100);}
const before=project(),after=project({roof_overhang:24});near(before.slopedArea,after.slopedArea);assert.ok(after.rafter>before.rafter);
const enlarged=project({roof_plan_area:1344});near(enlarged.slopedArea,1344*Math.sqrt(1.25));
console.log(`${count} positive roof-area routing examples and input-mode equivalence checks passed; not a full roof-input validation audit.`);
