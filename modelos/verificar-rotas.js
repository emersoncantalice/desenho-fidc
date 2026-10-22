const fs=require('node:fs'),assert=require('node:assert/strict');
const {routeDiagram}=require('./roteamento.js');
const models=JSON.parse(fs.readFileSync('modelos/arquitetura-credito.json','utf8')).models;
const intersects=(a,b,n)=>a[1]===b[1]?a[1]>n.y+.1&&a[1]<n.y+n.h-.1&&Math.max(a[0],b[0])>n.x+.1&&Math.min(a[0],b[0])<n.x+n.w-.1:a[0]>n.x+.1&&a[0]<n.x+n.w-.1&&Math.max(a[1],b[1])>n.y+.1&&Math.min(a[1],b[1])<n.y+n.h-.1;
for(const m of models){
 const routes=routeDiagram(m),segments=[],labels=[],nodes=m.nodes.filter(n=>!['group','heading','text'].includes(n.kind));
 for(const e of m.edges){
  const r=routes.get(e.id);assert.ok(r,e.id);
  const p=r.points.split(' ').map(v=>v.split(',').map(Number));
  for(let i=1;i<p.length;i++){
   const a=p[i-1],b=p[i];assert.ok(a[0]===b[0]||a[1]===b[1]);
   for(const n of nodes)assert.ok(!intersects(a,b,n),`${m.name}: ${e.id} atravessa ${n.id}`);
   for(const v of segments){const h=a[1]===b[1];if(h!==(v.a[1]===v.b[1]))continue;const k=h?0:1;const overlap=Math.min(Math.max(a[k],b[k]),Math.max(v.a[k],v.b[k]))-Math.max(Math.min(a[k],b[k]),Math.min(v.a[k],v.b[k]));assert.ok(Math.abs(a[1-k]-v.a[1-k])>.1||overlap<=1,`${m.name}: ${e.id} sobrepoe ${v.id}`)}
  }
  for(let i=1;i<p.length;i++)segments.push({id:e.id,a:p[i-1],b:p[i]});
  const [x,y]=r.label,w=e.label.length*6.4+12,box=r.rotation?{x:x-13,y:y-w/2,w:19,h:w}:{x:x-w/2,y:y-13,w,h:19};
  for(const n of [...nodes,...labels])assert.ok(!(box.x<n.x+n.w&&box.x+box.w>n.x&&box.y<n.y+n.h&&box.y+box.h>n.y),`${m.name}: rotulo ${e.id} sobrepoe ${n.id}`);
  labels.push({...box,id:e.id});
 }
 console.log(`OK: ${m.name}: ${routes.size} rotas sem trechos sobrepostos ou passagem por caixas; rotulos separados.`);
}
