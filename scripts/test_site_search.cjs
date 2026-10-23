const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const bundle=process.argv[2]||'dist/assets/search.js',index=process.argv[3]||'dist/assets/search-index.json';
const context=vm.createContext({window:{},document:{getElementById(){return null}}});
vm.runInContext(fs.readFileSync(bundle,'utf8'),context,{filename:bundle});
const source=JSON.parse(fs.readFileSync(index,'utf8')),find=context.createCalculatorSearch(source);
const cases=[
  ['car price estimate','used-car-value-calculator'],['gas cost calculator','trip-fuel-cost-calculator'],
  ['elapsed time calculator','time-duration-calculator'],['calculator mortgage','mortgage-calculator'],
  ['  MORTGAGE   CALCULATOR ','mortgage-calculator'],['millimeters-to-rods','millimeters-to-rods-calculator'],
  ['scientific calculator','scientific-calculator'],['area calculator','area-calculator'],
  ['ratio calculator','ratio-calculator'],['mortg','mortgage-calculator'],
];
for(const [query,slug]of cases){const result=find(query);assert.equal(result[0]?.slug,slug,query);assert.ok(result.length<=8);assert.equal(new Set(result.map(x=>x.slug)).size,result.length)}
for(const query of ['','   ','!!!','zzzxxyy nonexistent'])assert.equal(find(query).length,0,query);
for(const query of ['currency calculator','tax calculator','fha loan calculator'])assert.equal(find(query).some(x=>['currency-calculator','tax-calculator','fha-loan-calculator'].includes(x.slug)),false);
const synthetic=context.createCalculatorSearch([
  {title:'Mortgage Payment Calculator',slug:'payment',desc:'Mortgage payments'},
  {title:'Mortgage Calculator',slug:'mortgage',desc:'House loan payments'},
  {title:'Example Tool',slug:'example',aliases:'Loan Payment Calculator',desc:'Calculate a loan payment'},
  {title:'Café Area',slug:'cafe',desc:'Square meters'},
]);
assert.equal(synthetic('mortgage calculator')[0].slug,'mortgage');
assert.equal(synthetic('loan payment calculator')[0].slug,'example');
assert.equal(synthetic('cafe area')[0].slug,'cafe');
assert.equal(synthetic('square meters')[0].slug,'cafe');
assert.equal(synthetic('mortgage impossible').length,0);
assert.equal(synthetic('mortgage',1).length,1);
assert.equal(context.createCalculatorSearch([])('mortgage').length,0);
console.log(`Passed ${cases.length} real-query cases, 4 empty/no-result cases, 3 availability cases and 7 normalization/ranking cases.`);
