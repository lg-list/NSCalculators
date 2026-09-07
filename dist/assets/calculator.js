const $=s=>document.querySelector(s), V=id=>parseFloat(document.getElementById(id)?.value||0);
const F=(n,d=2)=>Number.isFinite(n)?n.toLocaleString('en-US',{maximumFractionDigits:d}):'n/a';
const USD=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2}).format(Number.isFinite(n)?n:0);
function show(html){const r=$('#result');if(r)r.innerHTML=html}
function unitValue(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function annualCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function monthlyCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100/12:V(id)/12}
function monthDate(id){const raw=document.getElementById(id)?.value||'';return /^\d{4}-\d{2}$/.test(raw)?new Date(`${raw}-01T00:00:00`):new Date(raw||Date.now())}
function syncMortgageCosts(){const box=document.getElementById('include_costs'),panel=document.getElementById('mortgageCostFields');if(!box||!panel)return true;const on=box.checked;panel.hidden=!on;panel.classList.toggle('is-hidden',!on);panel.style.display=on?'':'none';return on}
function clearCalcForm(){const form=document.querySelector('.calc');if(!form)return;form.querySelectorAll('input').forEach(input=>{if(input.type==='checkbox')input.checked=false;else input.value=''});form.querySelectorAll('select').forEach(select=>{select.selectedIndex=0});form.querySelectorAll('details').forEach(item=>{item.open=false});syncMortgageCosts();show('<strong>$0.00 / month</strong><br>Enter values to calculate a new result.');const engine=currentEngine();if(engine==='cn_mortgage')renderMortgage(0,0,1,0,0,0,0,0,0,0,0,0,0,new Date());if(engine==='loan_page')renderLoanPage()}
function calc(e){
 switch(e){
  case'trade_value':{let price=V('price'),age=V('age'),miles=V('miles'),cond=V('condition');let ageF=Math.pow(.84,age),expected=Math.max(1,age)*12000,mileageF=Math.max(.72,Math.min(1.12,1-(miles-expected)*0.000003));let r=price*ageF*mileageF*cond;show(`<strong>${USD(Math.max(0,r))}</strong><br>Illustrative estimate, not a dealer quote or appraisal.`);break}
  case'f150_bed':{let bed=String(document.getElementById('bed').value);let d={'5.5':['67.1 in','50.6 in','~52.8 cu ft'],'6.5':['78.9 in','50.6 in','~62.3 cu ft'],'8':['97.6 in','50.6 in','~77.4 cu ft']}[bed];show(`<strong>${bed} ft bed</strong><br>Approx. inside length: ${d[0]}; width between wheelhouses: ${d[1]}; cargo volume: ${d[2]}. Verify exact model year/configuration.`);break}
  case'depreciation':{let r=V('price')*Math.pow(1-V('rate')/100,V('years'));show(`<strong>${USD(r)}</strong><br>Estimated future value.`);break}
  case'payload':{let r=V('gvwr')-V('curb')-V('people')-V('cargo');show(`<strong>${F(r,0)} lb</strong><br>Estimated remaining payload.`);break}
  case'trailer_weight':{let r=V('empty')+V('cargo');show(`<strong>${F(r,0)} lb</strong><br>Estimated loaded trailer weight.`);break}
  case'tongue_weight':{let r=V('trailer')*V('percent')/100;show(`<strong>${F(r,0)} lb</strong><br>Estimated tongue weight.`);break}
  case'trailer_payload':{let r=V('gvwr')-V('empty');show(`<strong>${F(r,0)} lb</strong><br>Theoretical payload before other limits.`);break}
  case'tongue_pct':{let r=V('trailer')?V('tongue')/V('trailer')*100:0;show(`<strong>${F(r,2)}%</strong>`);break}
  case'towing':{let r=Math.min(V('rating'),Math.max(0,V('gcwr')-V('vehicle')));show(`<strong>${F(r,0)} lb</strong><br>Lower of tow rating and GCWR headroom; other limits may be lower.`);break}
  case'fuel_cost':{let r=V('distance')/Math.max(.01,V('mpg'))*V('fuelprice');show(`<strong>${USD(r)}</strong><br>Estimated fuel cost.`);break}
  case'mpg':{let r=V('gallons')?V('miles')/V('gallons'):0;show(`<strong>${F(r,2)} MPG</strong>`);break}
  case'tire':{let width=V('width'),aspect=V('aspect'),wheel=V('wheel');let side=width*aspect/100,diam=wheel+2*side/25.4,circ=Math.PI*diam;show(`<strong>${F(diam,2)} in diameter</strong><br>Sidewall: ${F(side,1)} mm; circumference: ${F(circ,2)} in.`);break}
  case'offset':{let r=(V('backspacing')-V('width')/2)*25.4;show(`<strong>${F(r,1)} mm offset</strong><br>Approximation using nominal wheel width.`);break}
  case'backspacing':{let r=V('width')/2+V('offset')/25.4;show(`<strong>${F(r,2)} in backspacing</strong><br>Approximation using nominal wheel width.`);break}
  case'bolt_pattern':{let r=V('adjacent')/Math.sin(Math.PI/V('lugs'));show(`<strong>${F(r,3)} in bolt-circle diameter</strong>`);break}
  case'horsepower':{let r=V('torque')*V('rpm')/5252;show(`<strong>${F(r,1)} hp</strong>`);break}
  case'power_weight':{let a=V('hp')/V('weight'),b=V('weight')/V('hp');show(`<strong>${F(a,4)} hp/lb</strong><br>${F(b,2)} lb per hp.`);break}
  case'car_loan':{let price=V('price'),tax=price*V('tax')/100,fees=V('fees'),include=(document.getElementById('include_fees')?.value||'0')==='1';let base=Math.max(0,price-V('incentives')-V('down')-V('trade')+V('owed')),P=Math.max(0,base+(include?tax+fees:0));let rr=V('apr')/1200,n=Math.max(1,V('months'));let pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n,upfront=V('down')+(include?0:tax+fees);show(`<strong>${USD(pay)} / month</strong><br>Total loan amount: ${USD(P)}; upfront payment: ${USD(upfront)}; sale tax: ${USD(tax)}.`);break}
  case'loan':{let P=V('amount'),rr=V('apr')/1200,n=Math.max(1,(V('years')*12)+(V('months_extra')||V('months')));let pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n,total=pay*n;show(`<strong>${USD(pay)} / month</strong><br>Total paid: ${USD(total)}; total interest: ${USD(total-P)}.`);break}
  case'loan_page':{renderLoanPage();break}
  case'compound':{let P=V('principal'),rr=V('rate')/1200,n=V('years')*12,pmt=V('monthly');let r=P*Math.pow(1+rr,n)+(rr?pmt*(Math.pow(1+rr,n)-1)/rr:pmt*n);show(`<strong>${USD(r)}</strong><br>Estimated future value with monthly contributions.`);break}
  case'discount':{let r=V('price')*(1-V('discount')/100);show(`<strong>${USD(r)}</strong><br>Savings: ${USD(V('price')-r)}.`);break}
  case'salary':{let r=V('salary')*(1+V('increase')/100);show(`<strong>${USD(r)}</strong><br>Annual increase: ${USD(r-V('salary'))}.`);break}
  case'dome':{let radius=V('diameter')/2,area=2*Math.PI*radius*radius,vol=2/3*Math.PI*Math.pow(radius,3);show(`<strong>${F(area,2)} sq ft</strong><br>Approx. curved area; ${F(vol,2)} cu ft volume.`);break}
  case'dome_material':{let radius=V('diameter')/2,area=2*Math.PI*radius*radius*(1+V('waste')/100);show(`<strong>${F(area,2)} sq ft</strong><br>Estimated covering area including waste.`);break}
  case'concrete':{let cf=V('length')*V('width')*(V('depth')/12),cy=cf/27*(1+V('waste')/100);show(`<strong>${F(cy,2)} cu yd</strong><br>${F(cf,2)} cu ft before waste.`);break}
  case'area':{let r=V('length')*V('width');show(`<strong>${F(r,2)} sq ft</strong>`);break}
  case'board_foot':{let r=V('thickness')*V('width')*V('length')/12*V('qty');show(`<strong>${F(r,2)} board ft</strong>`);break}
  case'studs':{let r=Math.ceil(V('wall')*12/V('spacing'))+1;show(`<strong>${F(r,0)} studs</strong><br>Basic count before corners, openings and special framing.`);break}
  case'roof_pitch':{let ratio=V('rise')/V('run'),per=ratio*100,angle=Math.atan(ratio)*180/Math.PI,pitch=ratio*12;show(`<strong>${F(pitch,2)}:12 pitch</strong><br>${F(per,1)}% slope; ${F(angle,1)} degree angle.`);break}
  case'rafter':{let r=Math.sqrt(V('run')**2+V('rise')**2)+V('overhang');show(`<strong>${F(r,2)} ft</strong><br>Approximate sloped length including entered overhang.`);break}
  case'flooring':{let r=V('length')*V('width')*(1+V('waste')/100);show(`<strong>${F(r,2)} sq ft</strong><br>Estimated order quantity.`);break}
  case'tile':{let tileArea=V('tilew')*V('tileh')/144,r=V('area')*(1+V('waste')/100)/tileArea;show(`<strong>${Math.ceil(r).toLocaleString()} tiles</strong><br>Area per tile: ${F(tileArea,3)} sq ft.`);break}
  case'tile_layout':{let count=Math.floor((V('row')+V('joint'))/(V('tile')+V('joint')));show(`<strong>${count} full tiles per row</strong><br>Approximate full-tile count before cuts.`);break}
  case'deck':{let total=V('deckwidth')*12,step=V('boardwidth')+V('gap'),r=Math.ceil(total/step);show(`<strong>${r} boards</strong><br>Approximate count across deck width.`);break}
  case'voltage_drop':{let drop=2*V('length')*V('amps')*V('resistance')/1000,per=drop/V('voltage')*100;show(`<strong>${F(drop,2)} V drop</strong><br>${F(per,2)}% of system voltage.`);break}
  case'wire_size':{let a=V('amps'),table=[[14,15],[12,20],[10,30],[8,40],[6,55],[4,70],[3,85],[2,95],[1,110],[0,125]],hit=table.find(x=>x[1]>=a)||table[table.length-1];show(`<strong>${hit[0]===0?'1/0':hit[0]} AWG reference</strong><br>Simplified planning table only; actual code-compliant sizing can differ.`);break}
  case'breaker':{let need=V('amps')*1.25,standard=[15,20,25,30,35,40,45,50,60,70,80,90,100,110,125,150,175,200],size=standard.find(x=>x>=need)||Math.ceil(need/25)*25;show(`<strong>${size} A reference breaker</strong><br>125% planning current: ${F(need,2)} A. Verify code, conductor and equipment requirements.`);break}
  case'amps_watts':{let r=V('amps')*V('volts');show(`<strong>${F(r,2)} W</strong>`);break}
  case'watts_amps':{let r=V('volts')?V('watts')/V('volts'):0;show(`<strong>${F(r,2)} A</strong>`);break}
  case'linear_convert':{let r=V('value')*V('factor'),target=document.getElementById('target')?.value||'target units';show(`<strong>${F(r,8)} ${target}</strong><br>Converted with the factor shown in the formula.`);break}
  case'cn_mortgage':{let price=V('price'),down=unitValue('down',price),P=Math.max(0,price-down),rr=V('apr')/1200,n=Math.max(1,V('years')*12);let pi=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n;let include=syncMortgageCosts(),tax=include?annualCost('tax',price)/12:0,ins=include?monthlyCost('insurance',price):0,pmi=include?monthlyCost('pmi',P):0,hoa=include?monthlyCost('hoa',price):0,other=include?monthlyCost('other',price):0,inc=include?V('increase'):0,extraM=V('extra_monthly'),extraY=V('extra_yearly'),extraO=V('extra_once'),extra=tax+ins+pmi+hoa+other;let start=monthDate('start');show(`<strong>${USD(pi)} / month</strong><br>Total monthly payment with selected taxes and costs: ${USD(pi+extra+extraM)}.`);renderMortgage(P,rr,n,pi,tax,ins,pmi,hoa,other,inc,extraM,extraY,extraO,start);break}
  case'cn_simple_interest':{let P=V('principal'),i=P*V('rate')/100*V('years');show(`<strong>${USD(P+i)}</strong><br>Simple interest: ${USD(i)}.`);break}
  case'cn_retirement':{let P=V('principal'),rr=V('rate')/1200,n=V('years')*12,pmt=V('monthly');let fv=P*Math.pow(1+rr,n)+(rr?pmt*(Math.pow(1+rr,n)-1)/rr:pmt*n);show(`<strong>${USD(fv)}</strong><br>Total contributions: ${USD(P+pmt*n)}; estimated growth: ${USD(fv-P-pmt*n)}.`);break}
  case'cn_inflation':{let r=V('amount')*Math.pow(1+V('rate')/100,V('years'));show(`<strong>${USD(r)}</strong><br>Inflation-adjusted estimate after ${F(V('years'),1)} years.`);break}
  case'cn_tax_salary':{let taxable=Math.max(0,V('income')-V('deductions')),tax=taxable*V('taxrate')/100,net=V('income')-tax;show(`<strong>${USD(net)} take-home</strong><br>Estimated tax: ${USD(tax)}; monthly take-home: ${USD(net/12)}.`);break}
  case'cn_bmi':{let h=V('feet')*12+V('inches'),bmi=h?703*V('weight')/(h*h):0;let band=bmi<18.5?'underweight':bmi<25?'healthy range':bmi<30?'overweight range':'obesity range';show(`<strong>${F(bmi,1)} BMI</strong><br>This falls in the ${band} by adult BMI screening ranges.`);break}
  case'cn_calorie':{let h=(V('feet')*12+V('inches'))*2.54,kg=V('weight')*0.453592,age=V('age'),sex=document.getElementById('sex')?.value||'male';let bmr=10*kg+6.25*h-5*age+(sex==='male'?5:-161),tdee=bmr*V('activity');show(`<strong>${F(tdee,0)} calories/day</strong><br>BMR: ${F(bmr,0)}. Protein planning range: ${F(kg*1.6,0)}-${F(kg*2.2,0)} g/day.`);break}
  case'cn_body_metric':{let h=V('feet')*12+V('inches'),bmi=h?703*V('weight')/(h*h):0,low=18.5*h*h/703,high=24.9*h*h/703;show(`<strong>${F(bmi,1)} BMI</strong><br>Adult BMI reference weight range at this height: ${F(low,0)}-${F(high,0)} lb.`);break}
  case'cn_due_date':{let d=new Date(document.getElementById('date')?.value||''),days=V('days');if(isNaN(d)){show('Enter a valid date.');break}let out=new Date(d.getTime()+days*86400000);show(`<strong>${out.toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'})}</strong><br>Calculated by adding ${F(days,0)} days to the start date.`);break}
  case'cn_pace':{let sec=V('hours')*3600+V('minutes')*60+V('seconds'),dist=V('distance');let pace=dist?sec/dist:0;show(`<strong>${Math.floor(pace/60)}:${String(Math.round(pace%60)).padStart(2,'0')} per mile</strong><br>Average speed: ${F(dist/(sec/3600),2)} mph.`);break}
  case'cn_percent':{let pct=V('whole')?V('part')/V('whole')*100:0,change=V('old')?(V('new')-V('old'))/V('old')*100:0;show(`<strong>${F(pct,2)}%</strong><br>Percent change from old to new value: ${F(change,2)}%.`);break}
  case'cn_triangle':{let a=V('a'),b=V('b'),c=Math.sqrt(a*a+b*b),area=a*b/2;show(`<strong>${F(c,4)} hypotenuse</strong><br>Area: ${F(area,4)}; perimeter: ${F(a+b+c,4)}.`);break}
  case'cn_stats':{let vals=(document.getElementById('values')?.value||'').split(/[,\s]+/).map(Number).filter(Number.isFinite);if(!vals.length){show('Enter at least one number.');break}let mean=vals.reduce((x,y)=>x+y,0)/vals.length,sorted=[...vals].sort((x,y)=>x-y),mid=Math.floor(sorted.length/2),median=sorted.length%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2,sd=Math.sqrt(vals.reduce((s,x)=>s+(x-mean)**2,0)/Math.max(1,vals.length-1));show(`<strong>${F(mean,4)} mean</strong><br>Median: ${F(median,4)}; sample standard deviation: ${F(sd,4)}; count: ${vals.length}.`);break}
  case'cn_random':{let min=Math.ceil(V('min')),max=Math.floor(V('max'));if(max<min){let t=min;min=max;max=t}let val=Math.floor(Math.random()*(max-min+1))+min;show(`<strong>${val}</strong><br>Random integer from ${min} to ${max}.`);break}
  case'cn_age':{let b=new Date(document.getElementById('birth')?.value||''),t=new Date(document.getElementById('target')?.value||'');if(isNaN(b)||isNaN(t)){show('Enter valid dates.');break}let years=t.getFullYear()-b.getFullYear();let before=t.getMonth()<b.getMonth()||(t.getMonth()===b.getMonth()&&t.getDate()<b.getDate());if(before)years--;let days=Math.floor((t-b)/86400000);show(`<strong>${years} years old</strong><br>Total days: ${F(days,0)}.`);renderAge(b,t,years,days);break}
  case'cn_date':{let s=new Date(document.getElementById('start')?.value||''),e2=new Date(document.getElementById('end')?.value||'');if(isNaN(s)||isNaN(e2)){show('Enter valid dates.');break}let days=Math.round((e2-s)/86400000);show(`<strong>${F(days,0)} days</strong><br>End date weekday: ${e2.toLocaleDateString('en-US',{weekday:'long'})}.`);break}
  case'cn_hours':{let total=V('hours')+V('minutes')/60;show(`<strong>${F(total,2)} hours</strong><br>Estimated pay at the entered rate: ${USD(total*V('rate'))}.`);break}
  case'cn_grade':{let pct=V('possible')?V('earned')/V('possible')*100:0,letter=pct>=90?'A':pct>=80?'B':pct>=70?'C':pct>=60?'D':'F';show(`<strong>${F(pct,2)}%</strong><br>Approximate letter grade: ${letter}; weighted points: ${F(pct*V('credits')/100,2)}.`);break}
  case'cn_subnet':{let p=Math.max(0,Math.min(32,V('prefix'))),addresses=Math.pow(2,32-p),usable=p>=31?addresses:Math.max(0,addresses-2);show(`<strong>${F(addresses,0)} addresses</strong><br>Approximate usable IPv4 hosts: ${F(usable,0)}.`);break}
  case'cn_password':{let len=Math.max(4,Math.min(64,Math.floor(V('length')))),chars='ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@$%';let out='';for(let i=0;i<len;i++)out+=chars[Math.floor(Math.random()*chars.length)];show(`<strong>${out}</strong><br>Generated in your browser. Use a password manager for important accounts.`);break}
  case'cn_tip':{let tip=V('bill')*V('tip')/100,total=V('bill')+tip,people=Math.max(1,V('people'));show(`<strong>${USD(total)}</strong><br>Tip: ${USD(tip)}; split per person: ${USD(total/people)}.`);break}
  case'cn_generic':{let base=V('amount'),rate=V('rate')/100,years=V('years'),simple=base*rate*years,compound=base*Math.pow(1+rate,years);show(`<strong>${USD(compound)}</strong><br>Simple change: ${USD(simple)}; compound estimate over ${F(years,1)} years.`);break}
  case'bottleneck':{let cpu=V('cpu_score'),gpu=V('gpu_score'),res=V('resolution'),refresh=Math.max(30,V('refresh')),work=document.getElementById('workload')?.value||'gaming';let resLoad=res>=2160?1.35:res>=1440?1.12:0.9,refreshLoad=Math.min(1.6,Math.max(.75,refresh/144)),workCpu=work==='streaming'?1.18:work==='productivity'?0.92:1,workGpu=work==='productivity'?0.9:1;let cpuCap=cpu/(refreshLoad*workCpu),gpuNeed=gpu*resLoad*workGpu,ratio=cpuCap/Math.max(1,gpuNeed),pct=Math.min(99,Math.abs(1-ratio)*100),type=ratio<0.92?'CPU bottleneck':ratio>1.12?'GPU bottleneck':'balanced';show(`<strong>${type}: ${F(pct,1)}%</strong><br>Estimated from CPU score, GPU score, resolution, refresh rate, and workload.`);break}
  case'gpu_compute':{let cores=V('cores'),clock=V('clock')/1000,ops=V('ops'),mem=V('memory_clock'),bus=V('bus'),power=Math.max(1,V('power'));let tflops=cores*clock*ops/1000,bandwidth=mem*bus/8,eff=tflops/power;show(`<strong>${F(tflops,2)} TFLOPS</strong><br>Memory bandwidth: ${F(bandwidth,0)} GB/s; efficiency: ${F(eff,3)} TFLOPS per watt.`);break}
  case'ai_compute':{let params=V('params_b')*1e9,tokens=V('tokens_b')*1e9,gpus=Math.max(1,V('gpu_count')),tflops=V('gpu_tflops'),util=Math.max(1,V('utilization'))/100,power=V('power_kw');let flops=6*params*tokens,effective=gpus*tflops*1e12*util,hours=flops/effective/3600,days=hours/24,pflopDays=flops/1e15/86400,energy=power*hours;show(`<strong>${F(pflopDays,2)} PFLOP-days</strong><br>Estimated training time: ${F(days,2)} days; GPU hours: ${F(hours*gpus,0)}.`);break}
  case'ai_cost':{let req=V('requests'),input=V('input_tokens'),output=V('output_tokens'),inPrice=V('input_price'),outPrice=V('output_price'),days=V('days');let daily=req*((input/1000000)*inPrice+(output/1000000)*outPrice),monthly=daily*days,perReq=daily/Math.max(1,req);show(`<strong>${USD(monthly)} / billing period</strong><br>Daily cost: ${USD(daily)}; cost per request: ${USD(perReq)}.`);break}
  case'mining_profit':{let rev=V('revenue'),power=V('power'),elec=V('electricity'),fee=V('pool_fee')/100,hardware=V('hardware'),uptime=V('uptime')/100;let gross=rev*uptime,energy=power/1000*24*elec*uptime,fees=gross*fee,profit=gross-energy-fees,payback=profit>0?hardware/profit:Infinity;show(`<strong>${USD(profit)} / day</strong><br>Electricity: ${USD(energy)} / day; payback: ${Number.isFinite(payback)?F(payback,0)+' days':'not profitable'} at entered values.`);break}
  case'power_supply':{let base=V('cpu_watts')+V('gpu_watts')+V('drives')+V('fans')+V('other'),recommended=base*(1+V('headroom')/100),standard=[450,500,550,600,650,700,750,850,1000,1200,1300,1500,1600],psu=standard.find(x=>x>=recommended)||Math.ceil(recommended/100)*100;show(`<strong>${F(psu,0)} W PSU</strong><br>Estimated load: ${F(base,0)} W; with headroom: ${F(recommended,0)} W.`);break}
  case'electrical_load':{let a=V('watts')/V('volts'),b=a*V('factor')/100;show(`<strong>${F(a,2)} A load</strong><br>${F(b,2)} A planning current at ${F(V('factor'),0)}%.`);break}
 }
 renderGenericFromEngine(e);
}
function currentEngine(){return document.querySelector('[data-engine]')?.dataset.engine||''}
document.addEventListener('click',e=>{const btn=e.target.closest('[data-engine]');if(btn)calc(btn.dataset.engine)});
document.addEventListener('click',e=>{if(e.target.closest('[data-clear]'))clearCalcForm()});
document.addEventListener('input',e=>{if(e.target.closest('.calc')){const engine=currentEngine();if(engine)calc(engine)}});
document.addEventListener('change',e=>{if(e.target.closest('.calc')){const engine=currentEngine();if(engine)calc(engine)}});
document.addEventListener('DOMContentLoaded',()=>{const engine=currentEngine();if(engine)calc(engine)});

