const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),context=vm.createContext({document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return[]},getElementById(id){return values.has(id)?{value:String(values.get(id))}:null}},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
let checks=0;
function near(actual,expected){assert.ok(Number.isFinite(actual));assert.ok(Math.abs(actual-expected)<=Math.abs(expected)*1e-12,`${actual} != ${expected}`);checks++;}
function project(input){values.clear();for(const [key,value]of Object.entries({geo_shape:'sector',geo_radius:6,geo_angle:360,geo_input_unit:'ft',geo_output_unit:'sqft',...input}))values.set(key,value);return context.geometryAreaProjection();}
for(const unit of ['ft','in','yd','mm','cm','m','km']){const sector=project({geo_input_unit:unit}),circle=project({geo_shape:'circle',geo_input_unit:unit});assert.equal(sector.valid,true);assert.equal(circle.valid,true);near(sector.area,circle.area);near(sector.result,circle.result);near(sector.perimeter,circle.perimeter);assert.match(sector.shapeLabel,/Full circle/);}
for(const angle of [0.001,45,90,180,270,359.999999]){const p=project({geo_angle:angle});assert.equal(p.valid,true);near(p.area,Math.PI*36*angle/360);near(p.perimeter,Math.PI*12*angle/360+12);}
const sides=[[3,4,5],[3,5,4],[4,3,5],[4,5,3],[5,3,4],[5,4,3]];
for(const input of sides)near(context.stableTriangleArea(...input),6);
for(const length of [1e-100,1,1e100]){const expected=Math.sqrt(3)/4*length*length;near(context.stableTriangleArea(length,length,length),expected);const p=project({geo_shape:'sss',geo_a:length,geo_b:length,geo_c:length});assert.equal(p.valid,true);near(p.area,expected);}
for(const input of [[1e100,1e100,1e80],[1e100,1e80,1e100],[1e80,1e100,1e100]])near(context.stableTriangleArea(...input),5e179);
near(context.stableTriangleArea(1e150,1e150,1e-150),.5);
const almostFlat=1.999999999999;near(context.stableTriangleArea(1,1,almostFlat),almostFlat/4*Math.sqrt((2-almostFlat)*(2+almostFlat)));
for(const input of [[1,1,2],[1,1,3],[0,3,4],[-1,3,4],[Infinity,3,4],[NaN,3,4],['3',4,5]]){assert.ok(Number.isNaN(context.stableTriangleArea(...input)));checks++;}
for(const angle of [0,-1,360.000001,Infinity,NaN]){assert.equal(project({geo_angle:angle}).valid,false);checks++;}
assert.equal(project({geo_shape:'unknown'}).valid,false);checks++;
assert.equal(project({geo_shape:'sss',geo_a:1,geo_b:1,geo_c:2}).valid,false);checks++;
console.log(`${checks} area boundary and numerical stability checks passed`);
