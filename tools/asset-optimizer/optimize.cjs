const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),zlib=require('node:zlib'),{minify}=require('terser');
const hash=value=>crypto.createHash('sha256').update(value).digest('hex').slice(0,16);
const OPTIONS={ecma:2020,module:false,toplevel:false,compress:false,mangle:{toplevel:false,properties:false},keep_fnames:true,format:{comments:'some'}};
function htmlFiles(root){const files=[];for(const item of fs.readdirSync(root,{withFileTypes:true})){const file=path.join(root,item.name);if(item.isDirectory())files.push(...htmlFiles(file));else if(item.isFile()&&item.name.endsWith('.html'))files.push(file)}return files}
async function optimize(root){
 root=path.resolve(root);const asset=path.join(root,'assets','calculator.js');if(!fs.existsSync(path.join(root,'index.html'))||!fs.existsSync(asset))throw Error('Expected a generated site root with index.html and assets/calculator.js.');
 const source=fs.readFileSync(asset),oldVersion=hash(source),result=await minify(source.toString('utf8'),OPTIONS);if(!result.code)throw Error('Optimizer produced no JavaScript.');const output=Buffer.from(result.code+'\n','utf8'),version=hash(output);if(output.length>source.length)throw Error('Optimization would enlarge the calculator bundle.');
 let references=0;const edits=[];
 for(const file of htmlFiles(root)){const html=fs.readFileSync(file,'utf8');const updated=html.replace(/<script\b[^>]*\bsrc="([^"]+)"[^>]*>/gi,(tag,src)=>{const url=new URL(src,'https://asset.invalid');if(!url.pathname.endsWith('/assets/calculator.js'))return tag;const versions=url.searchParams.getAll('v');if(versions.length!==1||versions[0]!==oldVersion)throw Error(`Stale calculator reference in ${file}: ${src}`);if(url.searchParams.size!==1||url.hash)throw Error(`Unexpected calculator query or fragment in ${file}`);references++;return tag.replace(src,src.replace(/([?&]v=)[^&]+/,(_,prefix)=>prefix+version))});if(updated!==html)edits.push([file,updated]);}
 if(!references)throw Error('No versioned calculator references found; nothing was written.');
 const variants=[];
 for(const spec of require('./engine-assets.json')){const page=path.join(root,spec.slug,'index.html');if(!fs.existsSync(page))continue;if(!fs.readFileSync(page,'utf8').includes('data-engine="'+spec.engine+'"'))throw Error(spec.slug+' engine does not match delivery registry');
  try{const candidate=require('./prototype-engine.cjs').specialize(source.toString('utf8'),spec.engine),minified=await minify(candidate.code,OPTIONS),bytes=Buffer.from(minified.code+'\n');if(!minified.code||bytes.length>=output.length)throw Error('No smaller candidate');const fingerprint=hash(bytes);let selected=0;for(const edit of edits)if(edit[0]===page)edit[1]=edit[1].replace(/\/assets\/calculator\.js\?v=[a-f0-9]+/g,()=>{selected++;return '/assets/'+spec.asset+'?v='+fingerprint});if(selected!==1)throw Error('Expected exactly one runtime reference');variants.push({...spec,bytes,fingerprint,pruned:candidate.pruned});}catch(error){throw Error(spec.slug+' specialization failed before publishing assets: '+error.message)}
 }
 const specialized=variants.find(x=>x.slug==='401k-calculator');
 fs.writeFileSync(asset,output);for(const variant of variants)fs.writeFileSync(path.join(root,'assets',variant.asset),variant.bytes);for(const [file,html] of edits)fs.writeFileSync(file,html,'utf8');
 return{sourceBytes:source.length,optimizedBytes:output.length,sourceGzipBytes:zlib.gzipSync(source,{level:9}).length,optimizedGzipBytes:zlib.gzipSync(output,{level:9}).length,sourceVersion:oldVersion,version,references,specialized:specialized?{version:specialized.fingerprint,bytes:specialized.bytes.length,pruned:specialized.pruned}:null,compress:false,globalNamesPreserved:true,propertyNamesPreserved:true};
}
module.exports={optimize,OPTIONS};
if(require.main===module)optimize(process.argv[2]||'dist').then(result=>console.log(JSON.stringify(result))).catch(error=>{console.error(error);process.exitCode=1});
