function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]))}
function anchor(n,side){return side==='left'?[n.x,n.y+n.h/2]:side==='right'?[n.x+n.w,n.y+n.h/2]:side==='top'?[n.x+n.w/2,n.y]:[n.x+n.w/2,n.y+n.h]}
function legacyGeometry(m,e){
 const a=m.nodes.find(n=>n.id===e.source),b=m.nodes.find(n=>n.id===e.target);if(!a||!b)return null;
 const s=anchor(a,e.sourceSide),t=anchor(b,e.targetSide);let p;
 const sh=['left','right'].includes(e.sourceSide),th=['left','right'].includes(e.targetSide);
 if(sh&&th){const x=e.via??(s[0]+t[0])/2;p=[s,[x,s[1]],[x,t[1]],t]}
 else if(!sh&&!th){const y=e.via??(s[1]+t[1])/2;p=[s,[s[0],y],[t[0],y],t]}
 else if(sh){p=[s,[t[0],s[1]],t]}else if(e.via!=null){const x=t[0]+(e.targetSide==='left'?-30:30);p=[s,[s[0],e.via],[x,e.via],[x,t[1]],t]}else{p=[s,[s[0],t[1]],t]}
 let best=0,len=-1;for(let i=0;i<p.length-1;i++){const d=Math.abs(p[i][0]-p[i+1][0])+Math.abs(p[i][1]-p[i+1][1]);if(d>len){best=i;len=d}}
 return {points:p.map(v=>v.join(',')).join(' '),label:[(p[best][0]+p[best+1][0])/2,(p[best][1]+p[best+1][1])/2-9]};
}
function routesFor(m){return (typeof routeDiagram==='function'?routeDiagram:require('./roteamento.js').routeDiagram)(m)}
function geometry(m,e){return routesFor(m).get(e.id)??null}
function renderNode(n){
 const change=['new','adapt','legacy','existing'].includes(n.change)?' change-'+n.change:'';
 let s=`<g data-node="${esc(n.id)}" class="node${change}">`;
 if(n.kind==='group')s+=`<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" fill="#f4f6fa" stroke="#cbd3e3"/><text x="${n.x+18}" y="${n.y+28}" class="section">${esc(n.title)}</text><text x="${n.x+18}" y="${n.y+50}" class="small">${esc(n.detail)}</text>`;
 else if(['text','heading'].includes(n.kind)){s+=`<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" fill="transparent"/>`;if(n.title)s+=`<text x="${n.x}" y="${n.y+28}" class="${n.kind==='heading'?'heading':'title'}">${esc(n.title)}</text>`;n.detail.split('\n').forEach((t,i)=>s+=`<text x="${n.x}" y="${n.y+(n.title?55:18)+i*21}" class="small">${esc(t)}</text>`)}
 else{
  s+=`<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="2" fill="white" stroke="#0033cc" stroke-width="1.3"/>`;
  if(n.kind==='database')s+=`<path d="M${n.x},${n.y+10} Q${n.x+n.w/2},${n.y+30} ${n.x+n.w},${n.y+10}" fill="none" stroke="#0033cc"/>`;
  if(n.kind==='actor')s+=`<circle cx="${n.x+20}" cy="${n.y+23}" r="6" fill="none" stroke="#374151"/><path d="M${n.x+20},${n.y+29}v16m-9,-10h18m-9,10l-8,10m8,-10l8,10" fill="none" stroke="#374151"/>`;
  const tx=n.x+(n.kind==='actor'?40:16);
  s+=`<text x="${tx}" y="${n.y+(n.kind==='database'?42:29)}" class="title">${esc(n.title)}</text>`;
  n.detail.split('\n').forEach((t,i)=>s+=`<text x="${tx}" y="${n.y+(n.kind==='database'?67:52)+i*20}" class="small">${esc(t)}</text>`);
 }
 return s+'</g>';
}
function render(m){
 const style=`text{font-family:Arial,Helvetica,sans-serif;fill:#16181c}.heading{fill:#001e62;font-size:25px;font-weight:700;letter-spacing:1px}.title{fill:#001e62;font-size:17px;font-weight:600}.section{fill:#0033cc;font-size:15px;font-weight:700;letter-spacing:1px}.small{font-size:14px;fill:#55606d}.edge-label{font-size:12px;fill:#354251;paint-order:stroke;stroke:white;stroke-width:5px;stroke-linejoin:round}.selected>rect{stroke:#0033cc;stroke-width:3}.selected>polyline:not(.hit){stroke:#0033cc;stroke-width:3}`;
 const changeStyle='.change-new>rect{fill:#0033cc}.change-new .title,.change-new .small{fill:#fff}.change-new>path,.change-new>circle{stroke:#fff}.change-adapt>rect{fill:#e2ebff}.change-legacy>rect{fill:#e1e3e7;stroke:#737a85}.change-legacy .title{fill:#252a33}.change-existing>rect{fill:#fff;stroke:#737a85}.change-new.selected>rect{stroke:#16181c;stroke-width:4;stroke-dasharray:6 3}';
 let s=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${m.width} ${m.height}" role="img" aria-label="${esc(m.name)}"><title>${esc(m.name)}</title><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10z" fill="#52606d"/></marker></defs><style>${style}${m.nodes.some(n=>n.change)?changeStyle:''}</style><rect width="100%" height="100%" fill="white"/>`;
 s+=m.nodes.filter(n=>n.kind==='group').map(renderNode).join('');
 const routes=routesFor(m);
 for(const e of m.edges){const g=routes.get(e.id);if(!g)continue;s+=`<g data-edge="${esc(e.id)}"><polyline class="hit" points="${g.points}" stroke="transparent" stroke-width="16" fill="none"/><polyline class="hit" points="${g.points}" fill="none" stroke="white" stroke-width="5" pointer-events="none"/><polyline points="${g.points}" fill="none" stroke="#52606d" stroke-width="1.5" ${e.async_?'stroke-dasharray="1 6" stroke-linecap="round"':''} marker-end="url(#arrow)"/><text x="${g.label[0]}" y="${g.label[1]}" text-anchor="middle" transform="rotate(${g.rotation??0} ${g.label[0]} ${g.label[1]})" class="edge-label">${esc(e.label)}</text></g>`}
 s+=m.nodes.filter(n=>n.kind!=='group').map(renderNode).join('');return s+'</svg>';
}
if(typeof module!=='undefined')module.exports={render,geometry};
