const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const values=new Map(),result={innerHTML:''},schedule={innerHTML:''};let captured;
const c=vm.createContext({document:{addEventListener(){},querySelector:s=>s==='#result'?result:s==='#rmdSchedule tbody'?schedule:null,querySelectorAll:()=>[],getElementById:id=>id==='genericSummary'?{}:values.get(id)||null},window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),c);
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'../exports/rmd-irs-factors-2026-10-27.json'),'utf8'));
let cases=0,factors=0;const near=(a,b)=>assert.ok(Math.abs(a-b)<=Math.max(1e-9,Math.abs(b)*1e-12),`${a} != ${b}`);
for(const [age,factor] of Object.entries(fixture.uniform)){assert.equal(c.rmdUniformFactor(Number(age)),factor);factors++}
for(const [owner,row] of Object.entries(fixture.joint))row.forEach((factor,i)=>{assert.equal(c.rmdJointFactor(Number(owner),i+20),factor);factors++});
assert.equal(factors,49+fixture.jointFactorsVerified);
const base={birthYear:1951,birthHalf:'unknown',year:2026,balanceInput:300000,spouseSolo:false,spouseBirthYear:NaN,annualReturn:.05,requestedYears:20};
function run(x){const p=c.rmdAmounts(x);assert.equal(p.valid,true,p.message);assert.ok(p.schedule.length>=1&&p.schedule.length<=x.requestedYears);let total=0;for(const row of p.schedule){assert.ok(row.age<=120&&row.year<=2100);near(row.rmd,row.required?row.balance/row.period:0);near(row.growth,row.balance*x.annualReturn);near(row.ending-row.shortfall,row.balance+row.growth-row.rmd);assert.ok([row.balance,row.rmd,row.growth,row.ending,row.shortfall].every(Number.isFinite));total+=row.rmd}near(p.totalRmd,total);cases++;return p}
let p=run(base);near(p.first.rmd,300000/24.6);near(p.first.ending,302804.8780487805);near(p.schedule[1].rmd,12776.577132859935);
// Independent IRS worked example: owner 75, sole-beneficiary spouse 64.
p=run({...base,balanceInput:100000,spouseSolo:true,spouseBirthYear:1962});assert.equal(p.first.period,25.3);near(p.first.rmd,100000/25.3);
for(const birthYear of [1940,1948,1949,1950,1951,1958,1959,1960,1961])for(const year of [2022,2026,2032,2035])for(const annualReturn of [-.1,0,.05])run({...base,birthYear,year,annualReturn});
for(const gap of [9,10,11,15,30]){p=run({...base,spouseSolo:true,spouseBirthYear:1951+gap});assert.equal(p.jointEligible,gap>10);assert.equal(p.first.table,gap>10?'Joint Life Table II':'Uniform Lifetime Table III')}
for(const [birthYear,birthHalf,firstYear,age] of [[1940,'first',2010,70.5],[1940,'second',2011,70.5],[1948,'first',2018,70.5],[1948,'second',2019,70.5],[1949,'first',2019,70.5],[1949,'second',2021,72],[1950,'unknown',2022,72],[1951,'unknown',2024,73],[1958,'unknown',2031,73],[1959,'unknown',2032,73],[1960,'unknown',2035,75]]){p=run({...base,birthYear,birthHalf});assert.equal(p.rule.firstYear,firstYear);assert.equal(p.rule.age,age)}
assert.equal(c.rmdStartRule(1940).yearLabel,'2010 or 2011');assert.equal(c.rmdStartRule(1949).yearLabel,'2019 or 2021');assert.equal(c.rmdStartRule(1949).firstYear,null);
p=run({...base,birthYear:1960,year:2034,requestedYears:2});assert.equal(p.schedule[0].required,false);assert.equal(p.schedule[0].rmd,0);assert.equal(p.schedule[1].required,true);assert.equal(p.schedule[1].period,24.6);
p=run({...base,birthYear:1951,year:2023});assert.equal(p.first.required,false);assert.equal(p.schedule[1].year,2024);assert.equal(p.schedule[1].required,true);
p=run({...base,balanceInput:0});assert.equal(p.totalRmd,0);assert.equal(p.first.ending,0);
p=run({...base,annualReturn:-.99});assert.equal(p.schedule.length,1);near(p.shortfall,300000/24.6-3000);assert.equal(p.first.ending,0);near(p.first.rmd,300000/24.6);
p=run({...base,birthYear:1906,year:2026});assert.equal(p.schedule.length,1);assert.equal(p.first.period,2);
p=run({...base,birthYear:1980,year:2100});assert.equal(p.schedule.length,1);
p=run({...base,birthYear:1981,year:2100});assert.equal(p.schedule.length,1);
for(const annualReturn of [-.5,0,.5])near(run({...base,annualReturn}).first.rmd,300000/24.6);
function invalid(x){assert.equal(c.rmdAmounts(x).valid,false);cases++}
for(const key of ['birthYear','year','balanceInput','annualReturn','requestedYears'])for(const value of [NaN,Infinity,null,undefined,'2026'])invalid({...base,[key]:value});
for(const patch of [{birthYear:1951.9},{year:2021},{year:2026.5},{year:2101},{birthYear:1899},{birthYear:2027},{birthYear:1900},{balanceInput:-1},{balanceInput:1e16},{annualReturn:-1},{annualReturn:1.01},{requestedYears:0},{requestedYears:40.1},{requestedYears:41},{spouseSolo:'no'},{birthYear:1949,birthHalf:'invalid'},{spouseSolo:true,spouseBirthYear:1965.5},{spouseSolo:true,spouseBirthYear:2027},{spouseSolo:true,spouseBirthYear:1899},{spouseSolo:true,spouseBirthYear:2007},{balanceInput:1e15,annualReturn:1}])invalid({...base,...patch});
for(const age of [NaN,71,120.5,121,'75'])assert.equal(c.rmdUniformFactor(age),null);
for(const [owner,spouse] of [[75,65],[75,19],[121,60],[75.1,60],[75,60.1]])assert.equal(c.rmdJointFactor(owner,spouse),null);
const dom={rmd_birth_year:'1951',rmd_birth_half:'unknown',rmd_year:'2026',rmd_balance:'300000',rmd_spouse_solo:'no',rmd_spouse_birth_year:'',rmd_return:'5',rmd_projection_years:'20'};Object.entries(dom).forEach(([id,value])=>values.set(id,{value}));c.renderGeneric=(cards,bars,rows)=>captured={cards,bars,rows};
c.calc('rmd_advanced');assert.match(result.innerHTML,/12,195.12/);assert.match(schedule.innerHTML,/302,804.88/);assert.equal(captured.bars.length,3);cases++;
values.get('rmd_year').value='2021';c.calc('rmd_advanced');assert.match(result.innerHTML,/Unable to calculate/);assert.equal(schedule.innerHTML,'');assert.equal(captured.bars.length,0);cases++;
values.get('rmd_year').value='2026';values.get('rmd_birth_year').value='1951.9';c.calc('rmd_advanced');assert.match(result.innerHTML,/Unable to calculate/);cases++;
values.get('rmd_birth_year').value='1951';values.get('rmd_return').value='-5';c.calc('rmd_advanced');assert.equal(captured.bars[1].value,-15000);cases++;
values.get('rmd_return').value='';c.calc('rmd_advanced');assert.match(result.innerHTML,/Unable to calculate/);assert.equal(captured.bars.length,0);cases++;
values.get('rmd_return').value='0';values.get('rmd_balance').value='0';c.calc('rmd_advanced');assert.match(result.innerHTML,/\$0.00/);assert.doesNotMatch(result.innerHTML,/NaN/);cases++;
values.get('rmd_birth_year').value='1959';c.calc('rmd_advanced');assert.match(result.innerHTML,/proposed clarification/);cases++;
console.log(`${factors} IRS-rendered factors and ${cases} RMD cohort, annual accounting, validation and stale-output scenarios passed.`);