// Generic dashboard rendering
function drawGenericBars(canvas, bars) {
  if (!canvas) return;
  const ctx = clearCanvas(canvas);
  const max = Math.max(...bars.map(x => Math.abs(x.value)), 1);
  const total = bars.reduce((s, x) => s + Math.abs(x.value), 0) || 1;
  const colors = ["#173f73", "#c0333a", "#6f91bd", "#f0a8ae", "#8aa4c6"];
  ctx.font = "700 13px system-ui, sans-serif";
  bars.slice(0, 6).forEach((bar, index) => {
    const y = 34 + index * 40;
    const label = String(bar.label).slice(0, 22);
    const width = (canvas.width - 210) * Math.abs(bar.value) / max;
    const pct = Math.abs(bar.value) / total * 100;
    ctx.fillStyle = "#344054";
    ctx.fillText(label, 16, y + 16);
    ctx.fillStyle = "#eef3f8";
    ctx.fillRect(158, y, canvas.width - 198, 24);
    ctx.fillStyle = colors[index % colors.length];
    ctx.fillRect(158, y, Math.max(4, width), 24);
    ctx.fillStyle = "#152033";
    ctx.fillText(`${bar.display || F(bar.value, 2)} (${F(pct,1)}%)`, 166 + Math.max(8, width), y + 17);
  });
}

