const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values={ratio_mode:'simplify',ratio_a:'12',ratio_b:'18',ratio_c:'',ratio_factor:'4',ratio_total:'100',ratio_pa:'2',ratio_pb:'3',ratio_pc:'14',ratio_pd:''};
const defaults={...values};
const context={document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return []},getElementById(id){return id==='genericSummary'?{}:id in values?{value:values[id]}:null}},window:{addEventListener(){}},console};
vm.createContext(context);vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
let checks=0;
for(const [raw,n,d]of [['12',12,1],['1.5',3,2],['.5',1,2],['+1.500000',3,2],['0',0,1],['1/3',1,3],['1.5/2.5',3,5],['9007199254.740991',9007199254740991,1000000],['9007199254740991.000000',9007199254740991,1],['9007199254740991/9007199254740991',1,1]]){
  const p=context.ratioParse(raw);assert.ok(p,raw);assert.equal(p.n,n,raw);assert.equal(p.d,d,raw);checks++;
}
for(const raw of ['', ' ', '-1', '1e-6','0.0000001','1/0','1/2/3','NaN','Infinity','2x','9007199254740992','9'.repeat(65)]){assert.equal(context.ratioParse(raw),null,raw);checks++;}
function project(input){Object.assign(values,defaults,input);return context.ratioProjection();}
let p=project({});assert.equal(context.ratioText(p.terms),'2 : 3');checks++;
p=project({ratio_a:'1/3',ratio_b:'1/2',ratio_c:'1/6'});assert.equal(context.ratioText(p.terms),'2 : 3 : 1');checks++;
p=project({ratio_mode:'scale',ratio_a:'0.000001',ratio_b:'0.000002',ratio_factor:'0.000001'});assert.equal(p.valid,true);assert.equal(context.ratioText(p.scaled),'1e-12 : 2e-12');assert.equal(context.ratioText(p.terms),'1 : 2');checks++;
for(let missing=0;missing<4;missing++){
  const fields={ratio_pa:'2',ratio_pb:'3',ratio_pc:'14',ratio_pd:'21'},ids=Object.keys(fields),expected=[2,3,14,21][missing];fields[ids[missing]]='';p=project({ratio_mode:'proportion',...fields});assert.equal(p.valid,true);assert.equal(p.solved,expected);checks++;
}
p=project({ratio_mode:'proportion',ratio_pa:'1000000',ratio_pb:'0.000001',ratio_pc:'0.000001'});assert.equal(p.valid,true);assert.equal(context.ratioNumber(p.solved),'1e-18');assert.match(p.equation,/1e-18/);checks++;
p=project({ratio_mode:'split',ratio_a:'3',ratio_b:'2',ratio_total:'100'});assert.deepEqual(Array.from(p.shares),[60,40]);assert.equal(p.check,100);checks++;
p=project({ratio_mode:'split',ratio_a:'9',ratio_b:'1',ratio_total:'1e308'});assert.equal(p.valid,true);assert.ok(p.shares.every(Number.isFinite));assert.ok(Math.abs(p.shares[0]/1e308-.9)<1e-15);assert.ok(Math.abs(p.check/1e308-1)<1e-15);checks++;
for(const total of ['', '0','-1','Infinity','1e309','abc','1x','5e-324']){assert.equal(project({ratio_mode:'split',ratio_total:total}).valid,false,total);checks++;}
for(const fields of [{ratio_a:'0'},{ratio_a:''},{ratio_b:'bad'},{ratio_c:'0'},{ratio_mode:'scale',ratio_factor:'0'},{ratio_mode:'scale',ratio_factor:''},{ratio_mode:'proportion',ratio_pc:''},{ratio_mode:'proportion',ratio_pd:'21'}]){assert.equal(project(fields).valid,false);checks++;}
for(const value of [1e-18,1e-12,1e-9,1e-6,.5,2,21]){const text=context.ratioNumber(value);assert.ok(Number(text.replaceAll(',',''))>0);assert.ok(Math.abs(Number(text.replaceAll(',',''))/value-1)<1e-9);checks++;}
let captured;context.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};
project({ratio_mode:'scale',ratio_a:'0.000001',ratio_b:'0.000002',ratio_factor:'0.000001'});context.renderGenericFromEngine('ratio_advanced');assert.equal(captured.cards[0][1],'1e-12 : 2e-12');assert.deepEqual(Array.from(captured.bars,x=>x.display),['1e-12','2e-12']);checks++;
project({ratio_mode:'proportion',ratio_pa:'1000000',ratio_pb:'0.000001',ratio_pc:'0.000001'});context.renderGenericFromEngine('ratio_advanced');assert.equal(captured.cards[0][1],'1e-18');assert.ok(captured.rows.some(row=>row.some(cell=>String(cell).includes('1e-18'))));checks++;
project({ratio_a:''});context.renderGenericFromEngine('ratio_advanced');assert.equal(captured.bars.length,0);assert.equal(captured.cards[0][1],'Check inputs');checks++;
console.log(`${checks} ratio parsing, precision and four-mode checks passed`);
