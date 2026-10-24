const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const values={sample_target:'proportion',sample_confidence:'1.96',sample_population:'0',sample_margin:'5',sample_proportion:'50',sample_sd:'20',sample_mean_margin:'10'};
const context={document:{addEventListener(){},querySelector(){return null},querySelectorAll(){return []},getElementById(id){return id==='genericSummary'?{}:id in values?{value:values[id]}:null}},window:{addEventListener(){}},console};
vm.createContext(context);vm.runInContext(fs.readFileSync(process.argv[2]||'dist/assets/calculator.js','utf8'),context);
const base={target:'proportion',z:1.96,population:0,margin:5,proportion:50,sd:20};let checks=0;
function verify(input,required){const p=context.sampleSizeAmounts({...base,...input});assert.equal(p.valid,true,p.message);assert.equal(p.required,required);checks++;return p;}
verify({},385);verify({population:1000},278);verify({population:1},1);verify({z:1.645},271);verify({z:2.576},664);
verify({target:'mean',sd:20,margin:10},16);verify({target:'mean',sd:25,margin:5},97);verify({target:'mean',sd:12,margin:2},139);verify({target:'mean',z:1.645,sd:10,margin:2},68);verify({target:'mean',z:2.576,sd:10,margin:2},166);
verify({target:'mean',sd:1e-10,margin:1e-9},1);verify({target:'mean',sd:1e200,margin:1e200},4);
const ignored=verify({target:'mean',population:NaN,proportion:NaN,margin:10},16);assert.equal(ignored.adjusted,false);assert.equal(ignored.population,0);
for(const z of [1.645,1.96,2.576])for(const scale of [.001,1,1000]){verify({target:'mean',z,sd:12*scale,margin:2*scale},Math.ceil((z*6)**2));}
for(const key of ['sd','margin'])for(const value of [0,-1,NaN,Infinity,-Infinity,null,undefined,'20']){assert.equal(context.sampleSizeAmounts({...base,target:'mean',margin:10,[key]:value}).valid,false);checks++;}
for(const input of [{target:'invalid'},{z:0},{z:2},{population:NaN},{population:1.5},{population:-1},{population:Number.MAX_SAFE_INTEGER+1},{margin:0},{margin:50.1},{proportion:0},{proportion:100},{target:'mean',sd:1e308,margin:1e-308},{target:'mean',sd:1e-308,margin:1e308},{target:'mean',sd:1e10,margin:1}]){assert.equal(context.sampleSizeAmounts({...base,...input}).valid,false);checks++;}
assert.equal(context.sampleSizeProjection().required,385);checks++;
values.sample_target='mean';values.sample_population='';values.sample_proportion='';assert.equal(context.sampleSizeProjection().required,16);checks++;
for(const id of ['sample_sd','sample_mean_margin','sample_confidence']){const initial=values[id];for(const raw of ['', ' ', 'Infinity','abc']){values[id]=raw;assert.equal(context.sampleSizeProjection().valid,false);checks++;}values[id]=initial;}
let captured;context.renderGeneric=(cards,bars,rows)=>{captured={cards,bars,rows}};context.renderGenericFromEngine('sample_size_advanced');assert.equal(captured.cards[0][1],'16');assert.equal(captured.bars.length,0);assert.ok(captured.rows.some(row=>row.includes('Not applied')));checks++;
values.sample_sd='';context.renderGenericFromEngine('sample_size_advanced');assert.equal(captured.cards[0][1],'Check inputs');assert.equal(captured.bars.length,0);checks++;
assert.equal(context.sampleMeasure(1e-12),'1e-12');checks++;
console.log(`${checks} proportion and mean sample-size checks passed`);