function renderGeneric(cards, bars, rows) {
  const summary = document.getElementById("genericSummary");
  const chart = document.getElementById("genericChart");
  const table = document.querySelector("#genericTable tbody");
  if (!summary || !chart || !table) return;
  summary.innerHTML = cards.slice(0, 4).map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
  if (chart.dataset.chartType === "pie") drawPie(chart, bars.map(x => Math.abs(x.value)), bars.map(x => x.label));
  else drawGenericBars(chart, bars);
  table.innerHTML = rows.map(row => `<tr><td>${row[0]}</td><td>${row[1]}</td><td>${row[2]}</td></tr>`).join("");
}

function renderGenericFromEngine(engine) {
  if (!document.getElementById("genericSummary")) return;
  let cards=[], bars=[], rows=[];
  if (engine === "loan") {
    const P=V('amount'), rr=V('apr')/1200, n=Math.max(1,(V('years')*12)+(V('months_extra')||V('months'))), pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n, total=pay*n, interest=total-P;
    cards=[["Monthly payment",USD(pay),"Estimated recurring payment."],["Total paid",USD(total),"Principal plus interest."],["Total interest",USD(interest),"Cost of borrowing."],["Loan term",`${F(n,0)} months`,"Entered repayment period."]];
    bars=[{label:"Principal",value:P,display:USD(P)},{label:"Interest",value:interest,display:USD(interest)},{label:"Monthly payment",value:pay,display:USD(pay)}];
    rows=[["Loan amount",USD(P),"Starting balance."],["APR",`${F(V('apr'),2)}%`,"Annual percentage rate."],["Term",`${F(n,0)} months`,"Number of payments."],["Total paid",USD(total),"Payment multiplied by term."]];
  } else if (engine === "car_loan") {
    const price=V('price'), tax=price*V('tax')/100, fees=V('fees'), include=(document.getElementById('include_fees')?.value||'0')==='1', base=Math.max(0,price-V('incentives')-V('down')-V('trade')+V('owed')), P=Math.max(0,base+(include?tax+fees:0)), rr=V('apr')/1200, n=Math.max(1,V('months')), pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n, total=pay*n, upfront=V('down')+(include?0:tax+fees);
    cards=[["Monthly Pay",USD(pay),"Estimated auto loan payment."],["Total Loan Amount",USD(P),"Amount financed."],["Sale Tax",USD(tax),"Estimated tax from entered rate."],["Upfront Payment",USD(upfront),"Down payment plus taxes and fees when not financed."]];
    bars=[{label:"Loan amount",value:P,display:USD(P)},{label:"Interest",value:total-P,display:USD(total-P)},{label:"Upfront",value:upfront,display:USD(upfront)}];
    rows=[["Monthly Pay",USD(pay),"Payment every month."],["Total Loan Amount",USD(P),"Balance used for amortization."],["Total of Payments",USD(total),"Monthly payment times term."],["Total Loan Interest",USD(total-P),"Total paid minus loan amount."],["Sale Tax",USD(tax),"Auto price times tax rate."],["Upfront Payment",USD(upfront),"Due at purchase if not financed."]];
  } else if (engine === "compound" || engine === "cn_retirement") {
    const P=V('principal'), rr=V('rate')/1200, n=V('years')*12, pmt=V('monthly'), fv=P*Math.pow(1+rr,n)+(rr?pmt*(Math.pow(1+rr,n)-1)/rr:pmt*n), contrib=P+pmt*n, growth=fv-contrib;
    cards=[["Future value",USD(fv),"Projected ending balance."],["Contributions",USD(contrib),"Starting amount plus deposits."],["Growth",USD(growth),"Estimated investment return."],["Time",`${F(V('years'),1)} years`,"Growth period."]];
    bars=[{label:"Starting amount",value:P,display:USD(P)},{label:"Deposits",value:pmt*n,display:USD(pmt*n)},{label:"Growth",value:growth,display:USD(growth)}];
    rows=[["Starting amount",USD(P),"Initial balance."],["Monthly contribution",USD(pmt),"Recurring addition."],["Annual return",`${F(V('rate'),2)}%`,"Assumed return."],["Projected balance",USD(fv),"Estimate before taxes and fees."]];
  } else if (engine === "cn_bmi" || engine === "cn_body_metric") {
    const h=V('feet')*12+V('inches'), bmi=h?703*V('weight')/(h*h):0, low=18.5*h*h/703, high=24.9*h*h/703;
    cards=[["BMI",F(bmi,1),"Adult screening estimate."],["Weight",`${F(V('weight'),1)} lb`,"Entered body weight."],["Healthy range",`${F(low,0)}-${F(high,0)} lb`,"BMI 18.5 to 24.9 range."],["Height",`${F(h,0)} in`,"Total height in inches."]];
    bars=[{label:"BMI",value:bmi,display:F(bmi,1)},{label:"Current weight",value:V('weight'),display:`${F(V('weight'),0)} lb`},{label:"Range low",value:low,display:`${F(low,0)} lb`},{label:"Range high",value:high,display:`${F(high,0)} lb`}];
    rows=[["BMI formula",`703 x weight / height^2`,"US customary formula."],["Current BMI",F(bmi,1),"Screening value."],["Lower reference",`${F(low,0)} lb`,"BMI 18.5."],["Upper reference",`${F(high,0)} lb`,"BMI 24.9."]];
  } else if (engine === "cn_calorie") {
    const h=(V('feet')*12+V('inches'))*2.54, kg=V('weight')*0.453592, age=V('age'), sex=document.getElementById('sex')?.value||'male', bmr=10*kg+6.25*h-5*age+(sex==='male'?5:-161), tdee=bmr*V('activity');
    cards=[["Daily calories",F(tdee,0),"Estimated maintenance calories."],["BMR",F(bmr,0),"Estimated resting burn."],["Protein range",`${F(kg*1.6,0)}-${F(kg*2.2,0)} g`,"Common athletic planning range."],["Activity factor",F(V('activity'),3),"Selected multiplier."]];
    bars=[{label:"BMR",value:bmr,display:F(bmr,0)},{label:"Daily calories",value:tdee,display:F(tdee,0)},{label:"Protein low",value:kg*1.6,display:`${F(kg*1.6,0)} g`},{label:"Protein high",value:kg*2.2,display:`${F(kg*2.2,0)} g`}];
    rows=[["Weight",`${F(V('weight'),1)} lb`,"Converted internally to kilograms."],["Height",`${F(h,0)} cm`,"Converted from feet and inches."],["Age",F(age,0),"Entered age."],["Formula",sex==="male"?"Male Mifflin-St Jeor":"Female Mifflin-St Jeor","Screening estimate."]];
  } else if (engine === "cn_tip") {
    const tip=V('bill')*V('tip')/100,total=V('bill')+tip,people=Math.max(1,V('people'));
    cards=[["Total bill",USD(total),"Bill plus tip."],["Tip amount",USD(tip),"Calculated from tip rate."],["Per person",USD(total/people),"Split total."],["Tip rate",`${F(V('tip'),1)}%`,"Entered percentage."]];
    bars=[{label:"Bill",value:V('bill'),display:USD(V('bill'))},{label:"Tip",value:tip,display:USD(tip)},{label:"Per person",value:total/people,display:USD(total/people)}];
    rows=[["Bill",USD(V('bill')),"Before tip."],["Tip",USD(tip),"Additional amount."],["People",F(people,0),"Split count."],["Total",USD(total),"Final amount."]];
  } else if (engine === "cn_date" || engine === "cn_due_date") {
    const start=new Date(document.getElementById(engine==="cn_date"?'start':'date')?.value||''), days=engine==="cn_date"?Math.round((new Date(document.getElementById('end')?.value||'')-start)/86400000):V('days');
    const end=engine==="cn_date"?new Date(document.getElementById('end')?.value||''):new Date(start.getTime()+days*86400000);
    if (isNaN(start)||isNaN(end)) return;
    cards=[["Day difference",`${F(days,0)} days`,"Calendar day span."],["Weeks",F(days/7,1),"Days divided by 7."],["Months",F(days/30.436875,1),"Average month estimate."],["End weekday",end.toLocaleDateString("en-US",{weekday:"long"}),"Day of week."]];
    bars=[{label:"Days",value:Math.abs(days),display:F(days,0)},{label:"Weeks",value:Math.abs(days/7),display:F(days/7,1)},{label:"Months",value:Math.abs(days/30.436875),display:F(days/30.436875,1)}];
    rows=[["Start date",start.toLocaleDateString("en-US"),"Entered start."],["End date",end.toLocaleDateString("en-US"),"Calculated or entered end."],["Days",F(days,0),"Difference in days."],["Weeks",F(days/7,2),"Approximate weeks."]];
  } else if (engine === "cn_pace") {
    const sec=V('hours')*3600+V('minutes')*60+V('seconds'), dist=Math.max(0.0001,V('distance')), pace=sec/dist, mph=dist/(sec/3600);
    cards=[["Pace",`${Math.floor(pace/60)}:${String(Math.round(pace%60)).padStart(2,'0')} / mile`,"Average pace."],["Speed",`${F(mph,2)} mph`,"Average speed."],["Distance",`${F(dist,2)} miles`,"Entered distance."],["Time",`${F(sec/60,1)} min`,"Total elapsed time."]];
    bars=[{label:"Time minutes",value:sec/60,display:F(sec/60,1)},{label:"Distance",value:dist,display:F(dist,2)},{label:"Speed",value:mph,display:F(mph,2)}];
    rows=[["Hours",F(V('hours'),0),"Entered time."],["Minutes",F(V('minutes'),0),"Entered time."],["Seconds",F(V('seconds'),0),"Entered time."],["Pace",`${Math.floor(pace/60)}:${String(Math.round(pace%60)).padStart(2,'0')}`,"Per mile."]];
  } else if (engine === "cn_simple_interest") {
    const P=V('principal'), interest=P*V('rate')/100*V('years'), total=P+interest;
    cards=[["Ending balance",USD(total),"Principal plus interest."],["Interest earned",USD(interest),"Simple interest amount."],["Principal",USD(P),"Starting amount."],["Rate",`${F(V('rate'),2)}%`,"Annual simple rate."]];
    bars=[{label:"Principal",value:P,display:USD(P)},{label:"Interest",value:interest,display:USD(interest)}];
    rows=[["Principal",USD(P),"Starting balance."],["Rate",`${F(V('rate'),2)}%`,"Annual rate."],["Time",`${F(V('years'),2)} years`,"Entered period."],["Ending balance",USD(total),"Principal plus interest."]];
  } else if (engine === "cn_tax_salary") {
    const income=V('income'), taxable=Math.max(0,income-V('deductions')), tax=taxable*V('taxrate')/100, net=income-tax;
    cards=[["Take-home pay",USD(net),"Estimated annual net pay."],["Monthly net",USD(net/12),"Estimated monthly take-home."],["Estimated tax",USD(tax),"Taxable income times rate."],["Taxable income",USD(taxable),"Income minus deductions."]];
    bars=[{label:"Take-home",value:net,display:USD(net)},{label:"Tax",value:tax,display:USD(tax)},{label:"Deductions",value:V('deductions'),display:USD(V('deductions'))}];
    rows=[["Gross income",USD(income),"Entered annual income."],["Deductions",USD(V('deductions')),"Entered deductions."],["Effective rate",`${F(V('taxrate'),2)}%`,"Applied to taxable income."],["Net pay",USD(net),"Estimated take-home."]];
  } else if (engine === "cn_percent") {
    const pct=V('whole')?V('part')/V('whole')*100:0, change=V('old')?(V('new')-V('old'))/V('old')*100:0;
    cards=[["Percentage",`${F(pct,2)}%`,"Part as a share of whole."],["Percent change",`${F(change,2)}%`,"New versus old value."],["Difference",F(V('new')-V('old'),2),"New value minus old value."],["Whole",F(V('whole'),2),"Entered denominator."]];
    bars=[{label:"Part",value:V('part'),display:F(V('part'),2)},{label:"Whole",value:V('whole'),display:F(V('whole'),2)},{label:"Old",value:V('old'),display:F(V('old'),2)},{label:"New",value:V('new'),display:F(V('new'),2)}];
    rows=[["Part / whole",`${F(V('part'),2)} / ${F(V('whole'),2)}`,"Percentage inputs."],["Percentage",`${F(pct,2)}%`,"Part divided by whole."],["Old to new",`${F(V('old'),2)} to ${F(V('new'),2)}`,"Change inputs."],["Percent change",`${F(change,2)}%`,"Relative change."]];
  } else if (engine === "discount") {
    const savings=V('price')*V('discount')/100, final=V('price')-savings;
    cards=[["Sale price",USD(final),"Price after discount."],["Savings",USD(savings),"Discount amount."],["Original price",USD(V('price')),"Entered price."],["Discount",`${F(V('discount'),1)}%`,"Entered discount rate."]];
    bars=[{label:"Sale price",value:final,display:USD(final)},{label:"Savings",value:savings,display:USD(savings)}];
    rows=[["Original price",USD(V('price')),"Before discount."],["Discount",`${F(V('discount'),2)}%`,"Rate applied."],["Savings",USD(savings),"Amount removed."],["Final price",USD(final),"After discount."]];
  } else if (engine === "cn_triangle") {
    const a=V('a'), b=V('b'), c=Math.sqrt(a*a+b*b), area=a*b/2, perimeter=a+b+c;
    cards=[["Hypotenuse",F(c,4),"Right-triangle side c."],["Area",F(area,4),"a x b / 2."],["Perimeter",F(perimeter,4),"a + b + c."],["Angle A",`${F(Math.atan2(a,b)*180/Math.PI,2)}°`,"Opposite side a."]];
    bars=[{label:"Side a",value:a,display:F(a,2)},{label:"Side b",value:b,display:F(b,2)},{label:"Side c",value:c,display:F(c,2)},{label:"Area",value:area,display:F(area,2)}];
    rows=[["Side a",F(a,4),"Entered leg."],["Side b",F(b,4),"Entered leg."],["Hypotenuse",F(c,4),"Pythagorean theorem."],["Perimeter",F(perimeter,4),"Sum of sides."]];
  } else if (engine === "cn_stats") {
    const vals=(document.getElementById('values')?.value||'').split(/[,\s]+/).map(Number).filter(Number.isFinite);
    if (!vals.length) return;
    const mean=vals.reduce((x,y)=>x+y,0)/vals.length, sorted=[...vals].sort((x,y)=>x-y), mid=Math.floor(sorted.length/2), median=sorted.length%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2, min=sorted[0], max=sorted[sorted.length-1], sd=Math.sqrt(vals.reduce((s,x)=>s+(x-mean)**2,0)/Math.max(1,vals.length-1));
    cards=[["Mean",F(mean,4),"Average value."],["Median",F(median,4),"Middle value."],["Std. dev.",F(sd,4),"Sample standard deviation."],["Count",F(vals.length,0),"Numbers included."]];
    bars=[{label:"Minimum",value:min,display:F(min,2)},{label:"Mean",value:mean,display:F(mean,2)},{label:"Median",value:median,display:F(median,2)},{label:"Maximum",value:max,display:F(max,2)}];
    rows=[["Minimum",F(min,4),"Lowest value."],["Maximum",F(max,4),"Highest value."],["Range",F(max-min,4),"Maximum minus minimum."],["Sample SD",F(sd,4),"Dispersion estimate."]];
  } else if (engine === "cn_random") {
    const min=Math.ceil(V('min')), max=Math.floor(V('max')), count=Math.max(1,max-min+1);
    cards=[["Range size",F(count,0),"Possible integer results."],["Minimum",F(min,0),"Lower bound."],["Maximum",F(max,0),"Upper bound."],["Chance each",`${F(100/count,2)}%`,"Uniform random estimate."]];
    bars=[{label:"Minimum",value:min,display:F(min,0)},{label:"Maximum",value:max,display:F(max,0)},{label:"Range size",value:count,display:F(count,0)}];
    rows=[["Minimum",F(min,0),"Included bound."],["Maximum",F(max,0),"Included bound."],["Possible results",F(count,0),"Inclusive integer count."],["Per-result chance",`${F(100/count,2)}%`,"If uniformly random."]];
  } else if (engine === "cn_hours") {
    const total=V('hours')+V('minutes')/60, pay=total*V('rate');
    cards=[["Total hours",F(total,2),"Hours plus minutes."],["Estimated pay",USD(pay),"Hours times rate."],["Minutes",F(total*60,0),"Total minutes."],["Hourly rate",USD(V('rate')),"Entered rate."]];
    bars=[{label:"Hours",value:V('hours'),display:F(V('hours'),2)},{label:"Extra minutes",value:V('minutes')/60,display:F(V('minutes')/60,2)},{label:"Pay",value:pay,display:USD(pay)}];
    rows=[["Hours",F(V('hours'),2),"Entered whole hours."],["Minutes",F(V('minutes'),0),"Converted to decimal hours."],["Total hours",F(total,2),"Combined time."],["Pay",USD(pay),"Estimated earnings."]];
  } else if (engine === "cn_grade") {
    const pct=V('possible')?V('earned')/V('possible')*100:0, letter=pct>=90?'A':pct>=80?'B':pct>=70?'C':pct>=60?'D':'F';
    cards=[["Grade",`${F(pct,2)}%`,"Earned divided by possible."],["Letter",letter,"Approximate US letter grade."],["Weighted points",F(pct*V('credits')/100,2),"Percent times credits or weight."],["Missing points",F(V('possible')-V('earned'),2),"Possible minus earned."]];
    bars=[{label:"Earned",value:V('earned'),display:F(V('earned'),2)},{label:"Missing",value:Math.max(0,V('possible')-V('earned')),display:F(Math.max(0,V('possible')-V('earned')),2)}];
    rows=[["Earned",F(V('earned'),2),"Entered earned points."],["Possible",F(V('possible'),2),"Entered possible points."],["Grade",`${F(pct,2)}%`,"Calculated percentage."],["Letter",letter,"Approximate band."]];
  } else if (engine === "cn_subnet") {
    const p=Math.max(0,Math.min(32,V('prefix'))), addresses=Math.pow(2,32-p), usable=p>=31?addresses:Math.max(0,addresses-2);
    cards=[["Addresses",F(addresses,0),"Total IPv4 addresses."],["Usable hosts",F(usable,0),"Common host estimate."],["CIDR",`/${F(p,0)}`,"Entered prefix."],["Network bits",F(p,0),"Fixed bits."]];
    bars=[{label:"Total",value:addresses,display:F(addresses,0)},{label:"Usable",value:usable,display:F(usable,0)},{label:"Reserved",value:addresses-usable,display:F(addresses-usable,0)}];
    rows=[["CIDR prefix",`/${F(p,0)}`,"Entered prefix."],["Host bits",F(32-p,0),"32 minus prefix."],["Addresses",F(addresses,0),"2^(host bits)."],["Usable hosts",F(usable,0),"Common estimate."]];
  } else if (engine === "cn_password") {
    const len=Math.max(4,Math.min(64,Math.floor(V('length')))), charset=55, entropy=len*Math.log2(charset);
    cards=[["Length",F(len,0),"Generated password length."],["Entropy",`${F(entropy,1)} bits`,"Approximate character-space entropy."],["Character set",F(charset,0),"Letters, numbers, and symbols."],["Generated locally","Yes","Runs in browser only."]];
    bars=[{label:"Length",value:len,display:F(len,0)},{label:"Entropy bits",value:entropy,display:F(entropy,1)},{label:"Character set",value:charset,display:F(charset,0)}];
    rows=[["Length",F(len,0),"Entered length."],["Approx. entropy",`${F(entropy,1)} bits`,"Planning estimate."],["Storage advice","Use a password manager","For important accounts."],["Generation","Browser-side","No account required."]];
  } else if (engine === "bottleneck") {
    const cpu=V('cpu_score'), gpu=V('gpu_score'), res=V('resolution'), refresh=Math.max(30,V('refresh')), work=document.getElementById('workload')?.value||'gaming', resLoad=res>=2160?1.35:res>=1440?1.12:0.9, refreshLoad=Math.min(1.6,Math.max(.75,refresh/144)), workCpu=work==='streaming'?1.18:work==='productivity'?0.92:1, workGpu=work==='productivity'?0.9:1, cpuCap=cpu/(refreshLoad*workCpu), gpuNeed=gpu*resLoad*workGpu, ratio=cpuCap/Math.max(1,gpuNeed), pct=Math.min(99,Math.abs(1-ratio)*100), type=ratio<0.92?'CPU bottleneck':ratio>1.12?'GPU bottleneck':'Balanced';
    cards=[["Likely result",type,"Estimated limiting side."],["Bottleneck index",`${F(pct,1)}%`,"Distance from balanced score."],["CPU headroom",F(cpuCap,0),"Adjusted CPU capacity."],["GPU demand",F(gpuNeed,0),"Adjusted GPU load."]];
    bars=[{label:"CPU headroom",value:cpuCap,display:F(cpuCap,0)},{label:"GPU demand",value:gpuNeed,display:F(gpuNeed,0)},{label:"Bottleneck",value:pct,display:`${F(pct,1)}%`}];
    rows=[["CPU score",F(cpu,0),"Entered benchmark score."],["GPU score",F(gpu,0),"Entered benchmark score."],["Resolution",`${F(res,0)}p`,"Higher resolution shifts load toward GPU."],["Refresh target",`${F(refresh,0)} Hz`,"Higher refresh increases CPU demand."],["Workload",work,"Selected usage model."]];
  } else if (engine === "gpu_compute") {
    const cores=V('cores'), clock=V('clock')/1000, ops=V('ops'), mem=V('memory_clock'), bus=V('bus'), power=Math.max(1,V('power')), tflops=cores*clock*ops/1000, bandwidth=mem*bus/8, eff=tflops/power;
    cards=[["FP32 compute",`${F(tflops,2)} TFLOPS`,"Theoretical peak estimate."],["Bandwidth",`${F(bandwidth,0)} GB/s`,"Memory throughput estimate."],["Efficiency",`${F(eff,3)} TFLOPS/W`,"Compute divided by board power."],["Boost clock",`${F(clock,2)} GHz`,"Entered boost frequency."]];
    bars=[{label:"TFLOPS",value:tflops,display:F(tflops,2)},{label:"Bandwidth",value:bandwidth,display:`${F(bandwidth,0)} GB/s`},{label:"Power",value:power,display:`${F(power,0)} W`}];
    rows=[["GPU cores",F(cores,0),"Shader/CUDA-style units."],["Boost clock",`${F(clock,3)} GHz`,"Clock in GHz."],["Operations/cycle",F(ops,0),"Selected math model."],["Memory bus",`${F(bus,0)} bit`,"Entered bus width."],["Board power",`${F(power,0)} W`,"Used for efficiency."]];
  } else if (engine === "ai_compute") {
    const params=V('params_b')*1e9, tokens=V('tokens_b')*1e9, gpus=Math.max(1,V('gpu_count')), tflops=V('gpu_tflops'), util=Math.max(1,V('utilization'))/100, power=V('power_kw'), flops=6*params*tokens, effective=gpus*tflops*1e12*util, hours=flops/effective/3600, days=hours/24, petaDays=flops/1e15/86400, gpuHours=hours*gpus, energy=power*hours;
    cards=[["Training compute",`${F(petaDays,2)} PFLOP-days`,"Approximate total training work."],["Training time",`${F(days,2)} days`,"Wall-clock time at entered throughput."],["GPU hours",F(gpuHours,0),"GPU count times wall-clock hours."],["Energy use",`${F(energy,0)} kWh`,"Cluster power times hours."]];
    bars=[{label:"PFLOP-days",value:petaDays,display:F(petaDays,2)},{label:"GPU hours",value:gpuHours,display:F(gpuHours,0)},{label:"Energy kWh",value:energy,display:F(energy,0)}];
    rows=[["Model size",`${F(params/1e9,2)}B parameters`,"Entered parameter count."],["Training tokens",`${F(tokens/1e9,2)}B tokens`,"Entered token count."],["Total FLOPs",`${F(flops/1e21,2)}e21`,"6 x parameters x tokens."],["Effective throughput",`${F(effective/1e15,2)} PFLOPS`,"GPU count x TFLOPS x utilization."],["GPU count",F(gpus,0),"Accelerators used."],["Utilization",`${F(util*100,1)}%`,"Effective hardware utilization."]];
  } else if (engine === "ai_cost") {
    const req=V('requests'), input=V('input_tokens'), output=V('output_tokens'), inPrice=V('input_price'), outPrice=V('output_price'), days=V('days'), inputCost=req*days*input/1000000*inPrice, outputCost=req*days*output/1000000*outPrice, total=inputCost+outputCost, daily=total/Math.max(1,days);
    cards=[["Billing-period cost",USD(total),"Input plus output token cost."],["Daily cost",USD(daily),"Average cost per day."],["Input token cost",USD(inputCost),"Prompt/context portion."],["Output token cost",USD(outputCost),"Generated response portion."]];
    bars=[{label:"Input cost",value:inputCost,display:USD(inputCost)},{label:"Output cost",value:outputCost,display:USD(outputCost)},{label:"Daily cost",value:daily,display:USD(daily)}];
    rows=[["Requests",`${F(req,0)} / day`,"Estimated daily API calls."],["Input tokens",F(input,0),"Average prompt/context tokens."],["Output tokens",F(output,0),"Average generated tokens."],["Input price",USD(inPrice),"Per 1M input tokens."],["Output price",USD(outPrice),"Per 1M output tokens."],["Billing days",F(days,0),"Days included."]];
  } else if (engine === "mining_profit") {
    const rev=V('revenue'), power=V('power'), elec=V('electricity'), fee=V('pool_fee')/100, hardware=V('hardware'), uptime=V('uptime')/100, gross=rev*uptime, energy=power/1000*24*elec*uptime, fees=gross*fee, profit=gross-energy-fees, monthly=profit*30, payback=profit>0?hardware/profit:Infinity;
    cards=[["Daily profit",USD(profit),"Revenue minus power and fees."],["Monthly profit",USD(monthly),"Daily profit times 30."],["Electricity/day",USD(energy),"Power draw times kWh rate."],["Payback",Number.isFinite(payback)?`${F(payback,0)} days`:"Not profitable","Hardware cost divided by profit."]];
    bars=[{label:"Gross revenue",value:gross,display:USD(gross)},{label:"Electricity",value:energy,display:USD(energy)},{label:"Pool fees",value:fees,display:USD(fees)},{label:"Profit",value:profit,display:USD(profit)}];
    rows=[["Revenue",USD(rev),"Estimated daily mining revenue before uptime."],["Power draw",`${F(power,0)} W`,"Miner load."],["Electricity rate",USD(elec),"Cost per kWh."],["Pool fee",`${F(fee*100,2)}%`,"Deducted from gross revenue."],["Uptime",`${F(uptime*100,1)}%`,"Operational time assumption."],["Hardware cost",USD(hardware),"Used for payback."]];
  } else if (engine === "power_supply") {
    const cpu=V('cpu_watts'), gpu=V('gpu_watts'), drives=V('drives'), fans=V('fans'), other=V('other'), base=cpu+gpu+drives+fans+other, recommended=base*(1+V('headroom')/100), standard=[450,500,550,600,650,700,750,850,1000,1200,1300,1500,1600], psu=standard.find(x=>x>=recommended)||Math.ceil(recommended/100)*100;
    cards=[["Recommended PSU",`${F(psu,0)} W`,"Next common PSU size."],["Estimated load",`${F(base,0)} W`,"Component wattage total."],["With headroom",`${F(recommended,0)} W`,"Load plus safety margin."],["Headroom",`${F(V('headroom'),0)}%`,"Entered planning margin."]];
    bars=[{label:"CPU",value:cpu,display:`${F(cpu,0)} W`},{label:"GPU",value:gpu,display:`${F(gpu,0)} W`},{label:"Storage",value:drives,display:`${F(drives,0)} W`},{label:"Cooling",value:fans,display:`${F(fans,0)} W`},{label:"Other",value:other,display:`${F(other,0)} W`}];
    rows=[["CPU",`${F(cpu,0)} W`,"Entered CPU power."],["GPU",`${F(gpu,0)} W`,"Entered GPU power."],["Drives/storage",`${F(drives,0)} W`,"Storage estimate."],["Fans/cooling/RGB",`${F(fans,0)} W`,"Cooling and lighting load."],["Other devices",`${F(other,0)} W`,"Additional system load."],["Recommended PSU",`${F(psu,0)} W`,"Rounded to a common size."]];
  } else if (engine === "cn_generic") {
    const inputs=Array.from(document.querySelectorAll(".calc input,.calc select")).filter(el=>el.type!=="hidden");
    const numeric=inputs.map(el=>({label:el.previousElementSibling?.textContent||el.id,value:parseFloat(el.value)})).filter(x=>Number.isFinite(x.value));
    const primary=numeric[0]?.value||0, secondary=numeric[1]?.value||0, result=numeric.reduce((s,x)=>s+x.value,0);
    cards=[["Primary value",F(primary,2),"First entered value."],["Second value",F(secondary,2),"Second entered value when available."],["Input total",F(result,2),"Sum of numeric inputs."],["Fields used",F(numeric.length,0),"Numeric values read from the form."]];
    bars=numeric.slice(0,6).map(x=>({label:x.label,value:x.value,display:F(x.value,2)}));
    rows=numeric.map(x=>[x.label,F(x.value,4),"Entered value."]);
  } else {
    const inputs=Array.from(document.querySelectorAll(".calc input,.calc select")).filter(el=>el.type!=="hidden"&&el.type!=="checkbox");
    const numeric=inputs.map(el=>({label:el.previousElementSibling?.textContent||el.closest('.field')?.querySelector('label')?.textContent||el.id,value:parseFloat(el.value)})).filter(x=>Number.isFinite(x.value));
    const result=numeric.reduce((s,x)=>s+x.value,0);
    const largest=numeric.slice().sort((a,b)=>Math.abs(b.value)-Math.abs(a.value))[0];
    cards=[["Calculated output",document.querySelector("#result strong")?.textContent||"Ready","Main result from the calculator."],["Input total",F(result,2),"Sum of numeric values entered."],["Largest input",largest?`${largest.label}: ${F(largest.value,2)}`:"n/a","Largest numeric field."],["Fields used",F(numeric.length,0),"Inputs included in this summary."]];
    bars=numeric.slice(0,6).map(x=>({label:x.label,value:x.value,display:F(x.value,2)}));
    rows=numeric.map(x=>[x.label,F(x.value,4),"Entered value."]);
  }
  renderGeneric(cards,bars.length?bars:[{label:"Result",value:1,display:"Ready"}],rows.length?rows:[["Result","Ready","Enter values to update."]]);
}
// End generic dashboard rendering

