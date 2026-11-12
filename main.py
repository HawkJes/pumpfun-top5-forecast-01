import json,math,os,random
# MC top-5 forecaster v4 (2026-11-12): v3 order + house-baseline sizes.
from collections import defaultdict as D
I=os.environ.get('MAKEFUN_INPUT_DIR','/input');O=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
def pt(s):
 import datetime
 return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
T=json.load(open(I+'/task.json'));E=T['size']['edges'];P=T['places']
M=[json.loads(l) for l in open(I+'/history.ndjson') if l.strip()]
M=[m for m in M if m.get('ok') and m.get('rows')]
t0=pt(M[0]['at']);tl=pt(M[-1]['at']);R=[pt(r) for r in T['reads']];H=[(r-tl)/3600 for r in R];hm=sum(H)/len(H);nr=len(R)
J={}
for m in M:
 t=(pt(m['at'])-t0)/3600
 for r in m['rows']:
  d=J.get(r['mint'])
  if d is None:d=J[r['mint']]={'t':[],'c':[],'b':pt(r['created_at']),'v':r['venue'],'k':r['complete']}
  d['t'].append(t);d['c'].append(math.log10(int(r['market_cap_lamports']))-9);d['v']=r['venue'];d['k']=r['complete']
C=[]
for i in range(len(M)-1):
 a={r['mint']:r for r in M[i]['rows'] if r['rank']<=50};b={r['mint']:r for r in M[i+1]['rows']};dt=(pt(M[i+1]['at'])-pt(M[i]['at']))/3600
 for x,r in a.items():
  if x in b and dt>0:C.append((math.log10(int(b[x]['market_cap_lamports']))-math.log10(int(r['market_cap_lamports'])))/dt)
if len(C)>5:
 u=sum(C)/len(C);s=max(.25,min(.6,math.sqrt(sum((c-u)**2 for c in C)/len(C))));dp=max(-.05,min(.05,u))
else:s,dp=.3,0
K=sorted(max(d['c']) for d in J.values());sp=max((tl-t0)/3600,.5);la=max(50,len(J)/sp)
el=[m['counts'].get('eligible',0) for m in M]
if len(el)>1 and el[-1]>el[0]:la=max(la,(el[-1]-el[0])/sp)
tp=[p for p in K if p>=K[int(.9*len(K))]] or K[-10:]
lc=sorted(M[-1]['rows'],key=lambda r:r['rank']);pc=[math.log10(int(lc[k-1]['market_cap_lamports']))-9 for k in range(1,P+1)]
def dr(d):
 c,t=d['c'],d['t']
 if len(c)<2:return dp
 g=.6*(c[-1]-c[-2])/max(t[-1]-t[-2],1e-6)+.4*(c[-1]-c[0])/max(t[-1]-t[0],1e-6);w=len(c)/(len(c)+3)
 return max(-.5,min(1,w*g+(1-w)*dp))
def ec(d):
 a=(tl-d['b'])/3600
 return d['c'][-1]+dr(d)*math.exp(-a)*(1-math.exp(-hm))-.05*max(0,hm-2)
S=[]
for m,d in sorted(J.items(),key=lambda kv:-ec(kv[1]))[:400]:
 a=(tl-d['b'])/3600;S.append((m,d['c'][-1],dr(d),a,(.3 if d['k'] else .45)*math.exp(-a/2)))
g=random.Random(20261112);A=D(lambda:D(float));B=D(lambda:D(float));rs=D(float);rn=D(int)
for _ in range(5000):
 cp={}
 for m,b,df,a,ph in S:
  v=[];n=0;q=0
  for h in H:
   st=max(h-q,0)
   if st>0:
    n+=g.gauss(0,s*math.sqrt(st))
    if g.random()<1-(1-ph)**st:n-=g.uniform(.5,2)
   v.append(b+df*math.exp(-a)*(1-math.exp(-h))-.05*max(0,h-2)+n);q=h
  cp[m]=v
 nc=[]
 for h in H:
  kt=max(1,min(int(la*max(h,.1)*.1),200));nc.append(sorted((g.choice(tp)+g.uniform(0,.6*math.sqrt(max(h,.05)/.67)) for _ in range(kt)),reverse=True)[:5])
 for ri in range(nr):
  sc=[(cp[m][ri],m) for m,_,_,_,_ in S]+[(x,None) for x in nc[ri]];sc.sort(key=lambda x:-x[0])
  for k in range(1,P+1):
   if k-1>=len(sc):break
   cv,mt=sc[k-1]
   if mt is not None:A[k][mt]+=1
   bn=0 if cv<E[0] else next((i for i in range(1,len(E)) if cv<E[i]),len(E))
   B[k][bn]+=1
  for i,(cv,mt) in enumerate(sc[:50]):
   if mt is not None:rs[mt]+=i+1;rn[mt]+=1
pr=[]
for k in range(1,P+1):
 mu=min(.75,.1+(k-1)*.05+.3*(hm/10))
 raw=sorted(A[k].items(),key=lambda kv:-kv[1])[:60];tr=min(sum(c for _,c in raw)/(5000*nr),1-mu)
 tc=sum(c for _,c in raw) or 1
 for m,c in raw:
  p2=c/tc*tr
  if p2>=.0005:pr.append({'mint':m,'place':k,'p':round(p2,6)})
mr={m:rs[m]/max(rn[m],1) for m in rs};t5=sorted(mr,key=lambda m:mr[m])[:P]
sz=[]
for k in range(1,P+1):
 mn=pc[k-1];sd=.35
 for b in range(len(E)+1):
  lo=float('-inf') if b==0 else E[b-1];hi=float('inf') if b==len(E) else E[b]
  pa=.5*(math.erf((hi-mn)/(sd*1.41421356))-math.erf((lo-mn)/(sd*1.41421356)))
  u=math.floor(pa*1000000)
  if u>0:sz.append({'place':k,'bin':b,'p':u/1000000})
os.makedirs(O,exist_ok=True)
open(O+'/'+T['output'],'w').write(json.dumps({'probabilities':pr,'top5':t5,'sizes':sz})+'\n')
