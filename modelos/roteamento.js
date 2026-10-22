// Rotas ortogonais com portas distintas e preferência por corredores livres.
function routeDiagram(m){
 const nodes=new Map(m.nodes.map(n=>[n.id,n]));
 const obstacles=m.nodes.filter(n=>!['group','heading','text'].includes(n.kind));
 const used=[],labels=[],result=new Map();
 const sides={left:[-1,0],right:[1,0],top:[0,-1],bottom:[0,1]};
 function port(id,side,edgeId,isSource){
  const n=nodes.get(id),ports=[];
  for(const e of m.edges){if(e.source===id&&e.sourceSide===side)ports.push(e.id+':s');if(e.target===id&&e.targetSide===side)ports.push(e.id+':t')}
  const fraction=(ports.indexOf(edgeId+(isSource?':s':':t'))+1)/(ports.length+1);
  return side==='left'?[n.x,n.y+n.h*fraction]:side==='right'?[n.x+n.w,n.y+n.h*fraction]:side==='top'?[n.x+n.w*fraction,n.y]:[n.x+n.w*fraction,n.y+n.h];
 }
 const segments=p=>p.slice(1).map((v,i)=>[p[i],v]);
 function clean(p){const q=[];for(const v of p){if(q.length&&q.at(-1)[0]===v[0]&&q.at(-1)[1]===v[1])continue;while(q.length>1&&((q.at(-2)[0]===q.at(-1)[0]&&v[0]===q.at(-1)[0])||(q.at(-2)[1]===q.at(-1)[1]&&v[1]===q.at(-1)[1]))){const a=q.at(-2),b=q.at(-1);if((b[0]-a[0])*(v[0]-b[0])+(b[1]-a[1])*(v[1]-b[1])<0)break;q.pop()}q.push(v)}return q}
 function inside(a,b,n){const eps=.1;return a[1]===b[1]?a[1]>n.y+eps&&a[1]<n.y+n.h-eps&&Math.max(a[0],b[0])>n.x+eps&&Math.min(a[0],b[0])<n.x+n.w-eps:a[0]>n.x+eps&&a[0]<n.x+n.w-eps&&Math.max(a[1],b[1])>n.y+eps&&Math.min(a[1],b[1])<n.y+n.h-eps}
 function cost(p){let score=p.length*12;for(const [a,b] of segments(p)){
  score+=Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1]);
  if([...a,...b].some(v=>!Number.isFinite(v))||Math.min(a[0],b[0])<20||Math.max(a[0],b[0])>m.width-20||Math.min(a[1],b[1])<110||Math.max(a[1],b[1])>m.height-20)score+=1e7;
  for(const n of obstacles)if(inside(a,b,n))score+=1e6;
  for(const n of labels)if(inside(a,b,n))score+=3000;
  for(const [c,d] of used){const h=a[1]===b[1],h2=c[1]===d[1];if(h===h2){const axis=h?0:1,fixed=1-axis,overlap=Math.min(Math.max(a[axis],b[axis]),Math.max(c[axis],d[axis]))-Math.max(Math.min(a[axis],b[axis]),Math.min(c[axis],d[axis]));if(overlap>1&&Math.abs(a[fixed]-c[fixed])<18)score+=overlap*2000;}else{const [ha,hb,va,vb]=h?[a,b,c,d]:[c,d,a,b];if(va[0]>Math.min(ha[0],hb[0])&&va[0]<Math.max(ha[0],hb[0])&&ha[1]>Math.min(va[1],vb[1])&&ha[1]<Math.max(va[1],vb[1]))score+=80;}}
 }return score}
 for(const e of m.edges){if(!nodes.has(e.source)||!nodes.has(e.target))continue;
  const s=port(e.source,e.sourceSide,e.id,true),t=port(e.target,e.targetSide,e.id,false);
  const sd=sides[e.sourceSide],td=sides[e.targetSide];if(!sd||!td)continue;
  const ss=[s[0]+sd[0]*24,s[1]+sd[1]*24],tt=[t[0]+td[0]*24,t[1]+td[1]*24];
  const xs=new Set([ss[0],tt[0],(ss[0]+tt[0])/2]),ys=new Set([ss[1],tt[1],(ss[1]+tt[1])/2]);
  if(e.via!=null){if(sd[0]&&td[0])xs.add(e.via);else ys.add(e.via)}
  for(const n of obstacles){xs.add(n.x-30);xs.add(n.x+n.w+30);ys.add(n.y-30);ys.add(n.y+n.h+30)}
  for(const [a,b] of used){if(a[0]===b[0]){xs.add(a[0]-30);xs.add(a[0]+30)}else{ys.add(a[1]-30);ys.add(a[1]+30)}}
  const candidates=[];
  for(const x of xs)candidates.push(clean([s,ss,[x,ss[1]],[x,tt[1]],tt,t]));
  for(const y of ys)candidates.push(clean([s,ss,[ss[0],y],[tt[0],y],tt,t]));
  candidates.push(clean([s,ss,[ss[0],tt[1]],tt,t]),clean([s,ss,[tt[0],ss[1]],tt,t]));
  let best=candidates[0],bestCost=Infinity;
  for(const p of candidates){const value=cost(p);if(value<bestCost){best=p;bestCost=value}}
  const parts=segments(best);let placement=null,placementScore=Infinity;
  for(const [a,b] of parts){const horizontal=a[1]===b[1],length=Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1]),width=e.label.length*6.4+12;
   for(const f of [.5,.3,.7]){const x=a[0]+(b[0]-a[0])*f+(horizontal?0:12),y=a[1]+(b[1]-a[1])*f-(horizontal?10:0);const box=horizontal?{x:x-width/2,y:y-13,w:width,h:19}:{x:x-13,y:y-width/2,w:19,h:width};
    const overlap=n=>box.x<n.x+n.w&&box.x+box.w>n.x&&box.y<n.y+n.h&&box.y+box.h>n.y;
    let v=(length<width?(width-length)*1000:0)+(horizontal?0:25)-Math.min(length,500)/100;
    for(const n of [...obstacles,...labels])if(overlap(n))v+=1e5;
    if(v<placementScore){placementScore=v;placement={label:[x,y],rotation:horizontal?0:-90,box}}
   }
  }
  used.push(...parts);if(placement)labels.push(placement.box);
  result.set(e.id,{points:best.map(v=>v.join(',')).join(' '),label:placement?.label??s,rotation:placement?.rotation??0});
 }
 return result;
}
if(typeof module!=='undefined')module.exports={routeDiagram};