// Loan calculator page rendering
function periodsPerYear(key) {
  return {daily:365,weekly:52,biweekly:26,halfmonth:24,month:12,quarter:4,halfyear:2,year:1,annually:1,semiannually:2,quarterly:4,monthly:12,semimonthly:24}[key] || 12;
}

function effectiveRate(annualRate, compoundKey, paybackKey) {
  const paybacks = periodsPerYear(paybackKey || "year");
  if (compoundKey === "continuously") return Math.exp(annualRate / paybacks) - 1;
  const compounds = periodsPerYear(compoundKey || "annually");
  return Math.pow(1 + annualRate / compounds, compounds / paybacks) - 1;
}

function loanTermPeriods(yearId, monthId, paybackKey) {
  const years = V(yearId) + V(monthId) / 12;
  return Math.max(1, Math.round(years * periodsPerYear(paybackKey)));
}

function loanTermYears(yearId, monthId) {
  return Math.max(0, V(yearId) + V(monthId) / 12);
}

function paybackLabel(key) {
  return {daily:"Day",weekly:"Week",biweekly:"2 Weeks",halfmonth:"Half Month",month:"Month",quarter:"Quarter",halfyear:"6 Months",year:"Year"}[key] || "Month";
}

function fillSummary(id, cards) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = cards.map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
}

