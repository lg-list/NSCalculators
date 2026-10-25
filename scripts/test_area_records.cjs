const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const inputs=new Map(),nodes=new Map(),context=vm.createContext({document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return[]},getElementById(id){return nodes.get(id)||(inputs.has(id)?{value:String(inputs.get(id))}:null)}},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
const defaults={geo_shape:'rectangle',geo_input_unit:'ft',geo_output_unit:'sqft',geo_length:20,geo_width:14,geo_side:10,geo_base:12,geo_height:8,geo_a:3,geo_b:4,geo_c:5,geo_radius:6,geo_semi_major:8,geo_semi_minor:5,geo_base_one:10,geo_base_two:16,geo_trap_height:7,geo_angle:90};
function project(values={}){inputs.clear();for(const [key,value] of Object.entries({...defaults,...values}))inputs.set(key,value);return context.geometryAreaProjection()}
function section(values={},operation='add'){const s=context.geometryAreaSection(project(values),operation);assert.ok(s);return s}
function parse(report){assert.equal(report.valid,true,report.message);assert.ok(report.csv.startsWith('\ufeff'));assert.ok(report.csv.endsWith('\r\n'));return JSON.parse(execFileSync('python',['-c','import csv,io,json,sys; rows=list(csv.reader(io.StringIO(sys.stdin.read().lstrip(chr(65279))))); print(json.dumps(rows))'],{input:report.csv,encoding:'utf8',env:{...process.env,PYTHONIOENCODING:'utf-8'}}))}
let cases=0;
const outline=section(),cutout=section({geo_length:8,geo_width:6},'subtract'),saved=[outline,cutout];
for(const unit of ['sqft','sqin','sqyd','sqm','sqmm','sqcm','sqkm','acre','ha']){
 const report=context.geometryAreaCsv(saved,unit),rows=parse(report),net=rows.find(r=>r[0]==='Summary'&&r[2]==='Net');
 assert.equal(rows.length,6);assert.ok(rows.every(r=>r.length===10));assert.equal(rows[1][4],'Length: 20 ft; Width: 14 ft');assert.equal(rows[2][2],'Subtract');assert.equal(rows[1][7],report.total.unit[1]);assert.equal(Number(net[6]),Number(report.total.result.toPrecision(15)));assert.ok(Math.abs(Number(net[8])-21.55350528)<1e-12);assert.equal(net[9],'https://nscalculators.com/area-calculator/');cases++;
}
for(const shape of ['rectangle','square','triangle','sss','circle','ellipse','parallelogram','trapezoid','sector']){
 const s=section({geo_shape:shape}),rows=parse(context.geometryAreaCsv([s]));assert.ok(rows[1][4].length);assert.equal(s.measurements.some(m=>['Diagonal','Diameter','Arc length'].includes(m.name)),false);
 if(shape==='sector'){assert.equal(s.measurements.find(m=>m.name==='Central angle').value,90);assert.equal(s.measurements.find(m=>m.name==='Central angle').unit,'deg');assert.ok(rows[1][4].includes('90 deg'));}cases++;
}
{
 const p=project(),s=context.geometryAreaSection(p);p.dimensions[0][1]=999;p.dimensions[0][2]='m';assert.equal(s.measurements[0].value,20);assert.equal(s.measurements[0].unit,'ft');cases++;
 const mixed=[section({geo_shape:'square',geo_side:1,geo_input_unit:'m'}),section({geo_shape:'square',geo_side:1})],rows=parse(context.geometryAreaCsv(mixed,'sqm'));
 assert.equal(rows[1][4],'Side: 1 m');assert.equal(rows[2][4],'Side: 1 ft');assert.equal(Number(rows.at(-1)[6]),1.09290304);cases++;
 const tiny=section({geo_shape:'square',geo_side:1e-12});assert.ok(parse(context.geometryAreaCsv([tiny]))[1][4].includes('1e-12'));cases++;
 const zero=parse(context.geometryAreaCsv([outline,{...outline,operation:'subtract'}]));assert.equal(Number(zero.at(-1)[6]),0);cases++;
}
for(const [sections,unit] of [[[],'sqft'],[[cutout],'sqft'],[saved,'invalid'],[[{squareMeters:1,shape:'Rectangle'}],'sqm'],[[{...outline,measurements:[]}],'sqft'],[[{...outline,measurements:[{name:'Length',value:NaN,unit:'ft'}]}],'sqft'],[[{...outline,formula:null}],'sqft']]){assert.equal(context.geometryAreaCsv(sections,unit).valid,false);cases++}
for(const p of [null,{},project({geo_length:0})]){assert.equal(context.geometryAreaSection(p),null);cases++}assert.equal(context.geometryAreaSection(project(),'multiply'),null);cases++;
{
 const evil={...outline,shape:'=HYPERLINK("https://invalid.example/","x")',formula:'+1',measurements:[{name:'Name, with "quotes"\nand newline',value:20,unit:'ft'}]},rows=parse(context.geometryAreaCsv([evil],'sqft','\t=1+1'));
 assert.equal(rows[1][3],"'"+evil.shape);assert.equal(rows[1][5],"'+1");assert.equal(rows[1][9],"'\t=1+1");assert.ok(rows[1][4].includes('"quotes"\nand newline'));cases++;
}
// Exercise browser download orchestration without writing files or making network requests.
const status={textContent:''};nodes.set('geo_export_status',status);inputs.set('geo_output_unit','sqft');context.testSaved=saved;vm.runInContext('geometryAreaSections.push(...testSaved)',context);
let removed=0,clicked=0,blob,cleanup,revoked;
context.Blob=class{constructor(parts,options){this.parts=parts;this.options=options}};
context.URL={createObjectURL:value=>{blob=value;return'blob:test'},revokeObjectURL:value=>{revoked=value}};
context.setTimeout=handler=>{cleanup=handler};
context.document.body={appendChild(){}};context.document.createElement=()=>({click(){clicked++},remove(){removed++}});
assert.equal(context.downloadGeometryAreaSections(),true);assert.equal(clicked,1);assert.equal(removed,1);assert.match(status.textContent,/prepared/);assert.equal(blob.options.type,'text/csv;charset=utf-8');assert.ok(blob.parts[0].startsWith('\ufeff'));cleanup();assert.equal(revoked,'blob:test');cases++;
context.document.createElement=()=>({click(){throw Error('Download blocked')},remove(){removed++}});
assert.equal(context.downloadGeometryAreaSections(),false);assert.match(status.textContent,/Unable/);cleanup();assert.equal(removed,2);cases++;
vm.runInContext('geometryAreaSections.length=0',context);assert.equal(context.downloadGeometryAreaSections(),false);assert.equal(clicked,1);assert.match(status.textContent,/Add a room section/);cases++;
console.log(`${cases} saved-area snapshot, CSV parsing, validation and local-download scenarios passed.`);
