const assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');
const values = {bill:'80',tip:'20',people:'2'};
const context = {document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return []},getElementById(id){return id==='genericSummary'?{}:id in values?{value:values[id]}:null}},window:{addEventListener(){}},console};
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[2] || 'dist/assets/calculator.js','utf8'),context);
let checks = 0;
function verify(input, expected){
  const p = context.tipAmounts({bill:'80',rate:'20',people:'2',...input});
  assert.equal(p.valid,true, p.message);
  for(const [key,value] of Object.entries(expected))assert.equal(p[key],value,key);
  assert.equal(BigInt(p.lowerCents)*BigInt(p.lowerCount)+BigInt(p.higherCents)*BigInt(p.higherCount),BigInt(p.totalCents));
  assert.equal(p.lowerCount+p.higherCount,p.people);
  checks++;
}
verify({}, {tip:16,total:96,lowerCents:4800,higherCount:0});
verify({bill:'100',rate:'0',people:'3'}, {total:100,lowerCents:3333,higherCents:3334,higherCount:1,lowerCount:2});
verify({bill:'0.03',rate:'50',people:'2'}, {tip:0.02,total:0.05,lowerCents:2,higherCount:1});
verify({bill:'0.01',rate:'49.9999'}, {tip:0,total:0.01});
verify({bill:'0.01',rate:'50'}, {tip:0.01,total:0.02});
verify({bill:'0',rate:'20',people:'3'}, {tip:0,total:0,lowerCents:0,higherCount:0});
verify({bill:'12.99',rate:'18',people:'1'}, {tip:2.34,total:15.33,lowerCents:1533});
verify({bill:'1.00',rate:'200',people:'7'}, {tip:2,total:3,lowerCents:42,higherCount:6});
verify({bill:' 00080.00 ',rate:'020.0000',people:'02'}, {tip:16,total:96,people:2});
verify({bill:'0.01',rate:'0',people:'9007199254740991'}, {lowerCents:0,higherCents:1,higherCount:1});
verify({bill:'90071992547409.91',rate:'0',people:'3'},{totalCents:9007199254740991,higherCount:1});
assert.equal(context.tipMoney(9007199254740991),'$90,071,992,547,409.91');checks++;
for(let cents=0;cents<1000;cents+=17)for(let people=1;people<20;people+=3){
  const bill=(cents/100).toFixed(2),p=context.tipAmounts({bill,rate:'17.5',people:String(people)});
  assert.equal(p.tip,Math.floor((cents*175+500)/1000)/100);
  verify({bill,rate:'17.5',people:String(people)},{});
}
for(const key of ['bill','rate','people'])for(const value of ['', ' ', '-1','Infinity','NaN','1e3','hello',null,undefined,1]){
  assert.equal(context.tipAmounts({bill:'80',rate:'20',people:'2',[key]:value}).valid,false,`${key}=${value}`);checks++;
}
for(const input of [{bill:'1.001'},{rate:'1.00001'},{people:'0'},{people:'2.5'},{people:'2.0'},{people:'9007199254740992'},{bill:'90071992547409.92'},{rate:'9999999999999999999999999'}]){
  assert.equal(context.tipAmounts({bill:'80',rate:'20',people:'2',...input}).valid,false);checks++;
}
assert.equal(context.tipProjection().total,96);checks++;
let captured;
context.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};
context.renderGenericFromEngine('cn_tip');
assert.equal(captured.bars.length,2);
assert.equal(captured.bars.reduce((sum,x)=>sum+x.value,0),96);checks++;
values.people='2.5';context.renderGenericFromEngine('cn_tip');
assert.equal(captured.bars.length,0);assert.equal(captured.cards[0][1],'Check inputs');checks++;
values.people='';values.bill='';values.tip='';context.renderGenericFromEngine('cn_tip');
assert.equal(captured.bars.length,0);assert.equal(captured.rows[0][1],'Unavailable');checks++;
console.log(`${checks} exact-cent tip and split cases passed`);