function fillResultTable(id, rows) {
  const el = document.querySelector(`#${id} tbody`) || document.getElementById(id);
  if (!el) return;
  el.innerHTML = rows.map(row => `<tr><td>${row[0]}</td><td><strong>${row[1]}</strong></td></tr>`).join("");
}

function amortizationRows(principal, rate, periods, payment) {
  let balance = principal;
  const rows = [];
  for (let i = 1; i <= periods && i <= 360 && balance > 0.01; i++) {
    const interest = balance * rate;
    const principalPaid = Math.min(balance, Math.max(0, payment - interest));
    balance = Math.max(0, balance - principalPaid);
    rows.push([i, payment, principalPaid, interest, balance]);
  }
  return rows;
}

function compoundAmount(principal, annualRate, years, compoundKey) {
  if (compoundKey === "continuously") return principal * Math.exp(annualRate * years);
  const compounds = periodsPerYear(compoundKey || "annually");
  return principal * Math.pow(1 + annualRate / compounds, compounds * years);
}

function presentValue(futureValue, annualRate, years, compoundKey) {
  if (compoundKey === "continuously") return futureValue / Math.exp(annualRate * years);
  const compounds = periodsPerYear(compoundKey || "annually");
  return futureValue / Math.pow(1 + annualRate / compounds, compounds * years);
}

