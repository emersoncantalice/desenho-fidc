// Testes de comportamento do editor em DOM simulado, sem dependências externas.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const initial=JSON.parse(fs.readFileSync('modelos/arquitetura-credito.json','utf8')).models;
const elements={},storage={},downloads=[],listeners={};
const svg={createSVGPoint(){return {x:0,y:0,matrixTransform(){return {x:this.x,y:this.y}}}},getScreenCTM(){return {inverse(){return {}}}},getBoundingClientRect(){return {left:0,top:0,width:1700,height:1340}}};
function element(id){return elements[id]??={value:'',checked:false,style:{},dataset:{},classList:{toggle(){}},setAttribute(name,value){this[name]=value},getBoundingClientRect(){return {left:0,top:0,width:1700,height:1000}},querySelector(){return svg},querySelectorAll(){return []},addEventListener(name,cb){listeners[id+':'+name]=cb},setPointerCapture(){},focus(){},click(){this.onclick?.()},files:[]}}
const scenarios=[0,1,2,3].map(i=>({...element('scenario'+i),dataset:{scenario:String(i)}}));
const context={console,Blob,setTimeout:fn=>fn(),confirm:()=>true,initialModels:initial,localStorage:{getItem:k=>storage[k],setItem:(k,v)=>storage[k]=v},URL:{createObjectURL:b=>{downloads.push(b);return 'blob:test'},revokeObjectURL(){}},window:{print(){}},document:{getElementById:element,querySelectorAll:()=>scenarios,createElement:()=>({click(){}}),addEventListener(name,cb){listeners["document:"+name]=cb}}};
vm.createContext(context);vm.runInContext(fs.readFileSync('modelos/roteamento.js','utf8')+'\n'+fs.readFileSync('modelos/renderizador.js','utf8')+'\n'+fs.readFileSync('modelos/editor.js','utf8'),context);
const run=s=>vm.runInContext(s,context);
async function test(){
 assert.equal(run('models.length'),4);assert.ok(element('canvas').innerHTML.includes('Kubernetes'));
 for(const m of initial.slice(0,2)){assert.ok(m.edges.some(e=>e.source==='proposal'&&e.target==='pdec2'&&e.label==='Solicita decisão'));assert.ok(m.edges.some(e=>e.source==='gcre'&&e.target==='pdec1'));}
 const modern=initial[3];assert.ok(!JSON.stringify(modern).includes('Sybase'));
 const newDesk=initial[2];
 assert.ok(newDesk.nodes.some(n=>n.id==='newdesk'&&n.change==='new'));
 assert.ok(newDesk.edges.some(e=>e.source==='credit'&&e.target==='pdec'));
 assert.ok(newDesk.edges.some(e=>e.source==='kafka'&&e.target==='newdesk'&&e.async_));
 assert.ok(!newDesk.nodes.some(n=>['EJB de crédito','Sybase','PTA'].includes(n.title)));
 assert.ok(!modern.nodes.some(n=>['legacy','gcre','pta','adapter','external'].includes(n.id)));
 assert.ok(modern.nodes.some(n=>n.id==='newdesk'));
 const migrated=run('validate([initialModels[0],initialModels[1],initialModels[3]])');
 assert.equal(migrated.length,4);assert.equal(migrated[2].name,initial[2].name);assert.equal(migrated[3].name,initial[3].name);
 assert.ok(modern.nodes.some(n=>n.id==='mysql'&&n.title==='MySQL cloud'));
 assert.ok(modern.edges.some(e=>e.source==='externalproposal'&&e.target==='proposalstore'&&!e.async_));
 assert.ok(modern.edges.some(e=>e.source==='externalproposal'&&e.target==='kafka'&&e.async_));
 assert.ok(modern.edges.some(e=>e.source==='externalproposal'&&e.target==='kafka'&&e.label==='Proposta persistida'));
 assert.ok(modern.edges.some(e=>e.source==='capturechannel'&&e.target==='externalproposal'&&e.label==='Solicita captura'));
 for(const legacy of initial.slice(0,2)){
  assert.ok(legacy.nodes.some(n=>n.id==='proposal'&&n.title==='EJB de crédito'&&n.detail.includes('Captura')));
  assert.ok(legacy.edges.some(e=>e.source==='origin'&&e.target==='proposal'&&e.label==='Solicita captura'));
 }
 assert.ok(modern.edges.some(e=>e.source==='creditprocessing'&&e.target==='pdec2'&&!e.async_));
 assert.ok(modern.edges.some(e=>e.source==='pdec2'&&e.target==='creditprocessing'&&!e.async_));
 assert.ok(!modern.edges.some(e=>(e.source==='pdec2'||e.target==='pdec2')&&e.async_));
 assert.ok(modern.edges.some(e=>e.source==='credit'&&e.target==='mysql'));
 const ejb=initial[1];assert.ok(ejb.nodes.some(n=>n.id==='origin'&&n.title==='Canal externo'));
 assert.ok(!ejb.nodes.some(n=>['external','externalhuman','adapter'].includes(n.id)));
 assert.ok(ejb.edges.some(e=>e.source==='proposal'&&e.target==='origin'&&e.async_));
 assert.ok(ejb.nodes.some(n=>n.id==='statusrule'&&n.detail.includes('NÃO ENCAMINHAR AO PAGAMENTO INTERNO')));
 assert.ok(!ejb.edges.some(e=>e.target==='payment'));
 assert.equal(ejb.nodes.find(n=>n.id==='statusrule').change,'new');
 assert.equal(ejb.nodes.find(n=>n.id==='proposal').change,'adapt');
 assert.ok(ejb.nodes.some(n=>n.id==='legacyrisk'&&n.detail.includes('Uso como transição')));
 const count=run('model().nodes.length');element('addbox').click();assert.equal(run('model().nodes.length'),count+1);
 element('title').value='Componente editado';element('detail').value='Java / JBoss';element('apply').click();assert.equal(run('object().title'),'Componente editado');
 const id=run('selected.id');listeners['canvas:pointerdown']({button:0,pointerId:1,clientX:100,clientY:100,target:{closest:q=>q==='[data-node]'?{dataset:{node:id}}:null}});const x=run('object().x');listeners['canvas:pointermove']({clientX:140,clientY:120});listeners['canvas:pointerup']();assert.equal(run('object().x'),x+40);
 element('addtext').click();assert.equal(run('object().kind'),'text');
 const edges=run('model().edges.length');element('connect').click();const pick=id=>listeners['canvas:pointerdown']({button:0,target:{closest:q=>q==='[data-node]'?{dataset:{node:id}}:null}});pick('proposal');pick('db');assert.equal(run('model().edges.length'),edges+1);
 element('async').checked=true;element('title').value='Evento';element('apply').click();assert.ok(run('object().async_'));assert.ok(element('canvas').innerHTML.includes('stroke-dasharray="1 6"'));
 element('save').click();const saved=JSON.parse(await downloads.at(-1).text());assert.equal(saved.models.length,4);assert.ok(saved.models[0].edges.some(e=>e.label==='Evento'));
 element('delete').click();assert.equal(run('model().edges.length'),edges);element('undo').click();assert.equal(run('model().edges.length'),edges+1);
 await element('file').onchange({target:{files:[{size:100,text:async()=>JSON.stringify(saved)}],value:'test'}});assert.equal(run('model().edges.length'),edges+1);
 element('svg').click();assert.ok((await downloads.at(-1).text()).startsWith('<svg'));
 scenarios[3].onclick();assert.ok(element('canvas').innerHTML.includes('Confluent Kafka'));
 const otherScenarios=run('JSON.stringify(models.slice(0,2))');
 element('addbox').click();element('title').value='Alteração antes de restaurar';element('apply').click();
 const edited=run('JSON.stringify(model())');element('connect').click();element('restore').click();
 assert.equal(run('JSON.stringify(model())'),JSON.stringify(initial[3]));
 assert.equal(run('JSON.stringify(models.slice(0,2))'),otherScenarios);
 assert.equal(run('connecting'),false);assert.equal(run('selected'),null);
 assert.equal(JSON.parse(storage['architecture-credit-editor-v4']).models[3].nodes.length,initial[3].nodes.length);
 element('undo').click();assert.equal(run('JSON.stringify(model())'),edited);
 // Exercita os atalhos reais, inclusive o isolamento da edição de texto.
 function key(k,target={tagName:'DIV'},extra={}){let prevented=false;listeners['document:keydown']({key:k,ctrlKey:true,target,preventDefault(){prevented=true},...extra});return prevented}
 run("select('node','credit')");const original=run('JSON.stringify(object())');
 const beforePaste=run('JSON.stringify(model())');assert.equal(key('c'),true);
 const depth=run('histories[current].length');assert.equal(key('v'),true);
 assert.equal(run('histories[current].length'),depth+1);
 const pastedId=run('selected.id');assert.notEqual(pastedId,'credit');assert.equal(run('object().title'),JSON.parse(original).title);
 assert.equal(run('object().x'),JSON.parse(original).x+24);
 assert.equal(key('v'),true);assert.notEqual(run('selected.id'),pastedId);assert.equal(run('object().x'),JSON.parse(original).x+48);
 assert.equal(key('z'),true);assert.equal(key('z'),true);assert.equal(run('JSON.stringify(model())'),beforePaste);
 for(const target of [{tagName:'INPUT'},{tagName:'TEXTAREA'},{tagName:'SELECT'},{tagName:'DIV',isContentEditable:true}]){
  for(const k of ['c','v','z'])assert.equal(key(k,target),false);
 }
 assert.equal(run('JSON.stringify(model())'),beforePaste);
 assert.equal(key('v',{tagName:'DIV'},{ctrlKey:false,metaKey:true}),true);key('z');
 scenarios[1].onclick();const legacyBefore=run('JSON.stringify(model())');key('v');assert.equal(run('object().title'),JSON.parse(original).title);key('z');assert.equal(run('JSON.stringify(model())'),legacyBefore);
 run("select('edge','returnchannel')");key('c');const edgeCount=run('model().edges.length');key('v');assert.equal(run('model().edges.length'),edgeCount+1);assert.equal(run('object().async_'),true);key('z');
 scenarios[3].onclick();const blockedBefore=run('JSON.stringify(model())');key('v');assert.equal(run('JSON.stringify(model())'),blockedBefore);
 run("select('node','legend')");key('c');key('v');assert.equal(run('object().kind'),'text');key('z');
 assert.throws(()=>run('validate([{name:"invalid"}])'));
 const beforeFullscreen=run('JSON.stringify(models)');
 run("select('node','credit')");element('change').value='adapt';element('apply').click();
 assert.equal(run('object().change'),'adapt');assert.ok(element('canvas').innerHTML.includes('class="node change-adapt"'));
 element('undo').click();assert.equal(run('JSON.stringify(models)'),beforeFullscreen);
 context.document.documentElement={requestFullscreen:async()=>{context.document.fullscreenElement=context.document.documentElement;listeners['document:fullscreenchange']()}};
 context.document.exitFullscreen=async()=>{context.document.fullscreenElement=null;listeners['document:fullscreenchange']()};
 assert.equal(element('fullscreen')['aria-pressed'],'false');
 await element('fullscreen').onclick();assert.equal(element('fullscreen')['aria-pressed'],'true');assert.ok(element('fullscreen').title.includes('Esc'));
 await element('fullscreen').onclick();assert.equal(element('fullscreen')['aria-pressed'],'false');
 await element('fullscreen').onclick();context.document.fullscreenElement=null;listeners['document:fullscreenchange']();assert.equal(element('fullscreen')['aria-pressed'],'false');
 context.document.documentElement.requestFullscreen=async()=>{throw Error('denied')};await element('fullscreen').onclick();assert.equal(element('fullscreen').disabled,false);assert.ok(element('message').textContent.includes('F11'));
 delete context.document.documentElement.requestFullscreen;await element('fullscreen').onclick();assert.ok(element('message').textContent.includes('F11'));
 assert.equal(run('JSON.stringify(models)'),beforeFullscreen);
 console.log('OK: tela cheia, saída pelo botão/Esc, estado do ícone e tratamento de indisponibilidade, sem alterar os desenhos.');
 console.log('OK: Ctrl+C/V/Z, IDs novos, deslocamento, colagens repetidas, texto e ligação, cópia entre cenários, histórico e edição nativa de texto.');
 console.log('OK: cenários, direção das chamadas, criação, edição, movimento, ligação pontilhada, exclusão/desfazer, salvamento/reabertura JSON e exportação SVG.');
}
test().catch(err=>{console.error(err);process.exitCode=1});
