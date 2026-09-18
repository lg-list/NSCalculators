const $=s=>document.querySelector(s), V=id=>parseFloat(document.getElementById(id)?.value||0);
const F=(n,d=2)=>Number.isFinite(n)?n.toLocaleString('en-US',{maximumFractionDigits:d}):'n/a';
const USD=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2}).format(Number.isFinite(n)?n:0);
const MONEY=(n,currency='USD')=>new Intl.NumberFormat('en-US',{style:'currency',currency,maximumFractionDigits:2}).format(Number.isFinite(n)?n:0);
function show(html){const r=$('#result');if(r)r.innerHTML=html}
function unitValue(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function annualCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function monthlyCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100/12:V(id)/12}
function monthDate(id){const raw=document.getElementById(id)?.value||'';return /^\d{4}-\d{2}$/.test(raw)?new Date(`${raw}-01T00:00:00`):new Date(raw||Date.now())}
function syncMortgageCosts(){const box=document.getElementById('include_costs'),panel=document.getElementById('mortgageCostFields');if(!box||!panel)return true;const on=box.checked;panel.hidden=!on;panel.classList.toggle('is-hidden',!on);panel.style.display=on?'':'none';return on}
function compoundProjection(){
  const principal=Math.max(0,V('principal')), annual=V('rate')/100, years=Math.max(0,Math.floor(V('years'))), frequency=Math.max(1,V('compound_frequency')||12), monthly=Math.max(0,V('monthly'));
  const timing=document.getElementById('contribution_timing')?.value||'end', months=years*12;
  const monthlyRate=Math.pow(1+annual/frequency,frequency/12)-1;
  let balance=principal,totalInterest=0,totalDeposits=0,yearInterest=0,yearDeposits=0;const schedule=[];
  for(let month=1;month<=months;month++){
    if(timing==='beginning'){balance+=monthly;totalDeposits+=monthly;yearDeposits+=monthly}
    const interest=balance*monthlyRate;balance+=interest;totalInterest+=interest;yearInterest+=interest;
    if(timing!=='beginning'){balance+=monthly;totalDeposits+=monthly;yearDeposits+=monthly}
    if(month%12===0)schedule.push({year:month/12,deposits:yearDeposits,interest:yearInterest,balance});
    if(month%12===0){yearInterest=0;yearDeposits=0}
  }
  return {principal,annual,years,frequency,monthly,timing,balance,totalInterest,totalDeposits,schedule,effectiveAnnual:Math.pow(1+annual/frequency,frequency)-1};
}
function salaryProjection(){const current=Math.max(0,V('salary')),unit=document.getElementById('raise_unit')?.value||'percent',entered=V('raise_amount'),raiseDollars=unit==='dollar'?entered:current*entered/100,raisePercent=current?raiseDollars/current*100:0,annual=Math.max(0,current+raiseDollars),periods=Math.max(1,Math.floor(V('pay_periods'))),hours=Math.max(.1,V('hours_week')),weeks=Math.max(.1,V('weeks_year')),inflation=Math.max(-99,V('inflation_rate')),realRaise=((1+raisePercent/100)/(1+inflation/100)-1)*100;return{current,unit,entered,raiseDollars,raisePercent,annual,periods,hours,weeks,inflation,realRaise,monthly:annual/12,perPeriod:annual/periods,weekly:annual/weeks,hourly:annual/(hours*weeks),oldMonthly:current/12,oldPerPeriod:current/periods,oldWeekly:current/weeks,oldHourly:current/(hours*weeks)}}
function discountProjection(){const price=Math.max(0,V('price')),first=Math.max(0,Math.min(100,V('discount'))),second=Math.max(0,Math.min(100,V('discount_two'))),quantity=Math.max(1,Math.floor(V('quantity'))),taxRate=Math.max(0,V('sales_tax')),fees=Math.max(0,V('checkout_fees')),multiplier=(1-first/100)*(1-second/100),unitPrice=price*multiplier,effective=(1-multiplier)*100,subtotal=unitPrice*quantity,savings=(price-unitPrice)*quantity,tax=subtotal*taxRate/100,total=subtotal+tax+fees;return{price,first,second,quantity,taxRate,fees,multiplier,unitPrice,effective,subtotal,savings,tax,total}}
const FEDERAL_2026={single:[[12400,.10],[50400,.12],[105700,.22],[201775,.24],[256225,.32],[640600,.35],[Infinity,.37]],joint:[[24800,.10],[100800,.12],[211400,.22],[403550,.24],[512450,.32],[768700,.35],[Infinity,.37]],head:[[17700,.10],[67450,.12],[105700,.22],[201750,.24],[256200,.32],[640600,.35],[Infinity,.37]]};
const STANDARD_DEDUCTION_2026={single:16100,joint:32200,head:24150};
function progressiveTax(income,brackets){let tax=0,lower=0;for(const[upper,rate]of brackets){const amount=Math.max(0,Math.min(income,upper)-lower);tax+=amount*rate;if(income<=upper)break;lower=upper}return tax}
function marginalRate(income,brackets){return(brackets.find(([upper])=>income<=upper)||brackets.at(-1))[1]}
function syncPayDeductionFields(){const custom=document.getElementById('pay_deduction_mode')?.value==='custom';document.querySelectorAll('[data-pay-custom]').forEach(el=>el.classList.toggle('is-hidden',!custom));return custom}
function takeHomeProjection(){const gross=Math.max(0,V('pay_gross')),status=document.getElementById('pay_status')?.value||'single',periods=Math.max(1,Math.floor(V('pay_periods'))),retirement=Math.max(0,V('pay_retirement')),pretax=Math.max(0,V('pay_pretax')),posttax=Math.max(0,V('pay_posttax')),stateRate=Math.max(0,V('pay_state_rate')),extraPerPay=Math.max(0,V('pay_extra')),custom=syncPayDeductionFields(),deduction=custom?Math.max(0,V('pay_custom_deduction')):STANDARD_DEDUCTION_2026[status],federalTaxable=Math.max(0,gross-retirement-pretax-deduction),brackets=FEDERAL_2026[status],federal=progressiveTax(federalTaxable,brackets),marginal=marginalRate(federalTaxable,brackets),ficaWages=Math.max(0,gross-pretax),social=Math.min(ficaWages,184500)*.062,medicareThreshold=status==='joint'?250000:200000,medicare=ficaWages*.0145+Math.max(0,ficaWages-medicareThreshold)*.009,stateTaxable=Math.max(0,gross-retirement-pretax),state=stateTaxable*stateRate/100,extra=extraPerPay*periods,totalTax=federal+social+medicare+state+extra,totalDeductions=retirement+pretax+posttax,net=Math.max(0,gross-totalTax-totalDeductions),effective=gross?totalTax/gross*100:0;return{gross,status,periods,retirement,pretax,posttax,stateRate,extraPerPay,extra,deduction,custom,federalTaxable,federal,marginal,ficaWages,social,medicareThreshold,medicare,stateTaxable,state,totalTax,totalDeductions,net,effective,perPay:net/periods,grossPerPay:gross/periods,monthly:net/12}}
function tradeInProjection(){const comparable=Math.max(0,V('comparable')),adjustment=V('market_adjustment'),margin=Math.max(0,V('dealer_margin')),reconditioning=Math.max(0,V('reconditioning')),payoff=Math.max(0,V('payoff')),replacement=Math.max(0,V('replacement_price')),taxRate=Math.max(0,V('tax_rate'))/100,trade=Math.max(0,comparable+adjustment-margin-reconditioning),equity=trade-payoff,taxSavings=Math.min(trade,replacement)*taxRate;return{comparable,adjustment,margin,reconditioning,payoff,replacement,taxRate,trade,equity,taxSavings,effective:trade+taxSavings}}
function usedCarProjection(){const benchmark=Math.max(0,V('retail_benchmark')),condition=V('condition_adjustment'),mileage=V('mileage_adjustment'),options=V('options_adjustment'),regional=V('regional_adjustment'),spread=Math.max(0,Math.min(50,V('dealer_spread'))),retail=Math.max(0,benchmark*(1+condition/100)*(1+regional/100)+mileage+options),privateValue=retail*(1-spread/200),trade=retail*(1-spread/100);return{benchmark,condition,mileage,options,regional,spread,retail,privateValue,trade}}
function tireSpec(width,aspect,rim){const sidewall=width*aspect/100,diameter=rim+2*sidewall/25.4,circumference=Math.PI*diameter,revsPerMile=63360/circumference;return{width,aspect,rim,sidewall,diameter,circumference,revsPerMile}}
function tireComparison(){const original=tireSpec(Math.max(0,V('original_width')),Math.max(0,V('original_aspect')),Math.max(0,V('original_rim'))),next=tireSpec(Math.max(0,V('new_width')),Math.max(0,V('new_aspect')),Math.max(0,V('new_rim'))),ratio=original.diameter?next.diameter/original.diameter:0,differencePct=(ratio-1)*100,indicated=Math.max(0,V('indicated_speed')),actualSpeed=indicated*ratio,clearance=(next.diameter-original.diameter)/2;return{original,next,ratio,differencePct,indicated,actualSpeed,clearance}}
function wheelOffsetComparison(){const currentWidth=Math.max(0,V('current_width')),currentOffset=V('current_offset'),newWidth=Math.max(0,V('new_wheel_width')),newOffset=V('new_offset'),spacer=Math.max(0,V('spacer')),effectiveOffset=newOffset-spacer,currentHalf=currentWidth*25.4/2,newHalf=newWidth*25.4/2,currentInner=currentHalf+currentOffset,currentOuter=currentHalf-currentOffset,newInner=newHalf+effectiveOffset,newOuter=newHalf-effectiveOffset,innerClearance=currentInner-newInner,outerPoke=newOuter-currentOuter,trackChange=outerPoke*2,currentBackspacing=(currentWidth+1)/2+currentOffset/25.4,newBackspacing=(newWidth+1)/2+effectiveOffset/25.4;return{currentWidth,currentOffset,newWidth,newOffset,spacer,effectiveOffset,currentInner,currentOuter,newInner,newOuter,innerClearance,outerPoke,trackChange,currentBackspacing,newBackspacing}}
function syncConcreteFields(){const round=(document.getElementById('concrete_shape')?.value||'slab')!=='slab';document.querySelectorAll('[data-concrete-rect]').forEach(el=>el.classList.toggle('is-hidden',round));document.querySelectorAll('[data-concrete-round]').forEach(el=>el.classList.toggle('is-hidden',!round));return round}
function concreteProjection(){const shape=document.getElementById('concrete_shape')?.value||'slab',round=syncConcreteFields();let baseFt3=0,quantity=1;if(round){const radius=Math.max(0,V('concrete_diameter'))/24,height=Math.max(0,V('concrete_height'));quantity=Math.max(1,Math.floor(V('concrete_qty')));baseFt3=Math.PI*radius*radius*height*quantity}else baseFt3=Math.max(0,V('concrete_length'))*Math.max(0,V('concrete_width'))*Math.max(0,V('concrete_thickness'))/12;const waste=Math.max(0,V('concrete_waste')),withWaste=baseFt3*(1+waste/100),yards=withWaste/27,yieldPerBag=Math.max(.001,V('concrete_bag_size')),bags=Math.ceil(withWaste/yieldPerBag),bagCost=bags*Math.max(0,V('concrete_bag_price')),readyCost=yards*Math.max(0,V('concrete_yard_price'));return{shape,quantity,baseFt3,waste,withWaste,yards,yieldPerBag,bags,bagCost,readyCost}}
function syncRoofFields(){const mode=document.getElementById('roof_input_mode')?.value||'pitch';document.querySelectorAll('[data-roof-pitch]').forEach(el=>el.classList.toggle('is-hidden',mode!=='pitch'));document.querySelectorAll('[data-roof-rise-run]').forEach(el=>el.classList.toggle('is-hidden',mode!=='rise_run'));document.querySelectorAll('[data-roof-angle]').forEach(el=>el.classList.toggle('is-hidden',mode!=='angle'));return mode}
function roofPitchProjection(){const mode=syncRoofFields();let slope=0;if(mode==='rise_run')slope=Math.max(0,V('roof_rise'))/Math.max(.0001,V('roof_run'));else if(mode==='angle')slope=Math.tan(Math.max(0,Math.min(89.9,V('roof_angle')))*Math.PI/180);else slope=Math.max(0,V('roof_pitch'))/12;const pitch=slope*12,angle=Math.atan(slope)*180/Math.PI,percent=slope*100,factor=Math.sqrt(1+slope*slope),run=Math.max(0,V('roof_rafter_run')),overhang=Math.max(0,V('roof_overhang'))/12,rafter=(run+overhang)*factor,rise=run*slope,planArea=Math.max(0,V('roof_plan_area')),slopedArea=planArea*factor,squares=slopedArea/100;return{mode,slope,pitch,angle,percent,factor,run,overhang,rafter,rise,planArea,slopedArea,squares}}
function rafterProjection(){const pitch=Math.max(0,V('rafter_pitch')),slope=pitch/12,factor=Math.sqrt(1+slope*slope),run=Math.max(0,V('rafter_run')),overhang=Math.max(0,V('rafter_overhang'))/12,baseLength=run*factor,tailLength=overhang*factor,totalLength=baseLength+tailLength,rise=run*slope,angle=Math.atan(slope)*180/Math.PI,quantity=Math.max(1,Math.floor(V('rafter_qty'))),totalLinear=totalLength*quantity;return{pitch,slope,factor,run,overhang,baseLength,tailLength,totalLength,rise,angle,quantity,totalLinear}}
function syncAreaFields(){const shape=document.getElementById('area_shape')?.value||'rectangle';document.querySelectorAll('[data-area-rectangle],[data-area-circle],[data-area-triangle],[data-area-walls]').forEach(el=>{const show=(shape==='rectangle'&&el.hasAttribute('data-area-rectangle'))||(shape==='circle'&&el.hasAttribute('data-area-circle'))||(shape==='triangle'&&el.hasAttribute('data-area-triangle'))||(shape==='room_walls'&&el.hasAttribute('data-area-walls'));el.classList.toggle('is-hidden',!show)});return shape}
function squareFootageProjection(){const shape=syncAreaFields(),length=Math.max(0,V('area_length')),width=Math.max(0,V('area_width'));let area=0,perimeter=null,gross=0,openings=0;if(shape==='circle'){const diameter=Math.max(0,V('area_diameter'));area=Math.PI*(diameter/2)**2;perimeter=Math.PI*diameter}else if(shape==='triangle'){area=Math.max(0,V('area_base'))*Math.max(0,V('area_height'))/2}else if(shape==='room_walls'){perimeter=2*(length+width);gross=perimeter*Math.max(0,V('wall_height'));openings=Math.max(0,V('area_openings'));area=Math.max(0,gross-openings)}else{area=length*width;perimeter=2*(length+width)}const overage=Math.max(0,V('area_overage')),orderArea=area*(1+overage/100),price=Math.max(0,V('area_price')),cost=orderArea*price;return{shape,length,width,area,perimeter,gross,openings,overage,orderArea,price,cost}}
function flooringProjection(){const length=Math.max(0,V('floor_length')),width=Math.max(0,V('floor_width')),extra=Math.max(0,V('floor_extra')),area=length*width+extra,waste=Math.max(0,V('floor_waste')),target=area*(1+waste/100),boxCoverage=Math.max(.001,V('floor_box_coverage')),boxes=Math.ceil(target/boxCoverage-1e-9),purchased=boxes*boxCoverage,leftover=Math.max(0,purchased-area),boxCost=boxes*Math.max(0,V('floor_box_price')),underlayCoverage=Math.max(.001,V('underlay_coverage')),underlayRolls=Math.ceil(area/underlayCoverage-1e-9),underlayCost=underlayRolls*Math.max(0,V('underlay_price')),totalCost=boxCost+underlayCost;return{length,width,extra,area,waste,target,boxCoverage,boxes,purchased,leftover,boxCost,underlayCoverage,underlayRolls,underlayCost,totalCost}}
function tileProjection(){const length=Math.max(0,V('tile_project_length')),width=Math.max(0,V('tile_project_width')),area=length*width,tileWidth=Math.max(.001,V('tile_width')),tileHeight=Math.max(.001,V('tile_height')),tileArea=tileWidth*tileHeight/144,waste=Math.max(0,V('tile_waste')),targetArea=area*(1+waste/100),pieces=Math.ceil(targetArea/tileArea-1e-9),perBox=Math.max(1,Math.floor(V('tile_per_box'))),boxes=Math.ceil(pieces/perBox-1e-9),purchasedPieces=boxes*perBox,purchasedArea=purchasedPieces*tileArea,leftover=Math.max(0,purchasedArea-area),cost=boxes*Math.max(0,V('tile_box_price'));return{length,width,area,tileWidth,tileHeight,tileArea,waste,targetArea,pieces,perBox,boxes,purchasedPieces,purchasedArea,leftover,cost}}
function deckProjection(){const length=Math.max(0,V('deck_length')),width=Math.max(0,V('deck_width')),boardWidth=Math.max(.001,V('deck_board_width')),gap=Math.max(0,V('deck_gap')),stockLength=Math.max(.001,V('deck_stock_length')),waste=Math.max(0,V('deck_waste')),joistSpacing=Math.max(.001,V('deck_joist_spacing')),boardPrice=Math.max(0,V('deck_board_price')),fastenersPerCrossing=Math.max(1,Math.floor(V('deck_fasteners_crossing'))),fastenersPerPack=Math.max(1,Math.floor(V('deck_fastener_pack'))),fastenerPackPrice=Math.max(0,V('deck_fastener_price')),area=length*width,rows=Math.ceil(width*12/(boardWidth+gap)-1e-9),boardsPerRow=Math.ceil(length/stockLength-1e-9),baseBoards=rows*boardsPerRow,boards=Math.ceil(baseBoards*(1+waste/100)-1e-9),coverageLinear=rows*length,stockLinear=baseBoards*stockLength,orderedLinear=boards*stockLength,joists=Math.ceil(length*12/joistSpacing-1e-9)+1,fasteners=rows*joists*fastenersPerCrossing,fastenerPacks=Math.ceil(fasteners/fastenersPerPack-1e-9),boardCost=boards*boardPrice,fastenerCost=fastenerPacks*fastenerPackPrice,totalCost=boardCost+fastenerCost;return{length,width,area,boardWidth,gap,stockLength,waste,rows,boardsPerRow,baseBoards,boards,coverageLinear,stockLinear,orderedLinear,joistSpacing,joists,fastenersPerCrossing,fasteners,fastenersPerPack,fastenerPacks,boardCost,fastenerCost,totalCost}}
function boardFootProjection(){const thickness=Math.max(0,V('bf_thickness')),width=Math.max(0,V('bf_width')),length=Math.max(0,V('bf_length')),quantity=Math.max(1,Math.floor(V('bf_quantity'))),waste=Math.max(0,V('bf_waste')),price=Math.max(0,V('bf_price')),perBoard=thickness*width*length/12,total=perBoard*quantity,order=total*(1+waste/100),cubicFeet=order/12,linearFeet=length*quantity,cost=order*price;return{thickness,width,length,quantity,waste,price,perBoard,total,order,cubicFeet,linearFeet,cost}}
const ELECTRICAL_WIRE_TABLE=[
 {g:'14',cuR:3.07,alR:5.06,cu60:15,cu75:15,al60:0,al75:0},{g:'12',cuR:1.93,alR:3.20,cu60:20,cu75:20,al60:0,al75:0},{g:'10',cuR:1.21,alR:2.00,cu60:30,cu75:30,al60:0,al75:0},{g:'8',cuR:.764,alR:1.26,cu60:40,cu75:50,al60:30,al75:40},{g:'6',cuR:.491,alR:.808,cu60:55,cu75:65,al60:40,al75:50},{g:'4',cuR:.308,alR:.508,cu60:70,cu75:85,al60:55,al75:65},{g:'3',cuR:.245,alR:.404,cu60:85,cu75:100,al60:65,al75:75},{g:'2',cuR:.194,alR:.319,cu60:95,cu75:115,al60:75,al75:90},{g:'1',cuR:.154,alR:.253,cu60:110,cu75:130,al60:85,al75:100},{g:'1/0',cuR:.122,alR:.201,cu60:125,cu75:150,al60:100,al75:120},{g:'2/0',cuR:.0967,alR:.159,cu60:145,cu75:175,al60:115,al75:135},{g:'3/0',cuR:.0766,alR:.126,cu60:165,cu75:200,al60:130,al75:155},{g:'4/0',cuR:.0608,alR:.100,cu60:195,cu75:230,al60:150,al75:180}
];
const STANDARD_BREAKERS=[15,20,25,30,35,40,45,50,60,70,80,90,100,110,125,150,175,200,225,250,300,350,400];
function nextBreaker(amps){return STANDARD_BREAKERS.find(x=>x+1e-9>=amps)||Math.ceil(amps/50)*50}
function phaseFactor(phase){return phase==='three'?Math.sqrt(3):2}
function wireResistance(row,material){return material==='aluminum'?row.alR:row.cuR}
function voltageDropFor(row,material,phase,length,amps){return phaseFactor(phase)*length*amps*wireResistance(row,material)/1000}
function voltageDropProjection(){const phase=document.getElementById('vd_phase')?.value||'single',material=document.getElementById('vd_material')?.value||'copper',gauge=document.getElementById('vd_gauge')?.value||'12',length=Math.max(0,V('vd_length')),amps=Math.max(0,V('vd_amps')),voltage=Math.max(.001,V('vd_voltage')),limit=Math.max(.1,V('vd_limit')),row=ELECTRICAL_WIRE_TABLE.find(x=>x.g===gauge)||ELECTRICAL_WIRE_TABLE[1],drop=voltageDropFor(row,material,phase,length,amps),percent=drop/voltage*100,loadVoltage=Math.max(0,voltage-drop),targetVolts=voltage*limit/100,recommended=ELECTRICAL_WIRE_TABLE.find(x=>voltageDropFor(x,material,phase,length,amps)<=targetVolts+1e-9)||ELECTRICAL_WIRE_TABLE.at(-1),maxLength=amps>0?targetVolts*1000/(phaseFactor(phase)*amps*wireResistance(row,material)):0;return{phase,material,gauge,length,amps,voltage,limit,row,drop,percent,loadVoltage,recommended,maxLength}}
function wireSizeProjection(){const amps=Math.max(0,V('ws_amps')),continuous=Math.min(amps,Math.max(0,V('ws_continuous'))),designAmps=amps+continuous*.25,material=document.getElementById('ws_material')?.value||'copper',temp=document.getElementById('ws_temp')?.value||'60',phase=document.getElementById('ws_phase')?.value||'single',voltage=Math.max(.001,V('ws_voltage')),length=Math.max(0,V('ws_length')),limit=Math.max(.1,V('ws_drop_limit')),ampKey=(material==='aluminum'?'al':'cu')+temp,ampacityRow=ELECTRICAL_WIRE_TABLE.find(x=>x[ampKey]>=designAmps&&x[ampKey]>0)||ELECTRICAL_WIRE_TABLE.at(-1),targetVolts=voltage*limit/100,dropRow=ELECTRICAL_WIRE_TABLE.find(x=>voltageDropFor(x,material,phase,length,amps)<=targetVolts+1e-9)||ELECTRICAL_WIRE_TABLE.at(-1),ampIndex=ELECTRICAL_WIRE_TABLE.indexOf(ampacityRow),dropIndex=ELECTRICAL_WIRE_TABLE.indexOf(dropRow),recommended=ELECTRICAL_WIRE_TABLE[Math.max(ampIndex,dropIndex)],ampacity=recommended[ampKey],drop=voltageDropFor(recommended,material,phase,length,amps),dropPercent=drop/voltage*100,loadVoltage=Math.max(0,voltage-drop);return{amps,continuous,designAmps,material,temp,phase,voltage,length,limit,ampacityRow,dropRow,recommended,ampacity,drop,dropPercent,loadVoltage}}
function breakerProjection(){const continuous=Math.max(0,V('br_continuous')),noncontinuous=Math.max(0,V('br_noncontinuous')),actual=continuous+noncontinuous,planning=continuous*1.25+noncontinuous,breaker=nextBreaker(planning),voltage=Math.max(0,V('br_voltage')),poles=Math.max(1,V('br_poles')),utilization=breaker>0?actual/breaker*100:0,headroom=Math.max(0,breaker-planning),power=actual*voltage;return{continuous,noncontinuous,actual,planning,breaker,voltage,poles,utilization,headroom,power}}
function electricalLoadProjection(){const continuous=Math.max(0,V('el_continuous')),noncontinuous=Math.max(0,V('el_noncontinuous')),watts=continuous+noncontinuous,planningWatts=continuous*1.25+noncontinuous,voltage=Math.max(.001,V('el_voltage')),phase=document.getElementById('el_phase')?.value||'single',pf=phase==='dc'?1:Math.max(.01,Math.min(1,V('el_pf'))),divisor=voltage*pf*(phase==='three'?Math.sqrt(3):1),amps=watts/divisor,planningAmps=planningWatts/divisor,va=watts/pf,breaker=nextBreaker(planningAmps),utilization=breaker>0?amps/breaker*100:0;return{continuous,noncontinuous,watts,planningWatts,voltage,phase,pf,amps,planningAmps,va,breaker,utilization}}
function wattsAmpsProjection(){const watts=Math.max(0,V('wa_watts')),voltage=Math.max(.001,V('wa_voltage')),phase=document.getElementById('wa_phase')?.value||'single',pf=phase==='dc'?1:Math.max(.01,Math.min(1,V('wa_pf'))),multiplier=phase==='three'?Math.sqrt(3):1,amps=watts/(voltage*pf*multiplier),va=watts/pf,vars=Math.sqrt(Math.max(0,va*va-watts*watts)),continuous=document.getElementById('wa_continuous')?.value==='yes',planningAmps=amps*(continuous?1.25:1);return{watts,voltage,phase,pf,multiplier,amps,va,vars,continuous,planningAmps}}
function ampsWattsProjection(){const amps=Math.max(0,V('aw_amps')),voltage=Math.max(.001,V('aw_voltage')),phase=document.getElementById('aw_phase')?.value||'single',pf=phase==='dc'?1:Math.max(.01,Math.min(1,V('aw_pf'))),multiplier=phase==='three'?Math.sqrt(3):1,va=amps*voltage*multiplier,watts=va*pf,vars=Math.sqrt(Math.max(0,va*va-watts*watts));return{amps,voltage,phase,pf,multiplier,va,watts,vars}}
function syncFeetMeterInputs(){const reverse=document.getElementById('conversion_direction')?.value==='meters_to_feet';document.querySelectorAll('[data-feet-input]').forEach(el=>el.classList.toggle('is-hidden',reverse));document.querySelectorAll('[data-meter-input]').forEach(el=>el.classList.toggle('is-hidden',!reverse));return reverse}
function clearCalcForm(){const form=document.querySelector('.calc');if(!form)return;form.querySelectorAll('input').forEach(input=>{if(input.type==='checkbox')input.checked=false;else input.value=''});form.querySelectorAll('select').forEach(select=>{select.selectedIndex=0});form.querySelectorAll('details').forEach(item=>{item.open=false});syncMortgageCosts();syncConcreteFields();syncRoofFields();syncAreaFields();syncPayDeductionFields();show('<strong>0</strong><br>Enter values to calculate a new result.');const engine=currentEngine();if(engine==='cn_mortgage')renderMortgage(0,0,1,0,0,0,0,0,0,0,0,0,0,new Date());if(engine==='loan_page')renderLoanPage()}
function calc(e){
 switch(e){
  case'trade_value':{let price=V('price'),age=V('age'),miles=V('miles'),cond=V('condition');let ageF=Math.pow(.84,age),expected=Math.max(1,age)*12000,mileageF=Math.max(.72,Math.min(1.12,1-(miles-expected)*0.000003));let r=price*ageF*mileageF*cond;show(`<strong>${USD(Math.max(0,r))}</strong><br>Illustrative estimate, not a dealer quote or appraisal.`);break}
  case'f150_bed':{let bed=String(document.getElementById('bed').value);let d={'5.5':['67.1 in','50.6 in','~52.8 cu ft'],'6.5':['78.9 in','50.6 in','~62.3 cu ft'],'8':['97.6 in','50.6 in','~77.4 cu ft']}[bed];show(`<strong>${bed} ft bed</strong><br>Approx. inside length: ${d[0]}; width between wheelhouses: ${d[1]}; cargo volume: ${d[2]}. Verify exact model year/configuration.`);break}
  case'depreciation':{let r=V('price')*Math.pow(1-V('rate')/100,V('years'));show(`<strong>${USD(r)}</strong><br>Estimated future value.`);break}
  case'payload':{let capacity=V('gvwr')-V('curb'),used=V('people')+V('cargo')+V('tongue'),remaining=capacity-used,status=remaining>=0?'Within entered GVWR':'Over entered GVWR';show(`<strong>${F(remaining,0)} lb remaining</strong><br>${status}; ${F(capacity,0)} lb total payload capacity and ${F(used,0)} lb entered load.`);break}
  case'trailer_weight':{let r=V('empty')+V('cargo');show(`<strong>${F(r,0)} lb</strong><br>Estimated loaded trailer weight.`);break}
  case'tongue_weight':{let r=V('trailer')*V('percent')/100;show(`<strong>${F(r,0)} lb</strong><br>Estimated tongue weight.`);break}
  case'trailer_payload':{let r=V('gvwr')-V('empty');show(`<strong>${F(r,0)} lb</strong><br>Theoretical payload before other limits.`);break}
  case'tongue_pct':{let r=V('trailer')?V('tongue')/V('trailer')*100:0;show(`<strong>${F(r,2)}%</strong>`);break}
  case'towing':{let loaded=V('curb')+V('people')+V('cargo'),remainingPayload=Math.max(0,V('gvwr')-loaded),pct=Math.max(.01,V('tongue_pct')/100),limits=[['Vehicle tow rating',V('rating')],['GCWR headroom',Math.max(0,V('gcwr')-loaded)],['Hitch rating',V('hitch_rating')],['Payload for tongue weight',remainingPayload/pct]],hit=limits.reduce((a,b)=>b[1]<a[1]?b:a);show(`<strong>${F(hit[1],0)} lb trailer</strong><br>Planning limit: ${hit[0]}; ${F(remainingPayload,0)} lb vehicle payload remains before tongue weight.`);break}
  case'fuel_cost':{let r=V('distance')/Math.max(.01,V('mpg'))*V('fuelprice');show(`<strong>${USD(r)}</strong><br>Estimated fuel cost.`);break}
  case'mpg':{let r=V('gallons')?V('miles')/V('gallons'):0;show(`<strong>${F(r,2)} MPG</strong>`);break}
  case'mpg_advanced':{let distance=V('distance'),fuel=V('fuel_used'),miles=(document.getElementById('distance_unit')?.value==='kilometers'?distance*0.621371192237:distance),liters=fuel*(document.getElementById('fuel_unit')?.value==='us_gallon'?3.785411784:document.getElementById('fuel_unit')?.value==='imperial_gallon'?4.54609:1),usGallons=liters/3.785411784,mpg=usGallons>0?miles/usGallons:0,km=miles/0.621371192237,l100=km>0?liters/km*100:0;show(`<strong>${F(mpg,2)} US MPG</strong><br>${F(l100,2)} L/100 km; ${F(miles/(liters/4.54609),2)} Imperial MPG; ${F(liters?km/liters:0,2)} km/L.`);break}
  case'fuel_cost_advanced':{let metric=document.getElementById('trip_units')?.value==='metric',distance=V('distance')*Math.max(1,V('trip_type'))*Math.max(1,V('trips')),eff=Math.max(.01,V('efficiency')),fuel=metric?distance*eff/100:distance/eff,cost=fuel*V('fuelprice'),currency=document.getElementById('currency')?.value||'USD',people=Math.max(1,V('people'));show(`<strong>${MONEY(cost,currency)}</strong><br>${F(fuel,2)} ${metric?'liters':'US gallons'}; ${MONEY(cost/people,currency)} per person; ${F(distance,0)} ${metric?'km':'miles'} total.`);break}
  case'trade_in_estimate':{const p=tradeInProjection(),equityLabel=p.equity>=0?'positive equity':'negative equity';show(`<strong>${USD(p.trade)} trade-in estimate</strong><br>${USD(Math.abs(p.equity))} ${equityLabel}; ${USD(p.taxSavings)} entered tax benefit; ${USD(p.effective)} effective trade value.`);break}
  case'used_car_estimate':{const p=usedCarProjection();show(`<strong>${USD(p.privateValue)} private-party estimate</strong><br>Adjusted retail: ${USD(p.retail)}; trade-in estimate: ${USD(p.trade)}; review the planning ranges below.`);break}
  case'tire_compare':{const p=tireComparison(),direction=p.differencePct>=0?'larger':'smaller';show(`<strong>${F(Math.abs(p.differencePct),2)}% ${direction} diameter</strong><br>Actual speed at ${F(p.indicated,0)} mph indicated: ${F(p.actualSpeed,2)} mph; ground-clearance change: ${p.clearance>=0?'+':''}${F(p.clearance,2)} in.`);break}
  case'wheel_offset_compare':{const p=wheelOffsetComparison(),clearance=p.innerClearance>=0?`${F(p.innerClearance,1)} mm more`:`${F(Math.abs(p.innerClearance),1)} mm less`;show(`<strong>${p.outerPoke>=0?'+':''}${F(p.outerPoke,1)} mm outer position</strong><br>${clearance} inner clearance; ${p.trackChange>=0?'+':''}${F(p.trackChange,1)} mm estimated track change.`);break}
  case'concrete_advanced':{const p=concreteProjection();show(`<strong>${F(p.yards,2)} cubic yards</strong><br>${F(p.withWaste,2)} cubic feet with waste; ${F(p.bags,0)} selected bags; estimated bag cost ${USD(p.bagCost)}.`);break}
  case'roof_pitch_advanced':{const p=roofPitchProjection();show(`<strong>${F(p.pitch,2)}:12 roof pitch</strong><br>${F(p.angle,2)}° angle; ${F(p.percent,1)}% slope; ${F(p.rafter,2)} ft estimated rafter length.`);break}
  case'rafter_advanced':{const p=rafterProjection();show(`<strong>${F(p.totalLength,2)} ft per rafter</strong><br>${F(p.baseLength,2)} ft to wall line plus ${F(p.tailLength,2)} ft sloped tail; ${F(p.totalLinear,1)} total linear feet.`);break}
  case'square_footage_advanced':{const p=squareFootageProjection();show(`<strong>${F(p.area,2)} square feet</strong><br>${F(p.orderArea,2)} sq ft with overage; estimated material cost ${USD(p.cost)}${p.perimeter!==null?`; ${F(p.perimeter,1)} ft perimeter`:''}.`);break}
	  case'flooring_advanced':{const p=flooringProjection();show(`<strong>${F(p.boxes,0)} boxes of flooring</strong><br>${F(p.target,1)} sq ft target; ${F(p.purchased,1)} sq ft purchased; estimated total with underlayment ${USD(p.totalCost)}.`);break}
	  case'tile_advanced':{const p=tileProjection();show(`<strong>${F(p.boxes,0)} boxes / ${F(p.pieces,0)} tiles</strong><br>${F(p.targetArea,1)} sq ft target; ${F(p.purchasedArea,1)} sq ft purchased; estimated tile cost ${USD(p.cost)}.`);break}
	  case'deck_advanced':{const p=deckProjection();show(`<strong>${F(p.boards,0)} full deck boards</strong><br>${F(p.rows,0)} rows; ${F(p.joists,0)} joist lines; ${F(p.fasteners,0)} fasteners; estimated materials ${USD(p.totalCost)}.`);break}
	  case'board_foot_advanced':{const p=boardFootProjection();show(`<strong>${F(p.order,2)} board feet to order</strong><br>${F(p.total,2)} board feet before waste; ${F(p.cubicFeet,2)} cubic feet; estimated lumber cost ${USD(p.cost)}.`);break}
	  case'voltage_drop_advanced':{const p=voltageDropProjection();show(`<strong>${F(p.drop,2)} V drop (${F(p.percent,2)}%)</strong><br>${F(p.loadVoltage,2)} V at load; ${p.recommended.g} AWG meets the entered ${F(p.limit,1)}% resistive-drop target.`);break}
	  case'wire_size_advanced':{const p=wireSizeProjection();show(`<strong>${p.recommended.g} AWG ${p.material}</strong><br>${F(p.ampacity,0)} A reference ampacity; ${F(p.dropPercent,2)}% estimated drop; ${F(p.designAmps,2)} A planning current.`);break}
	  case'breaker_advanced':{const p=breakerProjection();show(`<strong>${F(p.breaker,0)} A reference breaker</strong><br>${F(p.planning,2)} A minimum planning current; ${F(p.actual,2)} A connected load; verify conductor and equipment rules.`);break}
	  case'electrical_load_advanced':{const p=electricalLoadProjection();show(`<strong>${F(p.amps,2)} A actual load</strong><br>${F(p.planningAmps,2)} A continuous-load planning current; ${F(p.breaker,0)} A reference breaker; ${F(p.va,0)} VA.`);break}
	  case'watts_amps_advanced':{const p=wattsAmpsProjection();show(`<strong>${F(p.amps,3)} amps</strong><br>${F(p.watts/1000,3)} kW real power; ${F(p.va,1)} VA apparent power; ${F(p.planningAmps,3)} A ${p.continuous?'continuous-load planning':'conversion'} current.`);break}
	  case'amps_watts_advanced':{const p=ampsWattsProjection();show(`<strong>${F(p.watts,1)} watts</strong><br>${F(p.watts/1000,3)} kW real power; ${F(p.va,1)} VA apparent power; ${F(p.vars,1)} VAR reactive power.`);break}
  case'tire':{let width=V('width'),aspect=V('aspect'),wheel=V('wheel');let side=width*aspect/100,diam=wheel+2*side/25.4,circ=Math.PI*diam;show(`<strong>${F(diam,2)} in diameter</strong><br>Sidewall: ${F(side,1)} mm; circumference: ${F(circ,2)} in.`);break}
  case'offset':{let r=(V('backspacing')-V('width')/2)*25.4;show(`<strong>${F(r,1)} mm offset</strong><br>Approximation using nominal wheel width.`);break}
  case'backspacing':{let r=V('width')/2+V('offset')/25.4;show(`<strong>${F(r,2)} in backspacing</strong><br>Approximation using nominal wheel width.`);break}
  case'bolt_pattern':{let r=V('adjacent')/Math.sin(Math.PI/V('lugs'));show(`<strong>${F(r,3)} in bolt-circle diameter</strong>`);break}
  case'horsepower':{let r=V('torque')*V('rpm')/5252;show(`<strong>${F(r,1)} hp</strong>`);break}
  case'power_weight':{let a=V('hp')/V('weight'),b=V('weight')/V('hp');show(`<strong>${F(a,4)} hp/lb</strong><br>${F(b,2)} lb per hp.`);break}
  case'car_loan':{let price=V('price'),tax=price*V('tax')/100,fees=V('fees'),include=(document.getElementById('include_fees')?.value||'0')==='1';let base=Math.max(0,price-V('incentives')-V('down')-V('trade')+V('owed')),P=Math.max(0,base+(include?tax+fees:0));let rr=V('apr')/1200,n=Math.max(1,V('months'));let pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n,upfront=V('down')+(include?0:tax+fees);show(`<strong>${USD(pay)} / month</strong><br>Total loan amount: ${USD(P)}; upfront payment: ${USD(upfront)}; sale tax: ${USD(tax)}.`);break}
  case'loan':{let P=V('amount'),rr=V('apr')/1200,n=Math.max(1,(V('years')*12)+(V('months_extra')||V('months')));let pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n,total=pay*n;show(`<strong>${USD(pay)} / month</strong><br>Total paid: ${USD(total)}; total interest: ${USD(total-P)}.`);break}
  case'loan_page':{renderLoanPage();break}
  case'compound':{const p=compoundProjection();show(`<strong>${USD(p.balance)}</strong><br>Total contributions: ${USD(p.principal+p.totalDeposits)}; estimated interest: ${USD(p.totalInterest)}.`);renderCompound(p);break}
  case'salary_advanced':{const p=salaryProjection();show(`<strong>${USD(p.annual)} new annual salary</strong><br>${USD(p.raiseDollars)} raise (${F(p.raisePercent,2)}%); ${USD(p.perPeriod)} per selected pay period; ${USD(p.hourly)} hourly equivalent.`);break}
  case'discount_advanced':{const p=discountProjection();show(`<strong>${USD(p.total)} estimated checkout total</strong><br>${USD(p.unitPrice)} discounted unit price; ${USD(p.savings)} total savings; ${F(p.effective,2)}% effective discount.`);break}
  case'take_home_pay':{const p=takeHomeProjection();show(`<strong>${USD(p.perPay)} take-home per paycheck</strong><br>${USD(p.net)} annual net pay; ${USD(p.monthly)} monthly average; ${F(p.effective,2)}% estimated total tax rate.`);break}
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
  case'feet_meters':{let reverse=syncFeetMeterInputs();if(reverse){let meters=V('meters'),totalFeet=meters/0.3048,feet=Math.floor(totalFeet),inches=(totalFeet-feet)*12;show(`<strong>${F(totalFeet,6)} feet</strong><br>${feet} ft ${F(inches,3)} in; ${F(meters,6)} meters.`)}else{let feet=V('feet'),inches=V('inches'),totalFeet=feet+inches/12,meters=totalFeet*0.3048;show(`<strong>${F(meters,6)} meters</strong><br>${F(totalFeet,6)} feet; ${F(totalFeet*12,3)} total inches.`)}break}
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

function drawCompoundLine(canvas, schedule) {
  if (!canvas || !schedule.length) return;
  const ctx=clearCanvas(canvas), pad={left:48,right:18,top:18,bottom:30}, width=canvas.width-pad.left-pad.right, height=canvas.height-pad.top-pad.bottom;
  const points=[Math.max(0,V('principal')),...schedule.map(row=>row.balance)], max=Math.max(...points,1);
  ctx.strokeStyle="#d8e4f1";ctx.lineWidth=1;
  for(let i=0;i<=4;i++){const y=pad.top+height*i/4;ctx.beginPath();ctx.moveTo(pad.left,y);ctx.lineTo(pad.left+width,y);ctx.stroke()}
  ctx.beginPath();points.forEach((value,index)=>{const x=pad.left+width*index/Math.max(1,points.length-1),y=pad.top+height*(1-value/max);if(index===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)});ctx.strokeStyle="#2563eb";ctx.lineWidth=3;ctx.stroke();
  ctx.fillStyle="#52647b";ctx.font="600 11px system-ui, sans-serif";ctx.textAlign="left";ctx.fillText("$0",5,pad.top+height);ctx.fillText(USD(max).replace('.00',''),5,pad.top+9);ctx.fillText("Start",pad.left,canvas.height-8);ctx.textAlign="right";ctx.fillText(`Year ${schedule.length}`,canvas.width-pad.right,canvas.height-8);
}

function renderCompound(projection) {
  const summary=document.getElementById('compoundSummary'), pie=document.getElementById('compoundPie'), line=document.getElementById('compoundLine'), table=document.querySelector('#compoundSchedule tbody');
  if(!summary||!pie||!line||!table)return;
  const contributed=projection.principal+projection.totalDeposits;
  summary.innerHTML=[["Ending balance",USD(projection.balance),"Projected account value."],["Total contributed",USD(contributed),"Initial amount plus deposits."],["Interest earned",USD(projection.totalInterest),"Estimated compound growth."],["Effective annual yield",`${F(projection.effectiveAnnual*100,3)}%`,"Based on selected frequency."]].map(item=>`<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join('');
  drawPie(pie,[projection.principal,projection.totalDeposits,projection.totalInterest],["Initial investment","Monthly deposits","Interest"]);
  drawCompoundLine(line,projection.schedule);
  table.innerHTML=projection.schedule.map(row=>`<tr><td>${row.year}</td><td>${USD(row.deposits)}</td><td>${USD(row.interest)}</td><td>${USD(row.balance)}</td></tr>`).join('');
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
  if (engine === "feet_meters") {
    const reverse=document.getElementById('conversion_direction')?.value==='meters_to_feet';
    const meters=reverse?V('meters'):(V('feet')+V('inches')/12)*0.3048, totalFeet=meters/0.3048, wholeFeet=Math.floor(totalFeet), inches=(totalFeet-wholeFeet)*12;
    cards=[["Meters",`${F(meters,6)} m`,"SI length."],["Decimal feet",`${F(totalFeet,6)} ft`,"Feet as a decimal."],["Feet and inches",`${wholeFeet} ft ${F(inches,3)} in`,"US customary format."],["Total inches",`${F(totalFeet*12,3)} in`,"Combined length in inches."]];
    bars=[{label:"Meters",value:meters,display:`${F(meters,4)} m`},{label:"Feet",value:totalFeet,display:`${F(totalFeet,4)} ft`},{label:"Yards",value:totalFeet/3,display:`${F(totalFeet/3,4)} yd`}];
    rows=[["Exact factor","1 ft = 0.3048 m","International foot."],["Meters",F(meters,8),"Calculated metric length."],["Decimal feet",F(totalFeet,8),"Meters divided by 0.3048."],["Feet and inches",`${wholeFeet} ft ${F(inches,4)} in`,"Separated customary units."]];
  } else if (engine === "loan") {
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
  } else if (engine === "take_home_pay") {
    const p=takeHomeProjection(),statusLabel=p.status==='joint'?"Married filing jointly":p.status==='head'?"Head of household":"Single";
    cards=[["Take-home / paycheck",USD(p.perPay),`${F(p.periods,0)} paychecks per year.`],["Annual take-home",USD(p.net),"After estimated taxes and deductions."],["Monthly average",USD(p.monthly),"Annual net pay divided by 12."],["Effective tax rate",`${F(p.effective,2)}%`,"Estimated taxes divided by gross pay."]];
    bars=[{label:"Gross pay",value:p.gross,display:USD(p.gross)},{label:"Take-home pay",value:p.net,display:USD(p.net)},{label:"Estimated taxes",value:p.totalTax,display:USD(p.totalTax)},{label:"Payroll deductions",value:p.totalDeductions,display:USD(p.totalDeductions)}];
    rows=[["Gross annual salary",USD(p.gross),USD(p.grossPerPay)+" gross per paycheck."],["Filing status",statusLabel,"Used for 2026 federal brackets and deduction."],["Federal deduction",USD(p.deduction),p.custom?"Entered custom deduction.":"2026 standard deduction."],["Federal taxable income",USD(p.federalTaxable),"Gross less modeled pre-tax amounts and deduction."],["Federal income tax",USD(p.federal),`${F(p.marginal*100,0)}% estimated marginal bracket.`],["Social Security",USD(p.social),"6.2% up to the $184,500 wage base."],["Medicare",USD(p.medicare),"1.45% plus applicable Additional Medicare Tax."],["State and local tax",USD(p.state),`${F(p.stateRate,2)}% entered effective rate.`],["Extra federal withholding",USD(p.extra),USD(p.extraPerPay)+" per paycheck."],["Pre-tax retirement",USD(p.retirement),"Reduces modeled federal taxable income, not FICA wages."],["Other pre-tax benefits",USD(p.pretax),"Assumed to reduce income-tax and FICA wages."],["Post-tax deductions",USD(p.posttax),"Reduces take-home pay only."],["Total estimated taxes",USD(p.totalTax),"Federal, FICA, state or local, and extra withholding."],["Annual take-home pay",USD(p.net),"Gross pay less modeled taxes and deductions."]];
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
  } else if (engine === "salary_advanced") {
    const p=salaryProjection();
    cards=[["New annual salary",USD(p.annual),"Gross pay after the entered raise."],["Annual raise",USD(p.raiseDollars),`${F(p.raisePercent,2)}% of current salary.`],["Selected pay period",USD(p.perPeriod),`${F(p.periods,0)} pay periods per year.`],["Real raise",`${F(p.realRaise,2)}%`,"After the entered inflation rate."]];
    bars=[{label:"Current annual",value:p.current,display:USD(p.current)},{label:"Annual raise",value:Math.max(0,p.raiseDollars),display:USD(p.raiseDollars)},{label:"New annual",value:p.annual,display:USD(p.annual)}];
    rows=[["Current annual salary",USD(p.current),"Entered gross annual pay."],["Raise",`${USD(p.raiseDollars)} (${F(p.raisePercent,2)}%)`,p.unit==='dollar'?"Converted from annual dollars.":"Converted from the entered percentage."],["New annual salary",USD(p.annual),"Current salary plus raise."],["Monthly pay",USD(p.monthly),"New annual salary divided by 12."],["Selected pay period",USD(p.perPeriod),`New annual salary divided by ${F(p.periods,0)}.`],["Weekly pay",USD(p.weekly),`New annual salary divided by ${F(p.weeks,1)} working weeks.`],["Hourly equivalent",USD(p.hourly),`${F(p.hours,1)} hours/week across ${F(p.weeks,1)} weeks.`],["Inflation-adjusted raise",`${F(p.realRaise,2)}%`,`Nominal ${F(p.raisePercent,2)}% raise versus ${F(p.inflation,2)}% inflation.`]];
  } else if (engine === "discount_advanced" || engine === "discount") {
    const p=engine === "discount_advanced"?discountProjection():{price:V('price'),first:V('discount'),second:0,quantity:1,taxRate:0,fees:0,unitPrice:V('price')*(1-V('discount')/100),effective:V('discount'),subtotal:V('price')*(1-V('discount')/100),savings:V('price')*V('discount')/100,tax:0,total:V('price')*(1-V('discount')/100)};
    cards=[["Checkout total",USD(p.total),"Discounted merchandise, estimated tax, and fees."],["Discounted unit price",USD(p.unitPrice),"Price per item after both discounts."],["Total savings",USD(p.savings),`Savings across ${F(p.quantity,0)} item(s).`],["Effective discount",`${F(p.effective,2)}%`,"Combined discount rate."]];
    bars=[{label:"Merchandise",value:p.subtotal,display:USD(p.subtotal)},{label:"Savings",value:p.savings,display:USD(p.savings)},{label:"Estimated tax",value:p.tax,display:USD(p.tax)},{label:"Fees",value:p.fees,display:USD(p.fees)}];
    rows=[["Original unit price",USD(p.price),"Before discounts."],["First discount",`${F(p.first,2)}%`,"Applied to original price."],["Second discount",`${F(p.second,2)}%`,"Applied to the remaining price."],["Effective discount",`${F(p.effective,2)}%`,"Combined rate, not a simple sum."],["Discounted unit price",USD(p.unitPrice),"After both discounts."],["Quantity",F(p.quantity,0),"Number of items."],["Merchandise subtotal",USD(p.subtotal),"Discounted unit price times quantity."],["Estimated sales tax",USD(p.tax),`${F(p.taxRate,3)}% of discounted merchandise.`],["Shipping and fees",USD(p.fees),"Entered amount."],["Checkout total",USD(p.total),"Subtotal plus estimated tax and fees."]];
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
  } else if (engine === "trade_in_estimate") {
    const p=tradeInProjection(), equityLabel=p.equity>=0?"Positive equity":"Negative equity";
    cards=[["Trade-in estimate",USD(p.trade),"Comparable less entered dealer costs."],[equityLabel,USD(Math.abs(p.equity)),"Trade estimate minus loan payoff."],["Entered tax benefit",USD(p.taxSavings),"Varies by jurisdiction and transaction."],["Effective trade value",USD(p.effective),"Trade estimate plus entered tax benefit."]];
    bars=[{label:"Trade-in value",value:p.trade,display:USD(p.trade)},{label:"Loan payoff",value:p.payoff,display:USD(p.payoff)},{label:"Tax benefit",value:p.taxSavings,display:USD(p.taxSavings)},{label:"Dealer costs",value:p.margin+p.reconditioning,display:USD(p.margin+p.reconditioning)}];
    rows=[["Comparable retail listing",USD(p.comparable),"Current local asking-price benchmark."],["Condition/mileage adjustment",USD(p.adjustment),"Positive or negative difference."],["Dealer resale margin",USD(p.margin),"Entered planning allowance."],["Repair and cleanup",USD(p.reconditioning),"Expected reconditioning."],["Estimated trade-in",USD(p.trade),"Planning estimate, not an offer."],["Loan payoff",USD(p.payoff),"Entered lender payoff."],["Loan equity",USD(p.equity),p.equity>=0?"Value above payoff.":"Payoff above value."],["Entered sales-tax benefit",USD(p.taxSavings),"Confirm local rules."]];
  } else if (engine === "used_car_estimate") {
    const p=usedCarProjection(), range=(value)=>`${USD(value*.96)} - ${USD(value*1.04)}`;
    cards=[["Private-party estimate",USD(p.privateValue),"Midpoint for an as-is private sale."],["Trade-in estimate",USD(p.trade),"Midpoint after entered dealer spread."],["Adjusted retail",USD(p.retail),"Comparable retail after adjustments."],["Pricing spread",`${F(p.spread,1)}%`,"Entered retail-to-trade difference."]];
    bars=[{label:"Dealer retail",value:p.retail,display:USD(p.retail)},{label:"Private party",value:p.privateValue,display:USD(p.privateValue)},{label:"Trade-in",value:p.trade,display:USD(p.trade)}];
    rows=[["Local retail benchmark",USD(p.benchmark),"Comparable asking price."],["Condition adjustment",`${F(p.condition,1)}%`,"Selected condition factor."],["Mileage adjustment",USD(p.mileage),"Entered dollar adjustment."],["Options/history adjustment",USD(p.options),"Entered dollar adjustment."],["Regional adjustment",`${F(p.regional,1)}%`,"Local demand assumption."],["Adjusted retail range",range(p.retail),"Midpoint plus or minus 4%."],["Private-party range",range(p.privateValue),"Planning range."],["Trade-in range",range(p.trade),"Planning range, not an offer."]];
  } else if (engine === "concrete_advanced") {
    const p=concreteProjection(), shapeLabel=p.shape==='slab'?"Slab or footing":p.shape==='column'?"Round column":"Round post holes", bagLabel=document.getElementById('concrete_bag_size')?.selectedOptions[0]?.textContent||"Selected bag";
    cards=[["Concrete needed",`${F(p.yards,2)} yd³`,"Includes entered waste."],["Volume",`${F(p.withWaste,2)} ft³`,"Final ordering volume."],["Bag count",F(p.bags,0),bagLabel],["Estimated bag cost",USD(p.bagCost),"Price per bag times count."]];
    bars=[{label:"Volume before waste",value:p.baseFt3,display:`${F(p.baseFt3,2)} ft³`},{label:"Volume with waste",value:p.withWaste,display:`${F(p.withWaste,2)} ft³`},{label:"Bag cost",value:p.bagCost,display:USD(p.bagCost)},{label:"Ready-mix material",value:p.readyCost,display:USD(p.readyCost)}];
    rows=[["Project shape",shapeLabel,"Selected geometry."],["Volume before waste",`${F(p.baseFt3,3)} ft³`,"Calculated dimensions."],["Waste allowance",`${F(p.waste,1)}%`,"Entered planning margin."],["Ordering volume",`${F(p.withWaste,3)} ft³`,`${F(p.yards,3)} cubic yards.`],["Selected bag yield",`${F(p.yieldPerBag,3)} ft³`,"Approximate yield per bag."],["Bags required",F(p.bags,0),"Rounded up to a whole bag."],["Estimated bag cost",USD(p.bagCost),"Excludes tax and labor."],["Estimated ready-mix material",USD(p.readyCost),"Excludes delivery and fees."]];
  } else if (engine === "roof_pitch_advanced") {
    const p=roofPitchProjection();
    cards=[["Roof pitch",`${F(p.pitch,2)}:12`,"Rise per 12 inches of run."],["Roof angle",`${F(p.angle,2)}°`,"Angle from horizontal."],["Pitch multiplier",F(p.factor,4),"Sloped length per horizontal foot."],["Rafter length",`${F(p.rafter,2)} ft`,"Run plus horizontal overhang."]];
    bars=[{label:"Horizontal run",value:p.run,display:`${F(p.run,2)} ft`},{label:"Roof rise",value:p.rise,display:`${F(p.rise,2)} ft`},{label:"Rafter length",value:p.rafter,display:`${F(p.rafter,2)} ft`},{label:"Roofing squares",value:p.squares,display:F(p.squares,2)}];
    rows=[["Pitch",`${F(p.pitch,3)}:12`,"Normalized rise per 12."],["Percent slope",`${F(p.percent,3)}%`,"Rise divided by run."],["Angle",`${F(p.angle,3)}°`,"Angle from horizontal."],["Pitch multiplier",F(p.factor,5),"Square root of 1 plus slope squared."],["Horizontal rafter run",`${F(p.run,3)} ft`,"Entered plan distance."],["Roof rise",`${F(p.rise,3)} ft`,"Run times slope."],["Rafter with overhang",`${F(p.rafter,3)} ft`,"Geometry estimate before cuts."],["Sloped roof area",`${F(p.slopedArea,1)} ft²`,"Horizontal plan area times multiplier."],["Roofing squares",F(p.squares,2),"One square equals 100 square feet."]];
  } else if (engine === "rafter_advanced") {
    const p=rafterProjection();
    cards=[["Rafter length",`${F(p.totalLength,2)} ft`,"Includes horizontal overhang."],["Roof rise",`${F(p.rise,2)} ft`,"Over entered horizontal run."],["Slope factor",F(p.factor,4),"Length per horizontal foot."],["Total linear feet",`${F(p.totalLinear,1)} ft`,`${F(p.quantity,0)} rafters before waste.`]];
    bars=[{label:"Wall-to-ridge length",value:p.baseLength,display:`${F(p.baseLength,2)} ft`},{label:"Sloped tail",value:p.tailLength,display:`${F(p.tailLength,2)} ft`},{label:"Roof rise",value:p.rise,display:`${F(p.rise,2)} ft`},{label:"Total per rafter",value:p.totalLength,display:`${F(p.totalLength,2)} ft`}];
    rows=[["Roof pitch",`${F(p.pitch,2)}:12`,"Entered rise per 12."],["Pitch angle",`${F(p.angle,3)}°`,"Angle from horizontal."],["Slope factor",F(p.factor,5),"Sloped length multiplier."],["Horizontal run",`${F(p.run,3)} ft`,"Wall support to ridge."],["Roof rise",`${F(p.rise,3)} ft`,"Run times pitch ratio."],["Base rafter length",`${F(p.baseLength,3)} ft`,"Before overhang."],["Sloped overhang length",`${F(p.tailLength,3)} ft`,"From horizontal overhang."],["Total rafter length",`${F(p.totalLength,3)} ft`,"Before cut adjustments."],["Total linear footage",`${F(p.totalLinear,2)} ft`,"Length times rafter count."]];
  } else if (engine === "square_footage_advanced") {
    const p=squareFootageProjection(), shape={rectangle:"Rectangle",circle:"Circle",triangle:"Triangle",room_walls:"Four room walls"}[p.shape]||p.shape;
    cards=[["Net area",`${F(p.area,2)} ft²`,shape],["Order area",`${F(p.orderArea,2)} ft²`,`${F(p.overage,1)}% overage included.`],["Perimeter",p.perimeter===null?"n/a":`${F(p.perimeter,2)} ft`,"Boundary length when determined."],["Material cost",USD(p.cost),`${USD(p.price)} per square foot.`]];
    bars=[{label:"Measured area",value:p.area,display:`${F(p.area,2)} ft²`},{label:"Overage amount",value:p.orderArea-p.area,display:`${F(p.orderArea-p.area,2)} ft²`},{label:"Order area",value:p.orderArea,display:`${F(p.orderArea,2)} ft²`},{label:"Estimated cost",value:p.cost,display:USD(p.cost)}];
    rows=[["Area type",shape,"Selected geometry."],["Measured or net area",`${F(p.area,3)} ft²`,p.shape==='room_walls'?"Gross walls minus openings.":"Calculated geometry."],["Gross wall area",p.shape==='room_walls'?`${F(p.gross,3)} ft²`:"n/a","Available in wall mode."],["Openings deducted",p.shape==='room_walls'?`${F(p.openings,3)} ft²`:"n/a","Doors and windows."],["Perimeter",p.perimeter===null?"n/a":`${F(p.perimeter,3)} ft`,"Triangle sides are not inferred."],["Overage",`${F(p.overage,2)}%`,"Entered planning allowance."],["Order area",`${F(p.orderArea,3)} ft²`,"Area after overage."],["Estimated cost",USD(p.cost),"Area times entered unit price."]];
  } else if (engine === "flooring_advanced") {
    const p=flooringProjection();
    cards=[["Boxes to buy",F(p.boxes,0),"Rounded up to complete boxes."],["Order target",`${F(p.target,1)} ft²`,`${F(p.waste,1)}% waste included.`],["Purchased coverage",`${F(p.purchased,1)} ft²`,"Box count times coverage."],["Estimated total",USD(p.totalCost),"Flooring plus entered underlayment."]];
    bars=[{label:"Measured floor",value:p.area,display:`${F(p.area,1)} ft²`},{label:"Waste allowance",value:p.target-p.area,display:`${F(p.target-p.area,1)} ft²`},{label:"Purchased coverage",value:p.purchased,display:`${F(p.purchased,1)} ft²`},{label:"Flooring cost",value:p.boxCost,display:USD(p.boxCost)},{label:"Underlayment cost",value:p.underlayCost,display:USD(p.underlayCost)}];
    rows=[["Measured floor area",`${F(p.area,2)} ft²`,"Room plus extra area."],["Waste allowance",`${F(p.waste,2)}%`,"Cuts and planning margin."],["Order target",`${F(p.target,2)} ft²`,"Area after waste."],["Coverage per box",`${F(p.boxCoverage,2)} ft²`,"Entered package label."],["Boxes to buy",F(p.boxes,0),"Rounded up."],["Purchased coverage",`${F(p.purchased,2)} ft²`,"Whole-box coverage."],["Left after installation",`${F(p.leftover,2)} ft²`,"Includes waste and package remainder."],["Flooring cost",USD(p.boxCost),"Boxes times price."],["Underlayment rolls",F(p.underlayRolls,0),"Rounded up separately."],["Estimated total",USD(p.totalCost),"Entered materials only."]];
  } else if (engine === "tile_advanced") {
    const p=tileProjection();
    cards=[["Boxes to buy",F(p.boxes,0),`${F(p.perBox,0)} pieces per box.`],["Tiles needed",F(p.pieces,0),`${F(p.waste,1)}% waste included.`],["Purchased coverage",`${F(p.purchasedArea,1)} ft²`,"Full boxes converted to area."],["Estimated tile cost",USD(p.cost),"Boxes times entered price."]];
    bars=[{label:"Project area",value:p.area,display:`${F(p.area,1)} ft²`},{label:"Waste allowance",value:p.targetArea-p.area,display:`${F(p.targetArea-p.area,1)} ft²`},{label:"Purchased coverage",value:p.purchasedArea,display:`${F(p.purchasedArea,1)} ft²`},{label:"Tile cost",value:p.cost,display:USD(p.cost)}];
    rows=[["Project area",`${F(p.area,2)} ft²`,"Length times width."],["Tile face size",`${F(p.tileWidth,2)} x ${F(p.tileHeight,2)} in`,`${F(p.tileArea,4)} square feet each.`],["Waste allowance",`${F(p.waste,2)}%`,"Entered cutting margin."],["Order target",`${F(p.targetArea,2)} ft²`,"Project area after waste."],["Tiles needed",F(p.pieces,0),"Rounded up by piece."],["Tiles per box",F(p.perBox,0),"Entered package quantity."],["Boxes to buy",F(p.boxes,0),"Rounded up to full boxes."],["Purchased tile",`${F(p.purchasedArea,2)} ft²`,`${F(p.purchasedPieces,0)} total pieces.`],["Left after installation",`${F(p.leftover,2)} ft²`,"Includes waste and box remainder."],["Estimated cost",USD(p.cost),"Tile boxes only."]];
  } else if (engine === "deck_advanced") {
    const p=deckProjection();
    cards=[["Full boards to buy",F(p.boards,0),`${F(p.waste,1)}% waste included.`],["Board rows",F(p.rows,0),`${F(p.boardWidth,3)} in boards plus ${F(p.gap,3)} in gaps.`],["Fastener boxes",F(p.fastenerPacks,0),`${F(p.fasteners,0)} fasteners estimated.`],["Estimated materials",USD(p.totalCost),"Boards plus entered fastener cost."]];
    bars=[{label:"Base whole boards",value:p.baseBoards,display:F(p.baseBoards,0)},{label:"Boards with waste",value:p.boards,display:F(p.boards,0)},{label:"Joist lines",value:p.joists,display:F(p.joists,0)},{label:"Fastener boxes",value:p.fastenerPacks,display:F(p.fastenerPacks,0)},{label:"Material cost",value:p.totalCost,display:USD(p.totalCost)}];
    rows=[["Deck area",`${F(p.area,2)} ft²`,"Length times width."],["Board rows",F(p.rows,0),"Rounded across deck width."],["Stock boards per row",F(p.boardsPerRow,0),"Rounded from deck length."],["Base whole-board count",F(p.baseBoards,0),"Rows times boards per row."],["Waste allowance",`${F(p.waste,2)}%`,"Applied to whole-board count."],["Full boards to buy",F(p.boards,0),"Final count rounded up."],["Coverage linear footage",`${F(p.coverageLinear,1)} ft`,"Rows times deck length."],["Ordered stock footage",`${F(p.orderedLinear,1)} ft`,"Full boards times stock length."],["Joist lines",F(p.joists,0),`${F(p.joistSpacing,2)} in on center, including edges.`],["Fasteners",F(p.fasteners,0),`${F(p.fastenersPerCrossing,0)} per row and joist crossing.`],["Fastener boxes",F(p.fastenerPacks,0),`${F(p.fastenersPerPack,0)} per box.`],["Board cost",USD(p.boardCost),"Full boards times entered price."],["Fastener cost",USD(p.fastenerCost),"Full boxes times entered price."],["Estimated total",USD(p.totalCost),"Entered decking and fasteners only."]];
  } else if (engine === "board_foot_advanced") {
    const p=boardFootProjection();
    cards=[["Board feet to order",F(p.order,2),`${F(p.waste,1)}% waste included.`],["Board feet per piece",F(p.perBoard,3),`${F(p.thickness,2)} x ${F(p.width,2)} in x ${F(p.length,2)} ft.`],["Cubic feet",F(p.cubicFeet,3),"Waste-adjusted lumber volume."],["Estimated lumber cost",USD(p.cost),`${USD(p.price)} per board foot.`]];
    bars=[{label:"Board feet before waste",value:p.total,display:F(p.total,2)},{label:"Waste allowance",value:p.order-p.total,display:F(p.order-p.total,2)},{label:"Board feet to order",value:p.order,display:F(p.order,2)},{label:"Estimated cost",value:p.cost,display:USD(p.cost)}];
    rows=[["Dimensions",`${F(p.thickness,2)} in x ${F(p.width,2)} in x ${F(p.length,2)} ft`,"Entered pricing dimensions."],["Quantity",F(p.quantity,0),"Whole pieces."],["Board feet per piece",F(p.perBoard,4),"Thickness x width x length / 12."],["Board feet before waste",F(p.total,4),"Per-piece volume times quantity."],["Waste allowance",`${F(p.waste,2)}%`,"Entered purchasing margin."],["Board feet to order",F(p.order,4),"Volume after waste."],["Cubic feet",F(p.cubicFeet,4),"Board feet divided by 12."],["Total linear feet",`${F(p.linearFeet,2)} ft`,"Length times quantity before waste."],["Price per board foot",USD(p.price),"Entered unit price."],["Estimated cost",USD(p.cost),"Order volume times unit price."]];
  } else if (engine === "voltage_drop_advanced") {
    const p=voltageDropProjection(), material=p.material==='copper'?"Copper":"Aluminum", phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Voltage drop",`${F(p.drop,2)} V`,`${F(p.percent,2)}% of source voltage.`],["Voltage at load",`${F(p.loadVoltage,2)} V`,`${F(p.voltage,1)} V source.`],["Drop-target wire",`${p.recommended.g} AWG`,`${material}; ${F(p.limit,1)}% target.`],["Maximum run",`${F(p.maxLength,1)} ft`,"For selected wire and target."]];
    bars=[{label:"Source voltage",value:p.voltage,display:`${F(p.voltage,1)} V`},{label:"Voltage at load",value:p.loadVoltage,display:`${F(p.loadVoltage,2)} V`},{label:"Voltage lost",value:p.drop,display:`${F(p.drop,2)} V`},{label:"Drop limit",value:p.voltage*p.limit/100,display:`${F(p.limit,1)}%`}];
    rows=[["Circuit type",phase,"Selected formula."],["Conductor",`${p.gauge} AWG ${material}`,`${F(wireResistance(p.row,p.material),4)} ohms/1,000 ft reference.`],["One-way run",`${F(p.length,2)} ft`,"Round trip is handled by formula."],["Load current",`${F(p.amps,2)} A`,"Entered current."],["Source voltage",`${F(p.voltage,2)} V`,"Entered system voltage."],["Voltage drop",`${F(p.drop,3)} V`,`${F(p.percent,3)}% of source.`],["Voltage at load",`${F(p.loadVoltage,3)} V`,"Source minus estimated drop."],["Target conductor",`${p.recommended.g} AWG`,"Drop-only recommendation."],["Maximum selected-wire run",`${F(p.maxLength,2)} ft`,`${F(p.limit,2)}% entered target.`]];
  } else if (engine === "wire_size_advanced") {
    const p=wireSizeProjection(), material=p.material==='copper'?"Copper":"Aluminum", phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Recommended wire",`${p.recommended.g} AWG`,`${material}; larger of both checks.`],["Planning current",`${F(p.designAmps,2)} A`,"Includes continuous-load factor."],["Reference ampacity",`${F(p.ampacity,0)} A`,`${p.temp}°C selected column.`],["Voltage drop",`${F(p.dropPercent,2)}%`,`${F(p.drop,2)} V over entered run.`]];
    bars=[{label:"Actual load",value:p.amps,display:`${F(p.amps,2)} A`},{label:"Planning current",value:p.designAmps,display:`${F(p.designAmps,2)} A`},{label:"Reference ampacity",value:p.ampacity,display:`${F(p.ampacity,0)} A`},{label:"Drop percentage",value:p.dropPercent,display:`${F(p.dropPercent,2)}%`}];
    rows=[["Circuit type",phase,"Selected voltage-drop formula."],["Conductor",material,`${p.temp}°C reference column.`],["Actual load",`${F(p.amps,2)} A`,"Entered total current."],["Continuous portion",`${F(p.continuous,2)} A`,"Receives 125% planning factor."],["Planning current",`${F(p.designAmps,2)} A`,"Ampacity sizing load."],["Ampacity-only size",`${p.ampacityRow.g} AWG`,"First size meeting reference ampacity."],["Drop-only size",`${p.dropRow.g} AWG`,`${F(p.limit,2)}% target.`],["Recommended size",`${p.recommended.g} AWG`,"Larger of ampacity and drop checks."],["Reference ampacity",`${F(p.ampacity,0)} A`,"Before correction or adjustment."],["Estimated voltage drop",`${F(p.drop,3)} V`,`${F(p.dropPercent,3)}%; ${F(p.loadVoltage,2)} V at load.`]];
  } else if (engine === "breaker_advanced") {
    const p=breakerProjection();
    cards=[["Reference breaker",`${F(p.breaker,0)} A`,`${F(p.poles,0)} pole selection.`],["Planning current",`${F(p.planning,2)} A`,"125% continuous plus noncontinuous."],["Connected load",`${F(p.actual,2)} A`,`${F(p.utilization,1)}% of reference breaker.`],["Connected power",`${F(p.power,0)} W`,`${F(p.voltage,0)} V x actual amps.`]];
    bars=[{label:"Continuous load",value:p.continuous,display:`${F(p.continuous,2)} A`},{label:"Noncontinuous load",value:p.noncontinuous,display:`${F(p.noncontinuous,2)} A`},{label:"Planning current",value:p.planning,display:`${F(p.planning,2)} A`},{label:"Reference breaker",value:p.breaker,display:`${F(p.breaker,0)} A`}];
    rows=[["Continuous load",`${F(p.continuous,3)} A`,"Multiplied by 125%."],["Noncontinuous load",`${F(p.noncontinuous,3)} A`,"Added at 100%."],["Connected load",`${F(p.actual,3)} A`,"Sum before planning factor."],["Minimum planning current",`${F(p.planning,3)} A`,"Continuous x 1.25 plus noncontinuous."],["Reference breaker",`${F(p.breaker,0)} A`,"Next familiar standard rating."],["Planning headroom",`${F(p.headroom,2)} A`,"Breaker minus planning current."],["Connected-load utilization",`${F(p.utilization,2)}%`,"Actual amps divided by reference breaker."],["Connected power",`${F(p.power,1)} W`,"Simple volts x amps display."]];
  } else if (engine === "electrical_load_advanced") {
    const p=electricalLoadProjection(), phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Actual current",`${F(p.amps,2)} A`,`${F(p.watts,0)} W total load.`],["Planning current",`${F(p.planningAmps,2)} A`,"Continuous portion at 125%."],["Apparent power",`${F(p.va,0)} VA`,`${F(p.pf,2)} power factor.`],["Reference breaker",`${F(p.breaker,0)} A`,"Planning result only."]];
    bars=[{label:"Continuous power",value:p.continuous,display:`${F(p.continuous,0)} W`},{label:"Noncontinuous power",value:p.noncontinuous,display:`${F(p.noncontinuous,0)} W`},{label:"Actual current",value:p.amps,display:`${F(p.amps,2)} A`},{label:"Planning current",value:p.planningAmps,display:`${F(p.planningAmps,2)} A`}];
    rows=[["Circuit type",phase,"Selected current formula."],["Continuous load",`${F(p.continuous,2)} W`,"Receives 125% planning factor."],["Noncontinuous load",`${F(p.noncontinuous,2)} W`,"Included at 100%."],["Total real power",`${F(p.watts,2)} W`,"Entered loads combined."],["Power factor",F(p.pf,3),p.phase==='dc'?"Not applied to DC.":"Used for AC current."],["Apparent power",`${F(p.va,2)} VA`,"Watts divided by power factor."],["Actual current",`${F(p.amps,3)} A`,"Before continuous-load factor."],["Planning power",`${F(p.planningWatts,2)} W`,"Continuous x 1.25 plus other load."],["Planning current",`${F(p.planningAmps,3)} A`,"Used for reference breaker."],["Reference breaker",`${F(p.breaker,0)} A`,`${F(p.utilization,1)}% connected-load utilization.`]];
  } else if (engine === "watts_amps_advanced") {
    const p=wattsAmpsProjection(), phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Calculated current",`${F(p.amps,3)} A`,`${F(p.watts,1)} W real power.`],["Real power",`${F(p.watts/1000,3)} kW`,"Entered wattage."],["Apparent power",`${F(p.va,1)} VA`,`${F(p.pf,2)} power factor.`],["Planning current",`${F(p.planningAmps,3)} A`,p.continuous?"Includes 125% continuous factor.":"No continuous factor selected."]];
    bars=[{label:"Real power",value:p.watts,display:`${F(p.watts,1)} W`},{label:"Apparent power",value:p.va,display:`${F(p.va,1)} VA`},{label:"Reactive power",value:p.vars,display:`${F(p.vars,1)} VAR`},{label:"Current",value:p.amps,display:`${F(p.amps,3)} A`}];
    rows=[["Power system",phase,p.phase==='three'?"Uses line-to-line voltage.":"Selected conversion mode."],["Real power",`${F(p.watts,3)} W`,`${F(p.watts/1000,4)} kW.`],["Voltage",`${F(p.voltage,3)} V`,p.phase==='three'?"Line-to-line RMS voltage.":"Entered voltage."],["Power factor",F(p.pf,3),p.phase==='dc'?"Fixed at 1 for DC.":"Real power divided by apparent power."],["Calculated current",`${F(p.amps,4)} A`,"Formula result."],["Apparent power",`${F(p.va,3)} VA`,`${F(p.va/1000,4)} kVA.`],["Reactive power",`${F(p.vars,3)} VAR`,"Simplified magnitude."],["Load duration",p.continuous?"Continuous planning":"Conversion only",p.continuous?"125% factor shown.":"No sizing factor applied."],["Planning current",`${F(p.planningAmps,4)} A`,p.continuous?"Calculated amps x 1.25.":"Same as calculated amps."]];
  } else if (engine === "amps_watts_advanced") {
    const p=ampsWattsProjection(), phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Real power",`${F(p.watts,1)} W`,`${F(p.watts/1000,3)} kW.`],["Apparent power",`${F(p.va,1)} VA`,`${F(p.va/1000,3)} kVA.`],["Reactive power",`${F(p.vars,1)} VAR`,"Simplified magnitude."],["Power factor",F(p.pf,3),p.phase==='dc'?"Fixed at 1 for DC.":"Entered AC power factor."]];
    bars=[{label:"Real power",value:p.watts,display:`${F(p.watts,1)} W`},{label:"Apparent power",value:p.va,display:`${F(p.va,1)} VA`},{label:"Reactive power",value:p.vars,display:`${F(p.vars,1)} VAR`},{label:"Current",value:p.amps,display:`${F(p.amps,3)} A`}];
    rows=[["Power system",phase,p.phase==='three'?"Uses line-to-line voltage.":"Selected conversion mode."],["Current",`${F(p.amps,4)} A`,"Entered RMS current."],["Voltage",`${F(p.voltage,3)} V`,p.phase==='three'?"Line-to-line RMS voltage.":"Entered voltage."],["Power factor",F(p.pf,3),p.phase==='dc'?"Fixed at 1 for DC.":"Entered AC ratio."],["Real power",`${F(p.watts,3)} W`,`${F(p.watts/1000,4)} kW.`],["Apparent power",`${F(p.va,3)} VA`,`${F(p.va/1000,4)} kVA.`],["Reactive power",`${F(p.vars,3)} VAR`,"Square root of VA² minus W²."]];
  } else if (engine === "tire_compare") {
    const p=tireComparison(), speedError=p.actualSpeed-p.indicated;
    cards=[["Diameter difference",`${p.differencePct>=0?'+':''}${F(p.differencePct,2)}%`,"New tire versus original."],["Actual speed",`${F(p.actualSpeed,2)} mph`,`${F(p.indicated,0)} mph indicated.`],["Ground clearance",`${p.clearance>=0?'+':''}${F(p.clearance,2)} in`,"Half the diameter change."],["Revolutions per mile",F(p.next.revsPerMile,1),"Calculated new tire value."]];
    bars=[{label:"Original diameter",value:p.original.diameter,display:`${F(p.original.diameter,2)} in`},{label:"New diameter",value:p.next.diameter,display:`${F(p.next.diameter,2)} in`},{label:"Original sidewall",value:p.original.sidewall/25.4,display:`${F(p.original.sidewall,1)} mm`},{label:"New sidewall",value:p.next.sidewall/25.4,display:`${F(p.next.sidewall,1)} mm`}];
    rows=[["Original size",`${F(p.original.width,0)}/${F(p.original.aspect,0)}R${F(p.original.rim,1)}`,"Entered baseline tire."],["New size",`${F(p.next.width,0)}/${F(p.next.aspect,0)}R${F(p.next.rim,1)}`,"Entered comparison tire."],["Original diameter",`${F(p.original.diameter,3)} in`,"Nominal calculated diameter."],["New diameter",`${F(p.next.diameter,3)} in`,"Nominal calculated diameter."],["Diameter difference",`${p.differencePct>=0?'+':''}${F(p.differencePct,3)}%`,"Common 3% guidance is not fitment approval."],["Speedometer difference",`${speedError>=0?'+':''}${F(speedError,2)} mph`,`${F(p.indicated,0)} mph indicated.`],["Ground-clearance change",`${p.clearance>=0?'+':''}${F(p.clearance,3)} in`,"Static estimate."],["New revolutions per mile",F(p.next.revsPerMile,2),"Actual tire specs may vary."]];
  } else if (engine === "wheel_offset_compare") {
    const p=wheelOffsetComparison(), clearanceNote=p.innerClearance>=0?"More suspension-side clearance.":"Less suspension-side clearance.";
    cards=[["Outer position",`${p.outerPoke>=0?'+':''}${F(p.outerPoke,1)} mm`,p.outerPoke>=0?"Farther toward the fender.":"Farther inward."],["Inner clearance",`${p.innerClearance>=0?'+':''}${F(p.innerClearance,1)} mm`,clearanceNote],["Track change",`${p.trackChange>=0?'+':''}${F(p.trackChange,1)} mm`,"Estimated across both wheels."],["Effective new offset",`ET${F(p.effectiveOffset,1)}`,"New offset minus spacer."]];
    bars=[{label:"Outer position change",value:p.outerPoke,display:`${p.outerPoke>=0?'+':''}${F(p.outerPoke,1)} mm`},{label:"Inner clearance change",value:p.innerClearance,display:`${p.innerClearance>=0?'+':''}${F(p.innerClearance,1)} mm`},{label:"Track change",value:p.trackChange,display:`${p.trackChange>=0?'+':''}${F(p.trackChange,1)} mm`},{label:"Spacer",value:p.spacer,display:`${F(p.spacer,1)} mm`}];
    rows=[["Current wheel",`${F(p.currentWidth,1)} in ET${F(p.currentOffset,1)}`,"Entered baseline wheel."],["New wheel",`${F(p.newWidth,1)} in ET${F(p.newOffset,1)}`,"Before spacer adjustment."],["Effective new offset",`ET${F(p.effectiveOffset,1)}`,"Offset minus spacer thickness."],["Inner clearance change",`${p.innerClearance>=0?'+':''}${F(p.innerClearance,2)} mm`,clearanceNote],["Outer position change",`${p.outerPoke>=0?'+':''}${F(p.outerPoke,2)} mm`,p.outerPoke>=0?"Additional poke.":"Moves inward."],["Estimated track change",`${p.trackChange>=0?'+':''}${F(p.trackChange,2)} mm`,"Both sides combined."],["Current backspacing",`${F(p.currentBackspacing,3)} in`,"Includes estimated rim lips."],["New backspacing",`${F(p.newBackspacing,3)} in`,"Includes estimated rim lips and spacer."]];
  } else if (engine === "mpg_advanced") {
    const distance=V('distance'), fuel=V('fuel_used'), miles=document.getElementById('distance_unit')?.value==='kilometers'?distance*0.621371192237:distance, liters=fuel*(document.getElementById('fuel_unit')?.value==='us_gallon'?3.785411784:document.getElementById('fuel_unit')?.value==='imperial_gallon'?4.54609:1), km=miles/0.621371192237, usGallons=liters/3.785411784, imperialGallons=liters/4.54609, usMpg=usGallons>0?miles/usGallons:0, imperialMpg=imperialGallons>0?miles/imperialGallons:0, l100=km>0?liters/km*100:0, kmL=liters>0?km/liters:0;
    cards=[["US fuel economy",`${F(usMpg,2)} MPG`,"Miles per US gallon."],["Metric consumption",`${F(l100,2)} L/100 km`,"Lower is more efficient."],["Imperial fuel economy",`${F(imperialMpg,2)} MPG`,"Miles per UK gallon."],["Kilometers per liter",`${F(kmL,2)} km/L`,"Distance per liter."]];
    bars=[{label:"US MPG",value:usMpg,display:F(usMpg,2)},{label:"Imperial MPG",value:imperialMpg,display:F(imperialMpg,2)},{label:"km/L",value:kmL,display:F(kmL,2)},{label:"L/100 km",value:l100,display:F(l100,2)}];
    rows=[["Entered distance",`${F(distance,2)} ${document.getElementById('distance_unit')?.value||'miles'}`,"Normalized before conversion."],["Entered fuel",`${F(fuel,3)} ${(document.getElementById('fuel_unit')?.selectedOptions[0]?.textContent)||'fuel units'}`,"Normalized to liters."],["Distance in miles",F(miles,4),"Used for MPG."],["Fuel in US gallons",F(usGallons,4),"Used for US MPG."],["US MPG",F(usMpg,3),"Miles divided by US gallons."],["L/100 km",F(l100,3),"Liters used per 100 kilometers."]];
  } else if (engine === "fuel_cost_advanced") {
    const metric=document.getElementById('trip_units')?.value==='metric', oneWay=V('distance'), multiplier=Math.max(1,V('trip_type'))*Math.max(1,V('trips')), distance=oneWay*multiplier, efficiency=Math.max(.01,V('efficiency')), fuel=metric?distance*efficiency/100:distance/efficiency, price=V('fuelprice'), cost=fuel*price, currency=document.getElementById('currency')?.value||'USD', people=Math.max(1,V('people')), perPerson=cost/people, perDistance=distance>0?cost/distance:0;
    cards=[["Estimated fuel cost",MONEY(cost,currency),"For all selected trips."],["Fuel needed",`${F(fuel,2)} ${metric?'L':'gal'}`,"Estimated volume used."],["Cost per person",MONEY(perPerson,currency),`Split between ${F(people,0)} people.`],[`Cost per ${metric?'km':'mile'}`,MONEY(perDistance,currency),"Fuel cost only."]];
    bars=[{label:"Fuel cost",value:cost,display:MONEY(cost,currency)},{label:"Per person",value:perPerson,display:MONEY(perPerson,currency)},{label:`Fuel ${metric?'liters':'gallons'}`,value:fuel,display:F(fuel,2)}];
    rows=[["One-way distance",`${F(oneWay,1)} ${metric?'km':'mi'}`,"Entered route length."],["Total distance",`${F(distance,1)} ${metric?'km':'mi'}`,"Trip type multiplied by trip count."],["Fuel economy",`${F(efficiency,2)} ${metric?'L/100 km':'MPG'}`,"Entered real-world estimate."],["Fuel price",`${MONEY(price,currency)} / ${metric?'L':'gal'}`,"No currency conversion applied."],["Fuel needed",`${F(fuel,3)} ${metric?'L':'gal'}`,"Calculated trip volume."],["Total fuel cost",MONEY(cost,currency),"Fuel only."],["Cost per person",MONEY(perPerson,currency),"Even split."]];
  } else if (engine === "payload") {
    const capacity=V('gvwr')-V('curb'), occupants=V('people'), cargo=V('cargo'), tongue=V('tongue'), used=occupants+cargo+tongue, remaining=capacity-used, utilization=capacity>0?used/capacity*100:0;
    cards=[["Remaining payload",`${F(remaining,0)} lb`,remaining>=0?"Available before reaching GVWR.":"Entered load exceeds GVWR."],["Payload capacity",`${F(capacity,0)} lb`,"GVWR minus curb weight."],["Payload used",`${F(used,0)} lb`,"Occupants, cargo, and tongue weight."],["Utilization",`${F(utilization,1)}%`,"Share of payload capacity used."]];
    bars=[{label:"Occupants",value:occupants,display:`${F(occupants,0)} lb`},{label:"Cargo",value:cargo,display:`${F(cargo,0)} lb`},{label:"Tongue weight",value:tongue,display:`${F(tongue,0)} lb`},{label:"Remaining",value:Math.max(0,remaining),display:`${F(remaining,0)} lb`}];
    rows=[["GVWR",`${F(V('gvwr'),0)} lb`,"Maximum entered vehicle weight."],["Curb weight",`${F(V('curb'),0)} lb`,"Entered empty vehicle weight."],["Payload capacity",`${F(capacity,0)} lb`,"GVWR minus curb weight."],["Loaded vehicle weight",`${F(V('curb')+used,0)} lb`,"Curb weight plus entered payload."],["Remaining payload",`${F(remaining,0)} lb`,remaining>=0?"Within entered GVWR.":"Reduce load before travel."]];
  } else if (engine === "towing") {
    const loaded=V('curb')+V('people')+V('cargo'), remainingPayload=Math.max(0,V('gvwr')-loaded), pct=Math.max(.01,V('tongue_pct')/100), limits=[{label:"Vehicle tow rating",value:V('rating')},{label:"GCWR headroom",value:Math.max(0,V('gcwr')-loaded)},{label:"Hitch rating",value:V('hitch_rating')},{label:"Payload-based limit",value:remainingPayload/pct}], controlling=limits.reduce((a,b)=>b.value<a.value?b:a), tongue=controlling.value*pct;
    cards=[["Planning trailer limit",`${F(controlling.value,0)} lb`,"Lowest entered or calculated limit."],["Controlling factor",controlling.label,"The first rating reached."],["Estimated tongue weight",`${F(tongue,0)} lb`,`${F(V('tongue_pct'),1)}% of planning trailer limit.`],["Payload before hitch",`${F(remainingPayload,0)} lb`,"Available after passengers and cargo."]];
    bars=limits.map(item=>({label:item.label,value:item.value,display:`${F(item.value,0)} lb`}));
    rows=[["Loaded tow vehicle",`${F(loaded,0)} lb`,"Curb weight, occupants, and cargo."],["Tow rating",`${F(V('rating'),0)} lb`,"Vehicle manufacturer's entered rating."],["GCWR trailer headroom",`${F(Math.max(0,V('gcwr')-loaded),0)} lb`,"GCWR minus loaded vehicle."],["Hitch trailer rating",`${F(V('hitch_rating'),0)} lb`,"Entered equipment rating."],["Payload-based trailer limit",`${F(remainingPayload/pct,0)} lb`,"Remaining payload divided by tongue percentage."],["Planning limit",`${F(controlling.value,0)} lb`,controlling.label+" controls."]];
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
  const activeMode = document.querySelector("[data-loan-mode].is-active")?.dataset.loanMode || "monthlyfixed";
  const payback = document.getElementById("l_payback")?.value || "month";
  const compound = document.getElementById("l_compound")?.value || "monthly";
  const P = V("l_amount"), annual = V("l_rate") / 100, rate = effectiveRate(annual, compound, payback);
  const n = loanTermPeriods("l_years", "l_months", payback);
  const payment = rate ? P * rate * Math.pow(1 + rate, n) / (Math.pow(1 + rate, n) - 1) : P / n;
  const total = payment * n, interest = total - P, payLabel = paybackLabel(payback);
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
  if (activeMode === "intheend") show(`<strong>${USD(due)} due at maturity</strong><br>${USD(dP)} principal; ${USD(dInterest)} compounded interest over ${F(dYears,2)} years.`);
  else if (activeMode === "fixedend") show(`<strong>${USD(received)} present value</strong><br>${USD(bDue)} predetermined due amount; ${USD(bInterest)} total discount or interest.`);
  else show(`<strong>${USD(payment)} / ${payLabel.toLowerCase()}</strong><br>Total of ${F(n,0)} payments: ${USD(total)}; total interest: ${USD(interest)}.`);
}

function setLoanMode(mode) {
  document.querySelectorAll("[data-loan-mode]").forEach(button => {
    const active = button.dataset.loanMode === mode;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });
  document.querySelectorAll(".loan-mode-input").forEach(panel => panel.classList.toggle("is-active", panel.id === mode));
  document.querySelectorAll(".loan-result-panel").forEach(panel => panel.classList.toggle("is-active", panel.id === mode + "r"));
  renderLoanPage();
}

document.addEventListener("click", event => {
  const tab = event.target.closest("[data-loan-mode]");
  if (tab) setLoanMode(tab.dataset.loanMode);
});

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