function scheduleRows(start, annualRate, years, compoundKey) {
  const out = [];
  const wholeYears = Math.max(1, Math.ceil(years));
  for (let i = 1; i <= wholeYears && i <= 40; i++) {
    const from = compoundAmount(start, annualRate, Math.min(i - 1, years), compoundKey);
    const to = compoundAmount(start, annualRate, Math.min(i, years), compoundKey);
    out.push([i, from, Math.max(0, to - from), to]);
  }
  return out;
}

function renderLoanPage() {
  const payback = document.getElementById("l_payback")?.value || "month";
  const compound = document.getElementById("l_compound")?.value || "monthly";
  const P = V("l_amount"), annual = V("l_rate") / 100, rate = effectiveRate(annual, compound, payback);
  const n = loanTermPeriods("l_years", "l_months", payback);
  const payment = rate ? P * rate * Math.pow(1 + rate, n) / (Math.pow(1 + rate, n) - 1) : P / n;
  const total = payment * n, interest = total - P, payLabel = paybackLabel(payback);
  show(`<strong>${USD(payment)} / ${payLabel.toLowerCase()}</strong><br>Total of ${F(n,0)} payments: ${USD(total)}; total interest: ${USD(interest)}.`);
  fillSummary("loanSummary", [["Payment Every " + payLabel, USD(payment), "Fixed amortized payment."],["Total of " + F(n,0) + " Payments", USD(total), "Payment multiplied by term."],["Total Interest", USD(interest), "Total cost of borrowing."],["Effective Period Rate", `${F(rate*100,4)}%`, "Adjusted for compound and payback frequency."]]);
  fillResultTable("loanResultTable", [["Payment Every " + payLabel, USD(payment)],["Total of " + F(n,0) + " Payments", USD(total)],["Total Interest", USD(interest)]]);
  drawPie(document.getElementById("loanPie"), [P, interest], ["Principal", "Interest"]);
  const amortRows = amortizationRows(P, rate, n, payment);
  const amortBody = document.getElementById("loanAmortRows");
  if (amortBody) amortBody.innerHTML = amortRows.map(row => `<tr><td>${F(row[0],0)}</td><td>${USD(row[1])}</td><td>${USD(row[2])}</td><td>${USD(row[3])}</td><td>${USD(row[4])}</td></tr>`).join("");

  const dP = V("d_amount"), dAnnual = V("d_rate") / 100, dYears = loanTermYears("d_years", "d_months"), dComp = document.getElementById("d_compound")?.value || "annually";
  const due = compoundAmount(dP, dAnnual, dYears, dComp), dInterest = due - dP;
  fillSummary("deferredSummary", [["Amount Due at Loan Maturity", USD(due), "Principal plus compounded interest."],["Total Interest", USD(dInterest), "Interest accrued to maturity."],["Loan Amount", USD(dP), "Starting principal."],["Loan Term", `${F(dYears,2)} years`, "Entered term."]]);
  fillResultTable("deferredResultTable", [["Amount Due at Loan Maturity", USD(due)],["Total Interest", USD(dInterest)]]);
  drawPie(document.getElementById("deferredPie"), [dP, dInterest], ["Principal", "Interest"]);
  const dBody = document.getElementById("deferredRows");
  if (dBody) dBody.innerHTML = scheduleRows(dP, dAnnual, dYears, dComp).map(row => `<tr><td>${F(row[0],0)}</td><td>${USD(row[1])}</td><td>${USD(row[2])}</td><td>${USD(row[3])}</td></tr>`).join("");

  const bDue = V("b_due"), bAnnual = V("b_rate") / 100, bYears = loanTermYears("b_years", "b_months"), bComp = document.getElementById("b_compound")?.value || "annually";
  const received = presentValue(bDue, bAnnual, bYears, bComp), bInterest = bDue - received;
  fillSummary("bondSummary", [["Amount Received When the Loan Starts", USD(received), "Present value of due amount."],["Total Interest", USD(bInterest), "Discount between start and maturity."],["Predetermined Due Amount", USD(bDue), "Face amount paid at maturity."],["Loan Term", `${F(bYears,2)} years`, "Entered term."]]);
  fillResultTable("bondResultTable", [["Amount Received When the Loan Starts", USD(received)],["Total Interest", USD(bInterest)]]);
  drawPie(document.getElementById("bondPie"), [received, bInterest], ["Principal", "Interest"]);
  const bBody = document.getElementById("bondRows");
  if (bBody) bBody.innerHTML = scheduleRows(received, bAnnual, bYears, bComp).map(row => `<tr><td>${F(row[0],0)}</td><td>${USD(row[1])}</td><td>${USD(row[2])}</td><td>${USD(row[3])}</td></tr>`).join("");
}

