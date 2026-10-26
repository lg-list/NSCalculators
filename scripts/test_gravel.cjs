const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),flags={},result={innerHTML:''};const group=key=>({classList:{toggle:(_,v)=>flags[key+'Hidden']=v},querySelectorAll:()=>[{set disabled(v){flags[key+'Disabled']=v}}]});
const groups={'[data-gravel-dimensions]':[group('dimensions')],'[data-gravel-area]':[group('area')]};const c=vm.createContext({document:{addEventListener(){},querySelector:s=>s==='#result'?result:null,querySelectorAll:s=>groups[s]||[],getElementById:id=>id==='genericSummary'?{}:values.get(id)||null},window:{addEventListener(){}}});vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const base=()=>({mode:'dimensions',units:'us',length:20,width:10,area:200,depth:3,allowance:0,density:null,densityUnit:'lb_ft3',price:null,priceUnit:'yd3'});let count=0;const near=(a,b)=>assert.ok(Math.abs(a-b)<=Math.max(1e-10,Math.abs(b)*1e-12),`${a} != ${b}`);
function run(input){const p=c.gravelAmounts(input);assert.equal(p.valid,true,p.message);assert.ok(Object.values(p).filter(x=>typeof x==='number').every(Number.isFinite));near(p.baseFt3+p.allowanceFt3,p.adjustedFt3);near(p.yards*27,p.adjustedFt3);near(p.cubicMeters,p.adjustedFt3*.028316846592);if(p.pounds!==null){near(p.usTons*2000,p.pounds);near(p.kg,p.pounds*.45359237);near(p.tonnes*1000,p.kg)}count++;return p}
let p=run(base());near(p.baseFt3,50);near(p.yards,50/27);assert.equal(p.pounds,null);assert.equal(p.cost,null);
p=run({...base(),allowance:10,density:100,price:40,priceUnit:'us_ton'});near(p.adjustedFt3,55);near(p.pounds,5500);near(p.usTons,2.75);near(p.cost,110);near(p.tonnes,2.494758035);
p=run({...base(),allowance:10,price:50});near(p.cost,2750/27);
for(const mode of ['dimensions','area'])for(const units of ['us','metric'])for(const allowance of [0,10,100])for(const densityUnit of ['lb_ft3','us_ton_yd3','kg_m3'])for(const priceUnit of ['yd3','m3','us_ton','tonne']){
 const input={...base(),mode,units,allowance,densityUnit,priceUnit,density:densityUnit==='lb_ft3'?100:densityUnit==='us_ton_yd3'?1.35:100*.45359237/.028316846592,price:40};if(units==='metric')Object.assign(input,{length:6.096,width:3.048,area:18.580608,depth:7.62});p=run(input);near(p.baseFt3,50);near(p.pounds,50*(1+allowance/100)*100);const quantity=priceUnit==='yd3'?p.yards:priceUnit==='m3'?p.cubicMeters:priceUnit==='us_ton'?p.usTons:p.tonnes;near(p.cost,quantity*40);
}
run({...base(),mode:'area',length:NaN,width:NaN});run({...base(),area:NaN});
for(const priceUnit of ['yd3','m3','us_ton','tonne']){p=run({...base(),priceUnit,price:0});assert.equal(p.cost,priceUnit==='us_ton'||priceUnit==='tonne'?null:0)}
run({...base(),length:1e-30,width:1e-30,depth:1e-30});run({...base(),length:1e30,width:1e30,depth:1e30});
function invalid(input){assert.equal(c.gravelAmounts(input).valid,false);count++}
for(const key of ['length','width','depth'])for(const value of [0,-1,NaN,Infinity,'20',null,undefined])invalid({...base(),[key]:value});
for(const value of [0,-1,NaN,Infinity,'20',null])invalid({...base(),mode:'area',area:value});
for(const value of [-1,100.1,NaN,Infinity,'10',null])invalid({...base(),allowance:value});
for(const value of [0,-1,NaN,Infinity,'100',undefined])invalid({...base(),density:value});
for(const value of [-1,NaN,Infinity,'50',undefined])invalid({...base(),price:value});
for(const [key,value] of [['mode','bad'],['units','bad'],['densityUnit','bad'],['priceUnit','bad'],['length',1e308],['depth',Number.MIN_VALUE]])invalid({...base(),[key]:value});
invalid({...base(),length:1e-300,width:1e-300});invalid({...base(),density:1e308});invalid({...base(),price:1e308});invalid({...base(),density:Number.MIN_VALUE});
for(const kind of ['length','area','depth'])for(const value of [1,3,20,1e-20,1e20]){const metric=c.gravelDimensionConversion(value,kind,'us','metric');near(c.gravelDimensionConversion(metric,kind,'metric','us'),value);count++}
near(c.gravelDimensionConversion(3,'depth','us','metric'),7.62);assert.equal(c.gravelDimensionConversion(1,'bogus','us','metric'),null);assert.equal(c.gravelDimensionConversion(Infinity,'length','us','metric'),null);count++;
const dom={gravel_mode:'dimensions',gravel_units:'us',gravel_length:20,gravel_width:10,gravel_area:200,gravel_depth:3,gravel_allowance:0,gravel_density:'',gravel_density_unit:'lb_ft3',gravel_price:'',gravel_price_unit:'yd3'};for(const [key,value] of Object.entries(dom))values.set(key,{value:String(value)});let captured;c.renderGeneric=(cards,bars,rows)=>captured={cards,bars,rows};
c.calc('gravel_advanced');assert.match(result.innerHTML,/1.852 cubic yards/);assert.match(result.innerHTML,/Enter density/);assert.ok(captured.bars.every(b=>b.display.endsWith(' ft³')));assert.equal(flags.areaDisabled,true);count++;
values.get('gravel_units').value='metric';c.changeGravelUnits();assert.equal(values.get('gravel_length').value,'6.096');assert.equal(values.get('gravel_depth').value,'7.62');c.changeGravelUnits();assert.equal(values.get('gravel_length').value,'6.096');c.calc('gravel_advanced');assert.match(result.innerHTML,/1.852 cubic yards/);count++;
values.get('gravel_length').value='bad';values.get('gravel_mode').value='area';c.calc('gravel_advanced');assert.match(result.innerHTML,/1.852 cubic yards/);assert.equal(flags.dimensionsDisabled,true);count++;
values.get('gravel_density').value='0';c.calc('gravel_advanced');assert.match(result.innerHTML,/Check the gravel inputs/);assert.equal(captured.bars.length,0);count++;
values.get('gravel_density').value='100';values.get('gravel_allowance').value='10';values.get('gravel_price').value='40';values.get('gravel_price_unit').value='us_ton';c.calc('gravel_advanced');assert.match(result.innerHTML,/2.75 US short tons/);assert.match(result.innerHTML,/110.00/);count++;
for(const [key,input] of values)if(!['gravel_mode','gravel_units','gravel_density_unit','gravel_price_unit'].includes(key))input.value='';c.calc('gravel_advanced');assert.match(result.innerHTML,/Check the gravel inputs/);assert.equal(captured.rows[0][0],'Validation');count++;
console.log(`${count} gravel volume, unit conversion, density, price, unknown-state and validation scenarios passed.`);
