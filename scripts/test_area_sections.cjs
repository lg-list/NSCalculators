const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const file=process.argv[2]||'dist/assets/calculator.js';
const values=new Map();
const context=vm.createContext({document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return []},getElementById(id){return values.has(id)?{value:String(values.get(id))}:null}},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(file,'utf8'),context,{filename:file});
const total=context.geometryAreaTotal,ft2=.09290304;
function near(actual,expected,label){assert.ok(Math.abs(actual-expected)<=1e-9*Math.max(1,Math.abs(expected)),`${label}: ${actual} != ${expected}`)}
const sections=[{squareMeters:280*ft2,operation:'add'},{squareMeters:48*ft2,operation:'subtract'}];
const units={sqft:232,sqin:33408,sqyd:232/9,sqm:21.55350528,sqmm:21553505.28,sqcm:215535.0528,sqkm:.00002155350528,acre:232/43560,ha:.002155350528};
for(const [unit,expected]of Object.entries(units)){const p=total(sections,unit);assert.equal(p.valid,true);near(p.result,expected,unit)}
const cases=[
  ['addition split', [{squareMeters:168*ft2},{squareMeters:64*ft2}],232],
  ['mixed-unit deduction', [{squareMeters:280*ft2},{squareMeters:4.45934592,operation:'subtract'}],232],
  ['order does not change final total',[sections[1],sections[0]],232],
  ['zero after matching deduction',[sections[0],{...sections[0],operation:'subtract'}],0],
  ['empty list',[],0],
  ['tiny valid area',[{squareMeters:1e-20}],1e-20/ft2],
  ['roundoff only',[{squareMeters:.3},{squareMeters:.1,operation:'subtract'},{squareMeters:.2,operation:'subtract'}],0],
];
for(const [label,input,expected]of cases){const p=total(input);assert.equal(p.valid,true,label);near(p.result,expected,label);if(label==='tiny valid area')assert.ok(p.result>0)}
const invalid=[
  [sections,'bad-unit'],[[sections[1]],'sqft'],[[{squareMeters:1},{squareMeters:2,operation:'subtract'}],'sqm'],
  [[{squareMeters:.3},{squareMeters:.30000000001,operation:'subtract'}],'sqm'],
  [[{squareMeters:1e308},{squareMeters:1e308}],'sqm'],
  [[{squareMeters:1e308}],'sqmm'],[null,'sqft'],[[null],'sqft'],
  [[{squareMeters:1,operation:'multiply'}],'sqft'],
];
for(const value of [0,-1,NaN,Infinity,'100',null])invalid.push([[{squareMeters:value}],'sqft']);
for(const [input,unit]of invalid)assert.equal(total(input,unit).valid,false);
const base=total(sections);near(base.added,280,'gross');near(base.deducted,48,'deducted');
near(base.result,total([{squareMeters:168*ft2},{squareMeters:64*ft2}]).result,'addition equals subtraction method');
const shapeDefaults={geo_input_unit:'ft',geo_output_unit:'sqft',geo_length:20,geo_width:12,geo_side:10,geo_base:12,geo_height:8,geo_a:3,geo_b:4,geo_c:5,geo_radius:6,geo_semi_major:8,geo_semi_minor:5,geo_base_one:10,geo_base_two:16,geo_trap_height:7,geo_angle:90};
function project(overrides){values.clear();for(const [id,value]of Object.entries({...shapeDefaults,geo_shape:'rectangle',...overrides}))values.set(id,value);return context.geometryAreaProjection()}
const shapes={rectangle:240,square:100,triangle:48,sss:6,circle:36*Math.PI,ellipse:40*Math.PI,parallelogram:96,trapezoid:91,sector:9*Math.PI};
for(const [shape,expected]of Object.entries(shapes)){const p=project({geo_shape:shape});assert.equal(p.valid,true,shape);near(p.result,expected,shape)}
const badShapes=[{geo_length:1e308,geo_width:1e308},{geo_length:1e-200,geo_width:1e-200},{geo_shape:'sss',geo_c:9},{geo_input_unit:'bad'},{geo_output_unit:'bad'},{geo_shape:'sector',geo_angle:361}];
for(const value of [0,-1,NaN,Infinity])badShapes.push({geo_length:value});
for(const input of badShapes)assert.equal(project(input).valid,false,JSON.stringify(input));
console.log(`Passed ${Object.keys(units).length} output-unit cases, ${cases.length} section scenarios, ${invalid.length} invalid totals, 3 reconciliation checks, ${Object.keys(shapes).length} shape modes and ${badShapes.length} invalid projections.`);