document.addEventListener("click", event => {
  const trigger = event.target.closest("[data-toggle-table]");
  if (!trigger) return;
  const table = document.getElementById(trigger.dataset.toggleTable);
  if (!table) return;
  table.classList.toggle("is-collapsed");
  trigger.textContent = table.classList.contains("is-collapsed") ? trigger.textContent.replace("Hide", "View") : trigger.textContent.replace("View", "Hide");
});
// End loan calculator page rendering

// Mortgage dashboard rendering
function mortgageRows(principal, monthlyRate, months, payment, extraMonthly = 0, extraYearly = 0, extraOnce = 0) {
  let balance = principal;
  const rows = [];
  for (let month = 1; month <= months && balance > 0.01; month++) {
    const interest = balance * monthlyRate;
    const scheduledPrincipal = Math.max(0, payment - interest);
    const requestedExtra = extraMonthly + (month % 12 === 0 ? extraYearly : 0) + (month === 1 ? extraOnce : 0);
    const principalPaid = Math.min(balance, scheduledPrincipal + requestedExtra);
    const extraPaid = Math.max(0, principalPaid - Math.min(balance, scheduledPrincipal));
    balance = Math.max(0, balance - principalPaid);
    rows.push({ month, interest, principal: principalPaid, extra: extraPaid, balance });
  }
  return rows;
}

function clearCanvas(canvas) {
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  return ctx;
}

function drawPie(canvas, values, labels) {
  const logicalWidth = Number(canvas.dataset.logicalWidth || canvas.getAttribute("width")) || canvas.width;
  const logicalHeight = Number(canvas.dataset.logicalHeight || canvas.getAttribute("height")) || canvas.height;
  canvas.dataset.logicalWidth = String(logicalWidth);
  canvas.dataset.logicalHeight = String(logicalHeight);
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  if (canvas.width !== Math.round(logicalWidth * dpr) || canvas.height !== Math.round(logicalHeight * dpr)) {
    canvas.width = Math.round(logicalWidth * dpr);
    canvas.height = Math.round(logicalHeight * dpr);
  }
  canvas.style.width = `min(100%, ${logicalWidth}px)`;
  canvas.style.height = "auto";
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, logicalWidth, logicalHeight);
  const total = values.reduce((a, b) => a + Math.max(0, b), 0) || 1;
  const colors = ["#173f73", "#c0333a", "#6f91bd", "#f0a8ae", "#d6a13d", "#95a3b8"];
  const compact = logicalWidth <= 380;
  const legendX = compact ? Math.max(166, logicalWidth * .52) : logicalWidth * .58;
  const cx = Math.max(62, Math.min(logicalWidth * .24, legendX - 72));
  const cy = logicalHeight / 2;
  const radius = Math.max(44, Math.min(logicalHeight * .34, legendX - cx - 28));
  const inner = radius * .52;
  let start = -Math.PI / 2;
  values.forEach((value, index) => {
    const amount = Math.max(0, value);
    const angle = amount / total * Math.PI * 2;
    if (angle <= 0) return;
    const mid = start + angle / 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, radius, start, start + angle);
    ctx.closePath();
    ctx.fillStyle = colors[index % colors.length];
    ctx.fill();
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.stroke();
    const pct = amount / total * 100;
    if (pct >= 3) {
      const labelRadius = inner + (radius - inner) * .56;
      const tx = cx + Math.cos(mid) * labelRadius;
      const ty = cy + Math.sin(mid) * labelRadius;
      ctx.save();
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.font = compact ? "800 12px system-ui, sans-serif" : "800 15px system-ui, sans-serif";
      ctx.lineWidth = 4;
      ctx.strokeStyle = "rgba(21,32,51,.55)";
      ctx.strokeText(`${F(pct,1)}%`, tx, ty);
      ctx.fillStyle = "#fff";
      ctx.fillText(`${F(pct,1)}%`, tx, ty);
      ctx.restore();
    }
    start += angle;
  });
  ctx.beginPath();
  ctx.arc(cx, cy, inner, 0, Math.PI * 2);
  ctx.fillStyle = "#fff";
  ctx.fill();
  ctx.fillStyle = "#152033";
  ctx.font = compact ? "800 16px system-ui, sans-serif" : "800 17px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(USD(total).replace(".00", ""), cx, cy - 2);
  ctx.font = compact ? "700 10px system-ui, sans-serif" : "700 11px system-ui, sans-serif";
  ctx.fillStyle = "#667085";
  ctx.fillText(canvas.dataset.centerLabel || "per month", cx, cy + 14);
  ctx.textAlign = "left";
  ctx.fillStyle = "#152033";
  ctx.font = "700 14px system-ui, sans-serif";
  labels.forEach((label, index) => {
    const amount = Math.max(0, values[index]);
    const pct = amount / total * 100;
    const rowGap = compact ? 31 : 38;
    const startY = Math.max(24, cy - ((labels.length - 1) * rowGap) / 2);
    const y = startY + index * rowGap;
    ctx.fillStyle = colors[index % colors.length];
    ctx.fillRect(legendX, y - 11, compact ? 11 : 14, compact ? 11 : 14);
    ctx.fillStyle = "#344054";
    ctx.font = compact ? "700 11px system-ui, sans-serif" : "700 13px system-ui, sans-serif";
    ctx.fillText(`${label} (${F(pct,1)}%)`, legendX + (compact ? 18 : 23), y);
    ctx.font = compact ? "600 10px system-ui, sans-serif" : "600 12px system-ui, sans-serif";
    ctx.fillStyle = "#667085";
    ctx.fillText(USD(amount), legendX + (compact ? 18 : 23), y + (compact ? 14 : 17));
  });
}

