(function(){
  const input=document.getElementById('basicExpression'),output=document.getElementById('basicResult'),status=document.getElementById('basicStatus'),memoryLabel=document.getElementById('basicMemory'),historyList=document.getElementById('basicHistory');
  if(!input||!output||!status||!memoryLabel||!historyList||!window.math)return;
  let answer=0,memory=0,history=[],afterResult=false;
  function format(value){
    if(typeof value!=='number'||!Number.isFinite(value))throw new Error('The result is outside the supported numeric range.');
    return math.format(value,{precision:14,lowerExp:-9,upperExp:15});
  }
  function normalize(raw){
    if(!raw.trim())throw new Error('Enter a calculation.');
    if(raw.length>180)throw new Error('Keep the expression under 180 characters.');
    if(!/^[0-9A-Za-z+\-*/^().,%\s]+$/.test(raw)||/[;=\[\]{}'"_:?]/.test(raw))throw new Error('Use numbers and the calculator keys only.');
    const identifiers=raw.match(/[A-Za-z]+/g)||[];
    const unsupported=identifiers.find(name=>!['sqrt','ans','e'].includes(name.toLowerCase()));
    if(unsupported)throw new Error(`${unsupported} is not supported by this basic calculator.`);
    let expression=raw.replace(/\bAns\b/gi,'ans');
    for(let pass=0;pass<4;pass++)expression=expression.replace(/(\d+(?:\.\d+)?(?:e[+\-]?\d+)?|\([^()]*\))%/gi,'($1/100)');
    return expression;
  }
  function renderHistory(){
    historyList.innerHTML=history.length?history.map((item,index)=>`<li><button type="button" data-basic-history="${index}"><span>${item.expression}</span><strong>${item.result}</strong></button></li>`).join(''):'<li class="basic-history-empty">Your calculations will appear here.</li>';
  }
  function updateMemory(message){
    memoryLabel.textContent=memory===0?'Memory: empty':`M = ${format(memory)}`;
    if(message)status.textContent=message;
  }
  function run(){
    try{
      const expression=input.value.trim(),value=math.evaluate(normalize(expression),new Map([['ans',answer]]));
      if(typeof value!=='number')throw new Error('This expression does not have a real-number result.');
      const result=format(value);output.textContent=result;status.textContent='Calculated';answer=value;afterResult=true;
      history=[{expression,result},...history.filter(item=>item.expression!==expression)].slice(0,10);renderHistory();
    }catch(error){output.textContent='Error';status.textContent=error&&error.message?error.message:'Check the expression.';afterResult=false}
  }
  function insert(value){
    const isNumber=/^(?:\d*\.?\d+(?:e[+\-]?\d+)?)$/i.test(value);
    if(afterResult&&isNumber){input.value='';afterResult=false}
    else if(afterResult&&/^[+\-*/]$/.test(value)){input.value=format(answer);afterResult=false}
    const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;
    input.value=input.value.slice(0,start)+value+input.value.slice(end);const caret=start+value.length;input.focus();input.setSelectionRange(caret,caret);status.textContent='Ready';
  }
  function wrap(prefix,suffix=')'){
    const expression=input.value.trim()||(Number.isFinite(answer)?format(answer):'0');input.value=`${prefix}${expression}${suffix}`;afterResult=false;input.focus();input.setSelectionRange(input.value.length,input.value.length);
  }
  function applyPercent(){
    const raw=input.value.trim();if(!raw){input.value='0';return}
    const match=raw.match(/^(.*)([+\-*/])\s*(\d*\.?\d+(?:e[+\-]?\d+)?)$/i);
    if(match&&match[1].trim()){
      const base=match[1].trim(),operator=match[2],percent=match[3];
      input.value=(operator==='+'||operator==='-')?`${base}${operator}(${base})*(${percent}/100)`: `${base}${operator}(${percent}/100)`;
    }else input.value=`(${raw})/100`;
    afterResult=false;input.focus();input.setSelectionRange(input.value.length,input.value.length);status.textContent='Percent applied';
  }
  document.addEventListener('click',event=>{
    const historyButton=event.target.closest('[data-basic-history]');
    if(historyButton){const item=history[Number(historyButton.dataset.basicHistory)];if(item){input.value=item.expression;afterResult=false;input.focus()}return}
    const button=event.target.closest('[data-basic-action]');if(!button)return;
    const action=button.dataset.basicAction,value=button.dataset.basicValue||'';
    if(action==='insert')insert(value);else if(action==='calculate')run();else if(action==='clear'){input.value='';output.textContent='0';status.textContent='Ready';afterResult=false;input.focus()}
    else if(action==='backspace'){const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;if(start!==end)input.value=input.value.slice(0,start)+input.value.slice(end);else if(start>0)input.value=input.value.slice(0,start-1)+input.value.slice(end);const caret=Math.max(0,start-(start===end?1:0));afterResult=false;input.focus();input.setSelectionRange(caret,caret)}
    else if(action==='root')wrap('sqrt(',')');else if(action==='square')wrap('(',')^2');else if(action==='reciprocal')wrap('1/(',')');else if(action==='negate')wrap('-(',')');else if(action==='percent')applyPercent();else if(action==='answer')insert(format(answer));
    else if(action==='memory-clear'){memory=0;updateMemory('Memory cleared')}else if(action==='memory-recall')insert(format(memory));else if(action==='memory-add'){memory+=answer;updateMemory('Answer added to memory')}else if(action==='memory-subtract'){memory-=answer;updateMemory('Answer subtracted from memory')}else if(action==='history-clear'){history=[];renderHistory();status.textContent='History cleared'}
  });
  input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();run()}else if(event.key==='Escape'){event.preventDefault();input.value='';output.textContent='0';status.textContent='Ready';afterResult=false}});
  updateMemory();
})();
