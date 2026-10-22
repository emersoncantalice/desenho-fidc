const $=id=>document.getElementById(id),copy=v=>JSON.parse(JSON.stringify(v));
let models=copy(initialModels),current=0,selected=null,scale=100,connecting=false,source=null,drag=null;
let diagramClipboard=null,pasteCount=0;
const storageKey='architecture-credit-editor-v4',histories=initialModels.map(()=>[]);
function validate(list){
 if(!Array.isArray(list)||![3,4].includes(list.length))throw Error('O projeto deve conter quatro cenários (ou três de uma versão anterior).');
 for(const m of list){
  if(typeof m.name!=='string'||!Number.isFinite(m.width)||!Number.isFinite(m.height)||m.width<100||m.height<100||m.width>20000||m.height>20000||!Array.isArray(m.nodes)||!Array.isArray(m.edges)||m.nodes.length>2000||m.edges.length>4000)throw Error('Estrutura de projeto inválida.');
  const ids=new Set();for(const n of m.nodes){if(typeof n.id!=='string'||ids.has(n.id)||typeof n.title!=='string'||typeof n.detail!=='string'||!['component','actor','database','text','heading','group','note'].includes(n.kind)||!['x','y','w','h'].every(k=>Number.isFinite(n[k]))||n.w<1||n.h<1)throw Error('Elemento inválido.');if(n.change!=null&&!['new','adapt','legacy','existing'].includes(n.change))throw Error('Classificação de escopo inválida.');ids.add(n.id)}
  const edgeIds=new Set();for(const e of m.edges){if(typeof e.id!=='string'||edgeIds.has(e.id)||!ids.has(e.source)||!ids.has(e.target)||typeof e.label!=='string'||typeof e.async_!=='boolean'||!['left','right','top','bottom'].includes(e.sourceSide)||!['left','right','top','bottom'].includes(e.targetSide)||(e.via!=null&&!Number.isFinite(e.via)))throw Error('Ligação inválida.');edgeIds.add(e.id)}
 }return list.length===3?[list[0],list[1],copy(initialModels[2]),list[2]]:list;
}
try{const saved=localStorage.getItem(storageKey);if(saved)models=validate(JSON.parse(saved).models)}catch{}
let previousDraft=null;
try{const previous=localStorage.getItem('architecture-credit-editor-v3')||localStorage.getItem('architecture-credit-editor-v2');if(previous)previousDraft=validate(JSON.parse(previous).models)}catch{}
$('previous').hidden=!previousDraft;
$('previous').onclick=()=>download(JSON.stringify({format:'arquitetura-credito',version:1,models:previousDraft},null,2),'application/json','arquitetura-rascunho-anterior.json');
function model(){return models[current]}
function object(){return selected?(selected.type==='node'?model().nodes:model().edges).find(n=>n.id===selected.id):null}
function checkpoint(){histories[current].push(copy(model()));if(histories[current].length>60)histories[current].shift()}
function persist(){try{localStorage.setItem(storageKey,JSON.stringify({version:1,models}));$('status').textContent='Rascunho salvo no navegador'}catch{$('status').textContent='Exporte o projeto para salvar'}}
function draw(){
 $('canvas').innerHTML=render(model());$('canvas').style.width=scale+'%';
 document.querySelectorAll('[data-scenario]').forEach(b=>b.classList.toggle('active',Number(b.dataset.scenario)===current));
 if(selected){for(const el of $('canvas').querySelectorAll(selected.type==='node'?'[data-node]':'[data-edge]'))if(el.getAttribute('data-'+selected.type)===selected.id)el.classList.add('selected')}
}
function inspect(){const o=object();$('props').hidden=!o;if(!o)return;const isNode=selected.type==='node';$('nodeprops').hidden=!isNode;$('edgeprops').hidden=isNode;$('title').value=isNode?o.title:o.label;if(isNode){$('change').value=o.change??'';$('detail').value=o.detail;$('kind').value=o.kind==='note'?'component':o.kind;$('width').value=o.w;$('height').value=o.h}else{$('async').checked=o.async_;$('sourceSide').value=o.sourceSide;$('targetSide').value=o.targetSide;$('via').value=o.via??''}}
function select(type,id){selected={type,id};draw();inspect()}
function applyProperties(){const o=object();if(!o)return;const before=JSON.stringify(o);const changed=copy(o);if(selected.type==='node'){changed.title=$('title').value;changed.detail=$('detail').value;changed.kind=$('kind').value;if($('change').value)changed.change=$('change').value;else delete changed.change;changed.w=Math.max(60,Math.min(4000,Number($('width').value)||270));changed.h=Math.max(30,Math.min(4000,Number($('height').value)||94))}else{changed.label=$('title').value;changed.async_=$('async').checked;changed.sourceSide=$('sourceSide').value;changed.targetSide=$('targetSide').value;changed.via=$('via').value===''?null:Number($('via').value)}if(before!==JSON.stringify(changed)){checkpoint();Object.assign(o,changed);draw();persist()}}
function point(event){const svg=$('canvas').querySelector('svg'),p=svg.createSVGPoint();p.x=event.clientX;p.y=event.clientY;return p.matrixTransform(svg.getScreenCTM().inverse())}
function uid(prefix){return prefix+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8)}
function copySelected(){
 if(!object())return false;
 applyProperties();diagramClipboard={type:selected.type,item:copy(object()),scenario:current};pasteCount=0;
 $('message').textContent='Elemento copiado. Use Ctrl+V para colar no editor.';return true;
}
function pasteSelected(){
 if(!diagramClipboard)return false;
 const {type,item,scenario}=diagramClipboard;
 if(type==='edge'&&(scenario!==current||!model().nodes.some(n=>n.id===item.source)||!model().nodes.some(n=>n.id===item.target))){
  $('message').textContent='Cole esta ligação no cenário de origem, com os componentes de origem e destino presentes.';return true;
 }
 applyProperties();checkpoint();pasteCount++;
 const cloned=copy(item);cloned.id=uid(type);const offset=24*pasteCount;
 if(type==='node'){
  cloned.x=Math.max(0,Math.min(model().width-cloned.w,item.x+offset));
  cloned.y=Math.max(0,Math.min(model().height-cloned.h,item.y+offset));
  model().nodes.push(cloned);
 }else{
  if(cloned.via!=null)cloned.via+=offset;
  model().edges.push(cloned);
 }
 connecting=false;source=null;drag=null;$('connect').textContent='+ Ligação';
 select(type,cloned.id);persist();$('canvas').focus({preventScroll:true});
 $('message').textContent='Elemento colado. Use Ctrl+Z para desfazer.';return true;
}
$('canvas').addEventListener('pointerdown',ev=>{
 if(ev.button!==0)return;const n=ev.target.closest('[data-node]'),e=ev.target.closest('[data-edge]');
 $('canvas').focus({preventScroll:true});
 if(connecting){if(!n||['group','heading','text'].includes(model().nodes.find(v=>v.id===n.dataset.node).kind))return;if(!source){source=n.dataset.node;$('message').textContent='Selecione o componente de destino.';select('node',source)}else{checkpoint();const id=uid('edge');model().edges.push({id,source,target:n.dataset.node,label:'Nova ligação',sourceSide:'right',targetSide:'left',async_:false,via:null});connecting=false;source=null;$('connect').textContent='+ Ligação';$('message').textContent='Edite o rótulo e marque “Assíncrona” quando aplicável.';select('edge',id);persist()}return}
 if(n){select('node',n.dataset.node);const o=object(),p=point(ev);drag={id:o.id,px:p.x,py:p.y,x:o.x,y:o.y,moved:false};$('canvas').setPointerCapture(ev.pointerId)}else if(e){select('edge',e.dataset.edge)}else{selected=null;draw();inspect()}
});
$('canvas').addEventListener('pointermove',ev=>{if(!drag)return;const p=point(ev),dx=p.x-drag.px,dy=p.y-drag.py;if(!drag.moved&&Math.abs(dx)+Math.abs(dy)<3)return;if(!drag.moved){checkpoint();drag.moved=true}const o=model().nodes.find(n=>n.id===drag.id);o.x=Math.round(Math.max(0,Math.min(model().width-o.w,drag.x+dx)));o.y=Math.round(Math.max(0,Math.min(model().height-o.h,drag.y+dy)));draw()});
function endDrag(){if(drag?.moved)persist();drag=null}
$('canvas').addEventListener('pointerup',endDrag);$('canvas').addEventListener('pointercancel',endDrag);
function add(kind){applyProperties();checkpoint();const svg=$('canvas').querySelector('svg'),r=svg.getBoundingClientRect(),vp=$('viewport').getBoundingClientRect();const x=Math.max(40,Math.min(model().width-350,(vp.left+vp.width/2-r.left)/r.width*model().width-150)),y=Math.max(100,Math.min(model().height-150,(vp.top+vp.height/2-r.top)/r.height*model().height));const id=uid('node');model().nodes.push({id,x,y,w:300,h:100,title:kind==='text'?'Novo texto':'Novo componente',detail:kind==='text'?'':'Tecnologia / ambiente',kind});select('node',id);persist();$('title').focus()}
$('addbox').onclick=()=>add('component');$('addtext').onclick=()=>add('text');
$('connect').onclick=()=>{connecting=!connecting;source=null;$('connect').textContent=connecting?'Cancelar ligação':'+ Ligação';$('message').textContent=connecting?'Selecione a origem e depois o destino da ligação.':''};
$('apply').onclick=applyProperties;
$('delete').onclick=()=>{if(!object())return;checkpoint();if(selected.type==='node'){model().nodes=model().nodes.filter(n=>n.id!==selected.id);model().edges=model().edges.filter(e=>e.source!==selected.id&&e.target!==selected.id)}else model().edges=model().edges.filter(e=>e.id!==selected.id);selected=null;draw();inspect();persist()};
$('undo').onclick=()=>{if(!histories[current].length)return;models[current]=histories[current].pop();selected=null;drag=null;connecting=false;source=null;$('connect').textContent='+ Ligação';draw();inspect();persist();$('message').textContent='Última alteração desfeita.'};
$('restore').onclick=()=>{
 applyProperties();checkpoint();models[current]=copy(initialModels[current]);
 selected=null;connecting=false;source=null;drag=null;
 $('connect').textContent='+ Ligação';draw();inspect();zoom(100);persist();
 $('message').textContent='Desenho inicial restaurado neste cenário. Use Desfazer para recuperar suas alterações.';
};
function zoom(v){scale=Math.max(35,Math.min(250,v));$('zoom').textContent=scale+'%';$('canvas').style.width=scale+'%'}
$('minus').onclick=()=>zoom(scale-15);$('plus').onclick=()=>zoom(scale+15);$('fit').onclick=()=>zoom(100);
document.querySelectorAll('[data-scenario]').forEach(b=>b.onclick=()=>{applyProperties();current=Number(b.dataset.scenario);selected=null;connecting=false;source=null;$('connect').textContent='+ Ligação';$('message').textContent='';draw();inspect();zoom(100)});
function download(content,mime,name){const url=URL.createObjectURL(new Blob([content],{type:mime})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000)}
$('save').onclick=()=>{applyProperties();download(JSON.stringify({format:'arquitetura-credito',version:1,models},null,2),'application/json','arquitetura-credito.json');$('status').textContent='Projeto exportado em JSON'};
$('svg').onclick=()=>{applyProperties();download(render(model()),'image/svg+xml',model().name.toLowerCase().replaceAll(' ','-')+'.svg')};
$('open').onclick=()=>$('file').click();
$('file').onchange=async ev=>{const file=ev.target.files[0];if(!file)return;try{if(file.size>10000000)throw Error('Arquivo maior que 10 MB.');const p=JSON.parse(await file.text());if(p.format!=='arquitetura-credito'||p.version!==1)throw Error('Formato de projeto não reconhecido.');const incoming=validate(p.models);if(!confirm('Abrir este projeto substituirá os quatro cenários atuais. Exporte antes se precisar manter uma cópia. Continuar?'))return;models=copy(incoming);diagramClipboard=null;pasteCount=0;histories.forEach(h=>h.length=0);current=0;selected=null;draw();inspect();persist();$('message').textContent='Projeto carregado. Os elementos continuam editáveis.'}catch(err){$('message').textContent='Não foi possível abrir: '+err.message}finally{ev.target.value=''}};
$('print').onclick=()=>{applyProperties();selected=null;draw();window.print()};
function updateFullscreen(){
 const active=!!document.fullscreenElement,button=$('fullscreen');
 const label=active?'Sair da tela cheia':'Entrar em tela cheia';
 const path=active?'M9 3v6H3m18 0h-6V3M3 15h6v6m6 0v-6h6':'M9 3H3v6m12-6h6v6M3 15v6h6m6 0h6v-6';
 button.innerHTML=`<svg class="toolbar-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="${path}"/></svg>`;
 button.title=active?label+' (Esc)':label;
 button.setAttribute('aria-label',label);button.setAttribute('aria-pressed',String(active));
}
$('fullscreen').onclick=async()=>{
 const button=$('fullscreen');button.disabled=true;
 try{
  if(document.fullscreenElement)await document.exitFullscreen();
  else if(document.documentElement.requestFullscreen)await document.documentElement.requestFullscreen();
  else $('message').textContent='Este navegador não oferece tela cheia pelo botão. Use F11 no computador.';
 }catch{
  $('message').textContent='Não foi possível alternar a tela cheia. Tente novamente ou use F11 no computador.';
 }finally{button.disabled=false;updateFullscreen()}
};
document.addEventListener('fullscreenchange',updateFullscreen);
updateFullscreen();
document.addEventListener('keydown',ev=>{
 if(ev.isComposing||['INPUT','TEXTAREA','SELECT'].includes(ev.target.tagName)||ev.target.isContentEditable)return;
 const key=ev.key.toLowerCase(),command=(ev.ctrlKey||ev.metaKey)&&!ev.altKey&&!ev.shiftKey;
 if(command){
  if(key==='c'){if(copySelected())ev.preventDefault();return}
  if(key==='v'){if(pasteSelected())ev.preventDefault();return}
  if(key==='z'){ev.preventDefault();$('undo').click();return}
  if(key==='s'){ev.preventDefault();$('save').click();return}
 }
 if(ev.key==='Escape'){connecting=false;source=null;selected=null;drag=null;$('connect').textContent='+ Ligação';$('message').textContent='';draw();inspect()}
 if(ev.key==='Delete'){ev.preventDefault();$('delete').click()}
});
draw();$('status').textContent='Editor local · JSON editável';
