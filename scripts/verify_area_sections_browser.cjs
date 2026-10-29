const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{createHash}=require('node:crypto'),{chromium}=require('playwright');
(async()=>{const live=process.argv.includes('--live'),root=path.resolve('doc-work/discovery-build'),origin=live?'https://nscalculators.com':'http://ns.local';const hash=createHash('sha256').update(fs.readFileSync(path.join(root,'assets/calculator-area.js'))).digest('hex').slice(0,16);const b=await chromium.launch();try{
  const c=await b.newContext({deviceScaleFactor:2});await c.route('**/*',async r=>{const u=new URL(r.request().url());if(/google-analytics|googletagmanager/.test(u.hostname))return r.abort();if(live)return r.continue();if(u.hostname!=='ns.local')return r.abort();const file=path.join(root,decodeURIComponent(u.pathname),u.pathname.endsWith('/')?'index.html':'');if(!file.startsWith(root+path.sep)||!fs.existsSync(file))return r.fulfill({status:404,body:'Not found'});const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.json':'application/json'};return r.fulfill({body:fs.readFileSync(file),contentType:types[path.extname(file)]||'text/plain'})});
  const p=await c.newPage(),errors=[],checks=[];p.on('pageerror',e=>errors.push(e.message));
  const dimensions=async(l,w)=>{await p.locator('#geo_length').fill(String(l));await p.locator('#geo_width').fill(String(w))};
  for(const width of [1366,390,320]){
    await p.setViewportSize({width,height:844});const res=await p.goto(origin+'/area-calculator/',{waitUntil:'networkidle'});assert.equal(res.status(),200);assert.equal(await p.locator('script[src*="/assets/calculator-area.js"]').getAttribute('src'),`/assets/calculator-area.js?v=${hash}`);
    assert.match(await p.locator('#result').innerText(),/^240/);assert.ok(await p.locator('[data-engine=area_advanced]').evaluate(el=>el.getBoundingClientRect().bottom<=844));if(!live)await p.screenshot({path:`doc-work/area-initial-${width}.png`});
    for(const id of ['geo_add_section','geo_subtract_section'])assert.equal(await p.locator('#'+id).evaluate(el=>el.scrollWidth>el.clientWidth),false);
    await dimensions(20,14);await p.locator('#geo_add_section').click();assert.match(await p.locator('#geo_total_value').innerText(),/^280 /);
    await dimensions(8,6);await p.locator('#geo_subtract_section').click();assert.match(await p.locator('#geo_total_value').innerText(),/^232 .*net room area/);assert.match(await p.locator('#geo_total_list').innerText(),/Subtract Rectangle - 48/);
    await p.locator('#geo_output_unit').selectOption('sqm');assert.match(await p.locator('#geo_total_value').innerText(),/^21\.55350528 /);await p.locator('#geo_output_unit').selectOption('sqft');assert.match(await p.locator('#geo_total_value').innerText(),/^232 /);
    if(!live&&width===320)await p.locator('#geo_total_panel').screenshot({path:'doc-work/area-net-total-320.png'});
    await p.locator('[data-geo-remove="0"]').click();assert.match(await p.locator('#geo_total_value').innerText(),/Deductions exceed added area/);await p.locator('[data-geo-remove="0"]').click();assert.equal(await p.locator('#geo_total_panel').isVisible(),false);
    await dimensions(20,14);await p.locator('#geo_add_section').click();await p.locator('#geo_input_unit').selectOption('m');await dimensions(2.4384,1.8288);await p.locator('#geo_subtract_section').click();assert.match(await p.locator('#geo_total_value').innerText(),/^232 /);
    await p.locator('#geo_clear_sections').click();assert.equal(await p.locator('#geo_total_panel').isVisible(),false);
    await p.locator('#geo_subtract_section').click();assert.match(await p.locator('#geo_total_value').innerText(),/Deductions exceed/);await p.locator('#geo_add_section').click();assert.match(await p.locator('#geo_total_value').innerText(),/^0 .*net room area/);
    await p.locator('[data-clear]').click();assert.equal(await p.locator('#geo_total_panel').isVisible(),false);
    await dimensions(1e308,1e308);assert.match(await p.locator('#result').innerText(),/too large or small/);await p.locator('#geo_add_section').click();assert.match(await p.locator('#result').innerText(),/Section not saved/);assert.equal(await p.locator('#geo_total_panel').isVisible(),false);
    await dimensions(12,14);await p.locator('#geo_add_section').click();await dimensions(8,8);await p.locator('#geo_add_section').click();assert.match(await p.locator('#geo_total_value').innerText(),/^232 /);
    assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    if(!live&&width===320)await p.screenshot({path:'doc-work/area-sections-320.png',fullPage:true});
    checks.push({width,subtraction:232,mixedUnits:232,addition:232,zero:true,invalidTotal:true,overflowRejected:true});
  }
  assert.deepEqual(errors,[]);console.log(JSON.stringify({live,hash,checks,errors}));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exit(1)});
