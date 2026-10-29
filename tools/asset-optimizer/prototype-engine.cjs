// Isolated experiment: specializes only pure engine tests in the generic renderer.
// No helper removal, no production HTML rewrite, no coverage-driven deletion.
const fs=require('node:fs'),path=require('node:path'),acorn=require('acorn'),zlib=require('node:zlib');
function specialize(source,engine){
 if(!/^[a-z0-9_]+$/.test(engine))throw Error('Invalid engine');
 const ast=acorn.parse(source,{ecmaVersion:2020}),fn=ast.body.find(x=>x.type==='FunctionDeclaration'&&x.id.name==='renderGenericFromEngine');
 if(!fn||fn.params.length!==1||fn.params[0]?.type!=='Identifier')throw Error('Unsupported renderer boundary');const parameter=fn.params[0].name;
 function contains(node){if(!node||typeof node!=='object')return false;if(node.type==='Identifier')return node.name===parameter;return Object.values(node).some(x=>Array.isArray(x)?x.some(contains):contains(x))}
 function validate(node){if(!node||typeof node!=='object')return;if((node.type==='VariableDeclarator'&&contains(node.id))||((node.type==='AssignmentExpression'||node.type==='UpdateExpression')&&contains(node.left||node.argument))||(node.type==='CatchClause'&&contains(node.param))||node.type==='WithStatement')throw Error('Unsupported renderer parameter binding or mutation');for(const value of Object.values(node))if(Array.isArray(value))value.forEach(validate);else if(value&&typeof value==='object')validate(value)}validate(fn.body);
 const unknown=Symbol('unknown');let pruned=0;
 function test(n){if(n.type==='BinaryExpression'&&['===','!=='].includes(n.operator)){
 const a=n.left,b=n.right;if(a.type==='Identifier'&&a.name===parameter&&b.type==='Literal'&&typeof b.value==='string')return n.operator.includes('!')?engine!==b.value:engine===b.value;
 }return unknown}
 function render(n){if(['FunctionDeclaration','FunctionExpression','ArrowFunctionExpression'].includes(n.type))return source.slice(n.start,n.end);if(n.type==='IfStatement'){const value=test(n.test);if(value!==unknown){pruned++;return value?render(n.consequent):n.alternate?render(n.alternate):';'}}
 const children=[];for(const [key,value]of Object.entries(n)){if(['start','end'].includes(key))continue;for(const child of Array.isArray(value)?value:[value])if(child&&typeof child==='object'&&typeof child.start==='number')children.push(child)}
 let result=source.slice(n.start,n.end);for(const child of children.sort((a,b)=>b.start-a.start))result=result.slice(0,child.start-n.start)+render(child)+result.slice(child.end-n.start);return result}
 const guard=`if(${parameter}!==${JSON.stringify(engine)})throw new Error('Prototype renderer engine mismatch');`;
 const body=render(fn.body),output=source.slice(0,fn.body.start)+body.slice(0,1)+guard+body.slice(1)+source.slice(fn.body.end);
 acorn.parse(output,{ecmaVersion:2020});return{code:output,pruned,engine,sourceBytes:Buffer.byteLength(source),candidateBytes:Buffer.byteLength(output),sourceGzip:zlib.gzipSync(source).length,candidateGzip:zlib.gzipSync(output).length};
}
module.exports={specialize};
if(require.main===module){const [input,engine,output]=process.argv.slice(2);if(!input||!output||path.resolve(input)===path.resolve(output))throw Error('Separate input and output required');const result=specialize(fs.readFileSync(input,'utf8'),engine);fs.writeFileSync(output,result.code);const{code,...metrics}=result;console.log(JSON.stringify(metrics))}
