const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values=new Map(),result={innerHTML:''};
const context=vm.createContext({document:{addEventListener(){},querySelector(selector){return selector==='#result'?result:null},querySelectorAll(){return[]},getElementById(id){return id==='result'?result:id==='genericSummary'?{}:values.has(id)?{value:values.get(id)}:null}},window:{addEventListener(){},devicePixelRatio:1},console});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
let checks=0;
const cases=[
  ['2026-01-01','2026-01-02',1,'Thursday','Friday'],
  ['2026-01-02','2026-01-01',-1,'Friday','Thursday'],
  ['2026-01-01','2026-01-10',9,'Thursday','Saturday'],
  ['2026-01-10','2026-01-01',-9,'Saturday','Thursday'],
  ['2026-01-01','2026-01-01',0,'Thursday','Thursday'],
  ['2024-02-28','2024-03-01',2,'Wednesday','Friday'],
  ['2025-02-28','2025-03-01',1,'Friday','Saturday'],
  ['1900-02-28','1900-03-01',1,'Wednesday','Thursday'],
  ['2000-02-28','2000-03-01',2,'Monday','Wednesday'],
  ['2026-03-07','2026-03-09',2,'Saturday','Monday'],
  ['2026-10-31','2026-11-02',2,'Saturday','Monday'],
  ['0001-01-01','0001-01-02',1,'Monday','Tuesday'],
  ['0099-12-31','0100-01-01',1,'Thursday','Friday'],
  ['9999-12-30','9999-12-31',1,'Thursday','Friday'],
  ['0001-01-01','9999-12-31',3652058,'Monday','Friday'],
];
for(const [start,end,days,weekdayStart,weekdayEnd] of cases){
  const p=context.calendarDayDifference(start,end);
  assert.equal(p.valid,true);assert.equal(p.days,days);assert.equal(p.startWeekday,weekdayStart);assert.equal(p.endWeekday,weekdayEnd);
  assert.equal(p.wholeWeeks*7+p.remainingDays,Math.abs(days));assert.ok(p.remainingDays>=0&&p.remainingDays<7);
  assert.equal(p.direction,days<0?'End before start':days>0?'End after start':'Same date');
  const reverse=context.calendarDayDifference(end,start);assert.equal(reverse.days,days===0?0:-days);
  checks++;
}
for(const invalid of ['',null,undefined,0,'0000-01-01','10000-01-01','2026-02-29','1900-02-29','2026-02-30','2026-04-31','2026-13-01','2026-00-01','2026-01-00','2026-1-01','1/1/2026','2026-01-01T00:00:00Z',' 2026-01-01','2026-01-01 ']){
  assert.equal(context.calendarDayDifference(invalid,'2026-01-01').valid,false);
  assert.equal(context.calendarDayDifference('2026-01-01',invalid).valid,false);
  checks++;
}
assert.equal(context.calendarDayValue('1970-01-01'),0);checks++;
// Verify all rendered date labels, no mixed-unit bars and recovery after invalid input.
let captured;context.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};
function run(start,end){values.set('start',start);values.set('end',end);context.calc('cn_date');return captured}
let view=run('2026-01-01','2026-01-02');
assert.match(result.innerHTML,/1 day<\/strong>/);assert.match(result.innerHTML,/Friday, 1\/2\/2026/);
assert.equal(view.rows[0][1],'1/1/2026');assert.equal(view.rows[1][1],'1/2/2026');assert.equal(view.bars.length,0);checks++;
view=run('2026-01-10','2026-01-01');assert.equal(view.cards[1][1],'1w 2d');assert.match(result.innerHTML,/-9 days/);checks++;
view=run('','2026-01-01');assert.match(result.innerHTML,/Check the dates/);assert.equal(view.rows[0][0],'Validation');assert.equal(view.cards.length,1);assert.equal(view.bars.length,0);checks++;
view=run('2026-01-01','2026-01-01');assert.match(result.innerHTML,/0 days/);assert.equal(view.rows[2][2],'Same date');checks++;
console.log(`${checks} calendar date validation, Gregorian boundary and rendering cases passed (TZ=${process.env.TZ||'default'}).`);