function drawLine(canvas, rows, principal) {
  const ctx = clearCanvas(canvas);
  const pad = { left: 54, right: 18, top: 24, bottom: 42 };
  const w = canvas.width - pad.left - pad.right;
  const h = canvas.height - pad.top - pad.bottom;
  ctx.strokeStyle = "#dfe5ee";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + h * i / 4;
    ctx.beginPath();
    ctx.moveTo(pad.left, y);
    ctx.lineTo(pad.left + w, y);
    ctx.stroke();
  }
  ctx.fillStyle = "#667085";
  ctx.font = "12px system-ui, sans-serif";
  ctx.fillText(USD(principal), 6, pad.top + 4);
  ctx.fillText("$0", 28, pad.top + h + 4);
  ctx.beginPath();
  rows.forEach((row, index) => {
    const x = pad.left + w * index / Math.max(1, rows.length - 1);
    const y = pad.top + h - h * row.balance / Math.max(1, principal);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = "#173f73";
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(pad.left, pad.top + h);
  rows.forEach((row, index) => {
    const x = pad.left + w * index / Math.max(1, rows.length - 1);
    const y = pad.top + h - h * row.balance / Math.max(1, principal);
    ctx.lineTo(x, y);
  });
  ctx.lineTo(pad.left + w, pad.top + h);
  ctx.closePath();
  ctx.fillStyle = "rgba(23,63,115,.08)";
  ctx.fill();
  ctx.fillStyle = "#344054";
  ctx.font = "700 12px system-ui, sans-serif";
  ctx.fillText("Start", pad.left, canvas.height - 13);
  ctx.fillText("Payoff", pad.left + w - 42, canvas.height - 13);
}

function renderMortgage(principal, monthlyRate, months, pi, tax, insurance, pmi, hoa, other, increase, extraMonthly, extraYearly, extraOnce, startDate) {
  const summary = document.getElementById("mortgageSummary");
  const pie = document.getElementById("mortgagePie");
  const line = document.getElementById("mortgageLine");
  const table = document.querySelector("#mortgageSchedule tbody");
  const costTable = document.querySelector("#mortgageCostTable tbody");
  if (!summary || !pie || !line || !table || !costTable) return;
  const rows = mortgageRows(principal, monthlyRate, months, pi, extraMonthly, extraYearly, extraOnce);
  const paidMonths = rows.length || months;
  const totalInterest = rows.reduce((s, r) => s + r.interest, 0);
  const totalExtraPaid = rows.reduce((s, r) => s + r.extra, 0);
  let taxTotal = 0, insuranceTotal = 0, pmiTotal = 0, hoaTotal = 0, otherTotal = 0;
  for (let month = 1; month <= paidMonths; month++) {
    const growth = Math.pow(1 + increase / 100, Math.floor((month - 1) / 12));
    taxTotal += tax * growth;
    insuranceTotal += insurance * growth;
    pmiTotal += pmi;
    hoaTotal += hoa;
    otherTotal += other;
  }
  const baseExtra = tax + insurance + pmi + hoa + other;
  const totalMonthlyPayment = pi + baseExtra + extraMonthly;
  const totalCost = principal + totalInterest + taxTotal + insuranceTotal + pmiTotal + hoaTotal + otherTotal;
  const payoffDate = startDate instanceof Date && !Number.isNaN(startDate.valueOf()) ? new Date(startDate) : new Date();
  payoffDate.setMonth(payoffDate.getMonth() + paidMonths);
  summary.innerHTML = [
    ["Monthly Pay", USD(pi), "Principal and interest only."],
    ["Total monthly", USD(totalMonthlyPayment), "Includes selected taxes, insurance, PMI, HOA, other costs, and extra monthly pay."],
    ["Total interest", USD(totalInterest), "Lower when extra payments shorten the loan."],
    ["Payoff date", payoffDate.toLocaleDateString("en-US", { month: "short", year: "numeric" }), `${paidMonths} scheduled payments.`]
  ].map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
  drawPie(pie, [pi, tax, insurance, pmi + hoa + other], ["Principal & interest", "Property tax", "Insurance", "PMI / HOA / other"]);
  drawLine(line, rows, principal);
  costTable.innerHTML = [
    ["Principal & interest", pi, principal + totalInterest],
    ["Property tax", tax, taxTotal],
    ["Home insurance", insurance, insuranceTotal],
    ["PMI", pmi, pmiTotal],
    ["HOA", hoa, hoaTotal],
    ["Other costs", other, otherTotal],
    ["Extra payments", extraMonthly, totalExtraPaid],
    ["Total cost", totalMonthlyPayment, totalCost]
  ].map(row => `<tr><td>${row[0]}</td><td>${USD(row[1])}</td><td>${USD(row[2])}</td></tr>`).join("");
  const yearly = [];
  for (let y = 0; y < Math.ceil(rows.length / 12); y++) {
    const slice = rows.slice(y * 12, y * 12 + 12);
    yearly.push({
      year: y + 1,
      interest: slice.reduce((s, r) => s + r.interest, 0),
      principal: slice.reduce((s, r) => s + r.principal, 0),
      balance: slice.length ? slice[slice.length - 1].balance : 0
    });
  }
  table.innerHTML = yearly.map(row => `<tr><td>${row.year}</td><td>${USD(row.interest)}</td><td>${USD(row.principal)}</td><td>${USD(row.balance)}</td></tr>`).join("");
}
// End mortgage dashboard rendering

// Age dashboard rendering
function drawAgeBars(canvas, values) {
  const ctx = clearCanvas(canvas);
  const labels = ["Years", "Months", "Weeks", "Days"];
  const colors = ["#173f73", "#c0333a", "#6f91bd", "#f0a8ae"];
  const max = Math.max(...values, 1);
  ctx.font = "700 13px system-ui, sans-serif";
  values.forEach((value, index) => {
    const y = 42 + index * 54;
    const width = (canvas.width - 180) * value / max;
    ctx.fillStyle = "#344054";
    ctx.fillText(labels[index], 18, y + 17);
    ctx.fillStyle = "#eef3f8";
    ctx.fillRect(92, y, canvas.width - 130, 24);
    ctx.fillStyle = colors[index];
    ctx.fillRect(92, y, Math.max(3, width), 24);
    ctx.fillStyle = "#152033";
    ctx.fillText(F(value, 0), 102 + Math.max(8, width), y + 17);
  });
}

function drawAgeProgress(canvas, percent, daysSinceBirthday, daysToBirthday) {
  const ctx = clearCanvas(canvas);
  const cx = 128, cy = 132, radius = 82;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * percent);
  ctx.lineTo(cx, cy);
  ctx.closePath();
  ctx.fillStyle = "#173f73";
  ctx.fill();
  ctx.beginPath();
  ctx.arc(cx, cy, radius, -Math.PI / 2 + Math.PI * 2 * percent, Math.PI * 1.5);
  ctx.lineTo(cx, cy);
  ctx.closePath();
  ctx.fillStyle = "#eef3f8";
  ctx.fill();
  ctx.fillStyle = "#152033";
  ctx.font = "800 28px system-ui, sans-serif";
  ctx.fillText(`${F(percent * 100, 1)}%`, 255, 105);
  ctx.font = "700 13px system-ui, sans-serif";
  ctx.fillStyle = "#344054";
  ctx.fillText("of current birthday year", 255, 130);
  ctx.font = "600 12px system-ui, sans-serif";
  ctx.fillStyle = "#667085";
  ctx.fillText(`${F(daysSinceBirthday, 0)} days since last birthday`, 255, 164);
  ctx.fillText(`${F(daysToBirthday, 0)} days to next birthday`, 255, 186);
}

function addYears(date, years) {
  const next = new Date(date);
  next.setFullYear(date.getFullYear() + years);
  return next;
}

function daysBetween(a, b) {
  return Math.round((b - a) / 86400000);
}

function renderAge(birth, target, years, totalDays) {
  const summary = document.getElementById("ageSummary");
  const bars = document.getElementById("ageBars");
  const progress = document.getElementById("ageProgress");
  const table = document.querySelector("#ageMilestones tbody");
  if (!summary || !bars || !progress || !table) return;
  const months = Math.floor(totalDays / 30.436875);
  const weeks = Math.floor(totalDays / 7);
  const hours = totalDays * 24;
  const minutes = hours * 60;
  const seconds = minutes * 60;
  summary.innerHTML = [
    ["Calendar age", `${years} years`, "Full years between birth date and target date."],
    ["Total days", F(totalDays, 0), "Useful for exact day-based comparisons."],
    ["Total months", F(months, 0), "Average calendar-month estimate."],
    ["Total seconds", F(seconds, 0), "Approximate total seconds lived."]
  ].map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
  drawAgeBars(bars, [years, months, weeks, totalDays]);
  let lastBirthday = addYears(birth, years);
  if (lastBirthday > target) lastBirthday = addYears(birth, years - 1);
  let nextBirthday = addYears(birth, years + 1);
  if (nextBirthday <= target) nextBirthday = addYears(birth, years + 2);
  const since = Math.max(0, daysBetween(lastBirthday, target));
  const span = Math.max(1, daysBetween(lastBirthday, nextBirthday));
  const toNext = Math.max(0, daysBetween(target, nextBirthday));
  drawAgeProgress(progress, Math.min(1, since / span), since, toNext);
  const milestones = [1, 5, 10, 13, 16, 18, 21, 25, 30, 40, 50, 60, 65, 70, 75, 80, 90, 100];
  table.innerHTML = milestones.map(age => {
    const date = addYears(birth, age);
    const diff = daysBetween(target, date);
    const timing = diff === 0 ? "Today" : diff > 0 ? `${F(diff, 0)} days later` : `${F(Math.abs(diff), 0)} days ago`;
    return `<tr><td>Age ${age}</td><td>${date.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</td><td>${timing}</td></tr>`;
  }).join("");
}
// End age dashboard rendering
