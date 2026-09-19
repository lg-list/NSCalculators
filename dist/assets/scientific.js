(function(){
  const input=document.getElementById('sciExpression'),output=document.getElementById('sciResult'),status=document.getElementById('sciStatus'),historyList=document.getElementById('sciHistory');
  if(!input||!output||!status||!historyList||!window.math)return;
  let angleMode='deg',answer=0,memory=0,lastNumeric=12.25,history=[];
  const allowed=new Set(['sqrt','sin','cos','tan','asin','acos','atan','log','ln','abs','floor','ceil','round','exp','factorial','min','max','mod','pi','e','ans']);
  const toRadians=value=>angleMode==='deg'?value*Math.PI/180:value;
  const fromRadians=value=>angleMode==='deg'?value*180/Math.PI:value;
  const scope=()=>new Map([
    ['ans',answer],['nsSin',value=>Math.sin(toRadians(value))],['nsCos',value=>Math.cos(toRadians(value))],['nsTan',value=>Math.tan(toRadians(value))],
    ['nsAsin',value=>fromRadians(Math.asin(value))],['nsAcos',value=>fromRadians(Math.acos(value))],['nsAtan',value=>fromRadians(Math.atan(value))],
    ['log',value=>Math.log10(value)],['ln',value=>Math.log(value)]
  ]);
  function normalized(raw){
    if(!raw.trim())throw new Error('Enter an expression.');
    if(raw.length>240)throw new Error('Keep the expression under 240 characters.');
    if(!/^[0-9A-Za-z+\-*/^().,%!\s]+$/.test(raw)||/[;=\[\]{}'"_:?]/.test(raw))throw new Error('Use numbers, supported functions, and arithmetic operators only.');
    const identifiers=raw.match(/[A-Za-z]+/g)||[];
    const unsupported=identifiers.find(name=>!allowed.has(name.toLowerCase())&&!/^e\d+$/i.test(name));
    if(unsupported)throw new Error(`${unsupported} is not a supported function or constant.`);
    let expression=raw.replace(/\bAns\b/gi,'ans');
    for(let pass=0;pass<4;pass++)expression=expression.replace(/(\d+(?:\.\d+)?|\([^()]*\))%/g,'($1/100)');
    expression=expression.replace(/\basin\s*\(/gi,'nsAsin(').replace(/\bacos\s*\(/gi,'nsAcos(').replace(/\batan\s*\(/gi,'nsAtan(')
      .replace(/\bsin\s*\(/gi,'nsSin(').replace(/\bcos\s*\(/gi,'nsCos(').replace(/\btan\s*\(/gi,'nsTan(');
    return expression;
  }
  function displayValue(value){
    if(typeof value==='number'){
      if(!Number.isFinite(value))throw new Error('The result is outside the supported numeric range.');
      return math.format(value,{precision:14,lowerExp:-9,upperExp:15});
    }
    if(value&&typeof value.toString==='function')return math.format(value,{precision:14});
    throw new Error('The expression did not return a numeric result.');
  }
  function renderHistory(){
    historyList.innerHTML=history.length?history.map((item,index)=>`<li><button type="button" data-history-index="${index}"><span>${item.expression}</span><strong>${item.result}</strong></button></li>`).join(''):'<li class="sci-history-empty">Your calculations will appear here.</li>';
  }
  function run(){
    try{
      const expression=input.value.trim(),value=math.evaluate(normalized(expression),scope()),formatted=displayValue(value);
      output.textContent=formatted;status.textContent=`Calculated in ${angleMode==='deg'?'degree':'radian'} mode`;answer=value;lastNumeric=typeof value==='number'?value:lastNumeric;
      history=[{expression,result:formatted},...history.filter(item=>item.expression!==expression)].slice(0,8);renderHistory();
    }catch(error){output.textContent='Check expression';status.textContent=error&&error.message?error.message:'The expression could not be evaluated.'}
  }
  function insert(value){
    const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;
    input.value=input.value.slice(0,start)+value+input.value.slice(end);const caret=start+value.length;input.focus();input.setSelectionRange(caret,caret);
  }
  function wrap(prefix,suffix=')'){
    const expression=input.value.trim()||'0';input.value=`${prefix}${expression}${suffix}`;input.focus();input.setSelectionRange(input.value.length,input.value.length);
  }
  function setMode(mode){
    angleMode=mode;document.querySelectorAll('[data-angle-mode]').forEach(button=>{const active=button.dataset.angleMode===mode;button.classList.toggle('is-active',active);button.setAttribute('aria-pressed',active?'true':'false')});status.textContent=`Ready in ${mode==='deg'?'degree':'radian'} mode`;
  }
  document.addEventListener('click',event=>{
    const modeButton=event.target.closest('[data-angle-mode]');if(modeButton){setMode(modeButton.dataset.angleMode);return}
    const historyButton=event.target.closest('[data-history-index]');if(historyButton){const item=history[Number(historyButton.dataset.historyIndex)];if(item){input.value=item.expression;input.focus()}return}
    const button=event.target.closest('[data-sci-action]');if(!button)return;const action=button.dataset.sciAction,value=button.dataset.sciValue||'';
    if(action==='insert')insert(value);else if(action==='calculate')run();else if(action==='clear'){input.value='';output.textContent='0';status.textContent=`Ready in ${angleMode==='deg'?'degree':'radian'} mode`;input.focus()}
    else if(action==='backspace'){const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;if(start!==end)input.value=input.value.slice(0,start)+input.value.slice(end);else if(start>0)input.value=input.value.slice(0,start-1)+input.value.slice(end);const caret=Math.max(0,start-(start===end?1:0));input.focus();input.setSelectionRange(caret,caret)}
    else if(action==='square')wrap('(',')^2');else if(action==='reciprocal')wrap('1/(',')');else if(action==='negate')wrap('-(',')');else if(action==='percent')wrap('(',')%');
    else if(action==='memory-clear'){memory=0;status.textContent='Memory cleared'}else if(action==='memory-recall')insert(math.format(memory,{precision:14}));else if(action==='memory-add'){memory+=Number(lastNumeric)||0;status.textContent=`Memory: ${math.format(memory,{precision:14})}`}else if(action==='memory-subtract'){memory-=Number(lastNumeric)||0;status.textContent=`Memory: ${math.format(memory,{precision:14})}`}else if(action==='history-clear'){history=[];renderHistory()}
  });
  input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();run()}else if(event.key==='Escape'){event.preventDefault();input.value='';output.textContent='0';status.textContent=`Ready in ${angleMode==='deg'?'degree':'radian'} mode`}});
  setMode('deg');
})();
