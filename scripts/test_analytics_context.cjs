const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2]||'dist/area-calculator/index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(match=>match[1]).find(text=>text.includes('northstarAnalyticsContext'));
assert.ok(script,'Rendered analytics context exists');
let checks=0;
for(const [referrer,expected]of [['https://www.google.com/search?q=synthetic-secret','https://www.google.com/'],['https://nscalculators.com/loan-calculator/?amount=123456#synthetic','https://nscalculators.com/'],['http://example.com/private/path?key=synthetic','http://example.com/'],['',''],['not a url',''],['data:text/plain,synthetic','']]){
  const window={location:{origin:'https://nscalculators.com',pathname:'/area-calculator/',search:'?q=synthetic-secret&email=example%40example.com',hash:'#synthetic'}};
  const dataLayer=[];window.dataLayer=dataLayer;
  const context=vm.createContext({window,dataLayer,document:{referrer},URL,Date});
  vm.runInContext(script,context);
  const calls=Array.from(window.dataLayer,call=>Array.from(call));
  assert.equal(calls.length,3);assert.equal(calls[0][0],'js');assert.equal(calls[1][0],'set');assert.equal(calls[2][0],'config');
  for(const value of [calls[1][1],calls[2][2]]){assert.equal(value.page_location,'https://nscalculators.com/area-calculator/');assert.equal(value.page_referrer,expected);assert.equal(Object.keys(value).length,2);}
  assert.equal(JSON.stringify(calls).includes('synthetic'),false);checks++;
}
console.log(`${checks} analytics URL context scenarios passed`);
