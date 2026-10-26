const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),result={innerHTML:''},flags={};const group=key=>({classList:{toggle:(_,v)=>flags[key+'Hidden']=v},querySelectorAll:()=>[{set disabled(v){flags[key+'Disabled']=v}}]});
const groups={'[data-floor-dimensions]':[group('dimensions')],'[data-floor-total]':[group('area')],'[data-floor-underlay]':[group('underlay')]};
const c=vm.createContext({document:{addEventListener(){},querySelector:s=>s==='#result'?result:null,querySelectorAll:s=>groups[s]||[],getElementById:id=>id==='genericSummary'?{}:values.get(id)||null},window:{addEventListener(){}}});vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const base=()=>({mode:'dimensions',length:20,width:12,extra:0,totalArea:240,waste:10,boxCoverage:24,boxPrice:48,underlay:true,underlayCoverage:100,underlayPrice:35,underlayWaste:0});let count=0;const near=(a,b)=>assert.ok(Math.abs(a-b)<=Math.max(1e-10,Math.abs(b)*1e-12),`${a} != ${b}`);
function run(input){const p=c.flooringAmounts(input);assert.equal(p.valid,true,p.message);assert.ok(Number.isSafeInteger(p.boxes)&&p.boxes>=1);near(p.purchased,p.boxes*input.boxCoverage);near(p.target,p.area+p.allowanceArea);near(p.leftover,p.allowanceArea+p.roundingRemainder);assert.ok(p.purchased>=p.target-Number.EPSILON*Math.max(1,p.target)*8);assert.ok(Object.values(p).filter(x=>typeof x==='number').every(Number.isFinite));count++;return p}
let p=run(base());assert.equal(p.boxes,11);assert.equal(p.boxCost,528);assert.equal(p.underlayRolls,3);assert.equal(p.totalCost,633);
p=run({...base(),mode:'area',totalArea:250,length:NaN,width:NaN,extra:NaN});assert.equal(p.target,275);assert.equal(p.boxes,12);assert.equal(p.purchased,288);assert.equal(p.allowanceArea,25);assert.equal(p.roundingRemainder,13);assert.equal(p.leftover,38);
for(const mode of ['dimensions','area'])for(const waste of [0,10,25,100])for(const boxCoverage of [12,23.5,24,48])for(const underlay of [true,false])run({...base(),mode,waste,boxCoverage,underlay});
p=run({...base(),underlay:false,underlayCoverage:NaN,underlayPrice:NaN,underlayWaste:NaN});assert.equal(p.underlayRolls,0);assert.equal(p.underlayCost,0);assert.equal(p.totalCost,528);
p=run({...base(),underlayWaste:30});assert.equal(p.underlayTarget,312);assert.equal(p.underlayRolls,4);assert.equal(p.totalCost,668);
for(const boxPrice of [null,0,48])for(const underlayPrice of [null,0,35]){p=run({...base(),boxPrice,underlayPrice});assert.equal(p.totalCost===null,boxPrice===null||underlayPrice===null);if(boxPrice===0)assert.equal(p.boxCost,0)}
p=run({...base(),mode:'area',totalArea:.1,waste:0,boxCoverage:.01,underlay:false});assert.equal(p.boxes,10);
p=run({...base(),mode:'area',totalArea:.1000000001,waste:0,boxCoverage:.01,underlay:false});assert.equal(p.boxes,11);
p=run({...base(),mode:'area',totalArea:1e-100,waste:0,underlay:false});assert.equal(p.boxes,1);
p=run({...base(),mode:'area',totalArea:1e100,boxCoverage:1e99,underlay:false});assert.equal(p.boxes,11);
function invalid(input){assert.equal(c.flooringAmounts(input).valid,false);count++}
for(const key of ['length','width','boxCoverage'])for(const value of [0,-1,NaN,Infinity,'24',null,undefined])invalid({...base(),[key]:value});
for(const value of [0,-1,NaN,Infinity,'24',null])invalid({...base(),mode:'area',totalArea:value});
for(const key of ['extra','boxPrice'])for(const value of [-1,NaN,Infinity,'10',undefined])invalid({...base(),[key]:value});
for(const key of ['waste','underlayWaste'])for(const value of [-1,100.1,NaN,Infinity,'10',null])invalid({...base(),[key]:value});
for(const value of [0,-1,NaN,Infinity,'100',null])invalid({...base(),underlayCoverage:value});
for(const value of [-1,NaN,Infinity,'35',undefined])invalid({...base(),underlayPrice:value});
invalid({...base(),mode:'bad'});invalid({...base(),underlay:'true'});invalid({...base(),length:1e308,width:1e308});invalid({...base(),length:1e-300,width:1e-300});invalid({...base(),boxCoverage:1e-100});invalid({...base(),boxPrice:1e308});invalid({...base(),underlayPrice:1e308});invalid({...base(),mode:'area',totalArea:Number.MIN_VALUE});
assert.match(c.flooringNumber(1e-100),/e-100/);assert.match(c.flooringMoney(1e100),/e\+100/);assert.equal(c.flooringMoney(null),'Not entered');assert.equal(c.flooringMoney(0),'$0.00');count++;
const dom={floor_mode:'dimensions',floor_length:20,floor_width:12,floor_extra:0,floor_area:250,floor_waste:10,floor_box_coverage:24,floor_box_price:48,underlay_coverage:100,underlay_price:35,underlay_waste:0};for(const [key,value] of Object.entries(dom))values.set(key,{value:String(value)});values.set('floor_underlay',{checked:true});let captured;c.renderGeneric=(cards,bars,rows)=>captured={cards,bars,rows};
c.calc('flooring_advanced');assert.match(result.innerHTML,/633/);assert.equal(captured.bars.length,3);assert.ok(captured.bars.every(b=>b.display.endsWith(' ft²')));assert.equal(flags.areaDisabled,true);count++;
values.get('floor_mode').value='area';values.get('floor_length').value='bad';c.calc('flooring_advanced');assert.match(result.innerHTML,/12 boxes/);assert.equal(flags.dimensionsDisabled,true);assert.equal(flags.areaDisabled,false);count++;
values.get('floor_underlay').checked=false;values.get('underlay_coverage').value='0';c.calc('flooring_advanced');assert.match(result.innerHTML,/not included/);assert.equal(flags.underlayDisabled,true);count++;
values.get('floor_box_price').value='';c.calc('flooring_advanced');assert.match(result.innerHTML,/Enter all included/);assert.equal(captured.cards[3][1],'Not entered');count++;
values.get('floor_box_coverage').value='0';c.calc('flooring_advanced');assert.match(result.innerHTML,/Check the flooring inputs/);assert.equal(captured.bars.length,0);count++;
for(const [key,input] of values)if('value' in input&&key!=='floor_mode')input.value='';values.get('floor_mode').value='dimensions';c.calc('flooring_advanced');assert.match(result.innerHTML,/Check the flooring inputs/);assert.equal(captured.rows[0][0],'Validation');count++;
console.log(`${count} flooring coverage, whole-package rounding, optional costs, underlayment and validation scenarios passed.`);
