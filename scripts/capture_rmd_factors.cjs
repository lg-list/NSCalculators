// Read public rendered IRS tables; no account changes or submissions.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const browser=await chromium.launch();try{
  const page=await browser.newPage(),source='https://www.irs.gov/publications/p590b';
  assert.equal((await page.goto(source,{waitUntil:'domcontentloaded'})).status(),200);
  const tables=await page.locator('table').evaluateAll(ts=>ts.filter(t=>/Table II\b|Table III\b/.test(t.innerText)).map(t=>({kind:/Table III\b/.test(t.innerText)?'uniform':'joint',rows:[...t.rows].map(r=>[...r.cells].map(c=>c.textContent.trim()))})));
  const uniform={},matrix={};
  const age=text=>/^\d+(?:\+| and over)?$/.test(text)?Number.parseInt(text,10):null;
  for(const table of tables){
    if(table.kind==='uniform'){
      for(const row of table.rows)for(let i=0;i+1<row.length;i+=2){const a=age(row[i]),factor=Number(row[i+1]);if(a!==null&&a>=72&&a<=120&&row[i+1]!==''&&Number.isFinite(factor)&&factor>0)uniform[a]=factor;}
    }else{
      let columns=null;
      for(const row of table.rows){
        if(row[0]==='Ages'){columns=row.slice(1).map(age);continue}
        const a=age(row[0]);if(!columns||a===null)continue;
        row.slice(1).forEach((cell,i)=>{const b=columns[i],factor=Number(cell);if(b!==null&&b!==undefined&&cell!==''&&Number.isFinite(factor)&&factor>0)matrix[a+':'+b]=factor;});
      }
    }
  }
  assert.equal(Object.keys(uniform).length,49);assert.equal(uniform[75],24.6);assert.equal(uniform[120],2);
  const stored=JSON.parse(fs.readFileSync(path.join(__dirname,'../src/data/rmd-joint-life-table.json'),'utf8')),joint={};let checked=0;
  for(const [owner,row] of Object.entries(stored.rows)){
    joint[owner]=row.map((value,i)=>{const spouse=stored.spouse_age_start+i,observed=matrix[owner+':'+spouse]??matrix[spouse+':'+owner];assert.equal(observed,value,`IRS Table II ${owner}/${spouse}`);checked++;return observed});
  }
  assert.equal(joint['75'][64-20],25.3);
  const out={source,publication:await page.locator('h1').first().innerText(),capturedAt:new Date().toISOString(),method:'Playwright public rendered table cells; all 49 Uniform Lifetime ages and every stored Joint Life factor independently compared.',uniformAgeStart:72,uniformAgeCap:120,uniform,jointSpouseAgeStart:20,jointFactorsVerified:checked,joint};
  fs.writeFileSync(path.join(__dirname,'../exports/rmd-irs-factors-2026-10-27.json'),JSON.stringify(out,null,2)+'\n');
  console.log(JSON.stringify({uniformFactors:49,jointFactorsVerified:checked,publication:out.publication,capturedAt:out.capturedAt}));
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
