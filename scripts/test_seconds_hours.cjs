const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values={seconds_hours_direction:'seconds_to_hours',seconds_hours_value:'3600'};
const context={document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return []},getElementById(id){return id==='genericSummary'?{}:id in values?{value:values[id]}:null}},window:{addEventListener(){}},console};
vm.createContext(context);vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
let checks=0;
function verify(raw,direction,expected){const p=context.secondsHoursAmounts({raw,direction});assert.equal(p.valid,true,p.message);for(const [key,value]of Object.entries(expected))assert.equal(p[key],value,key);
const [seconds,fraction='']=p.secondsText.split('.');const rest=BigInt(seconds)*1000000n+BigInt(fraction.padEnd(6,'0'));
assert.equal((BigInt(p.hours)*3600n+BigInt(p.minutes)*60n)*1000000n+rest,p.ticks);
assert.equal((BigInt(p.days)*86400n+BigInt(p.dayHours)*3600n+BigInt(p.minutes)*60n)*1000000n+rest,p.ticks);
checks++;return p;}
for(const [raw,hms]of [['0','0h 0m 0s'],['1','0h 0m 1s'],['59.999999','0h 0m 59.999999s'],['60','0h 1m 0s'],['3599.999999','0h 59m 59.999999s'],['3600','1h 0m 0s'],['3661','1h 1m 1s'],['86400','24h 0m 0s'],['356442','99h 0m 42s'],['.5','0h 0m 0.5s'],['0001.','0h 0m 1s'],['0.000001','0h 0m 0.000001s']])verify(raw,'seconds_to_hours',{hms});
verify('356442','seconds_to_hours',{days:4,dayHours:3,dhms:'4d 3h 0m 42s',totalSecondsText:'356,442'});
verify('9007199254.740991','seconds_to_hours',{ticks:9007199254740991n,totalSecondsText:'9,007,199,254.740991'});
for(const [raw,totalSecondsText,hms]of [['1','3,600','1h 0m 0s'],['1.5','5,400','1h 30m 0s'],['1.30','4,680','1h 18m 0s'],['0.1','360','0h 6m 0s'],['0.000001','0.0036','0h 0m 0.0036s'],['0','0','0h 0m 0s']])verify(raw,'hours_to_seconds',{totalSecondsText,hms});
for(const direction of ['seconds_to_hours','hours_to_seconds'])for(const raw of ['', ' ', '-1','1e3','NaN','Infinity','1,000','1:30:00','0.0000001',null,undefined,1,'9'.repeat(25)]){assert.equal(context.secondsHoursAmounts({raw,direction}).valid,false);checks++;}
for(const [raw,direction]of [['9007199254.740992','seconds_to_hours'],['2502000','hours_to_seconds'],['1','invalid']]){assert.equal(context.secondsHoursAmounts({raw,direction}).valid,false);checks++;}
for(const seconds of [0,1,59,60,61,3599,3600,3601,86399,86400,86401,356442])verify(String(seconds),'seconds_to_hours',{totalSeconds:seconds});
assert.equal(context.secondsHoursProjection().hms,'1h 0m 0s');checks++;
assert.notEqual(context.durationDecimal(context.secondsHoursAmounts({raw:'0.000001',direction:'seconds_to_hours'}).totalHours),'0');checks++;
let captured;context.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};values.seconds_hours_value='356442';context.renderGenericFromEngine('seconds_hours_advanced');assert.ok(captured.cards.some(row=>row.includes('99h 0m 42s')));assert.equal(captured.bars.length,0);checks++;
values.seconds_hours_value='';context.renderGenericFromEngine('seconds_hours_advanced');assert.equal(captured.cards[0][1],'Check inputs');assert.equal(captured.rows[0][1],'Unavailable');checks++;
console.log(`${checks} seconds/hours precision and decomposition checks passed`);
