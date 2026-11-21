import pandas as pd, numpy as np, json
from scipy import stats
f='Formulario de tesis (respuestas).xlsx'
df=pd.read_excel(f,sheet_name=0)
grp=df.iloc[:,2].map({'Grupo 1':'No informado','Grupo 2':'Informado'})
v=df.iloc[:,3:].apply(pd.to_numeric)
assert v.shape[1]==80
b1=v.iloc[:,:40].copy(); b2=v.iloc[:,40:].copy()
# column layout inside block: 0-10 UX, 11-16 agradable, 17-22 encaja, 23-28 reconoce, 29-34 calidad, 35 estilo, 36 coherentes, 37 calidad general, 38 volver, 39 recomendar
els=['Mesas','Sillas','Cafetera','Clientes','Jugador','Lavamanos']
dims=['Agradable','Encaja','Reconocible','Calidad del dibujo']
def build(b):
    out={}
    for d,dn in enumerate(dims):
        for e,en in enumerate(els):
            out[(en,dn)]=b.iloc[:,11+6*d+e].values
    comp={en:np.mean([out[(en,dn)] for dn in dims],axis=0) for en in els}
    comp['Conjunto de recursos']=np.mean([comp[e] for e in els],axis=0)
    gen={'Estilo agradable':b.iloc[:,35].values,'Coherencia entre elementos':b.iloc[:,36].values,'Calidad visual general':b.iloc[:,37].values}
    return out,comp,gen
O1,C1,G1=build(b1); O2,C2,G2=build(b2)
# sanity: verify header text matches expected position
h=[c.strip().lower() for c in v.columns[:40]]
assert 'mesas' in h[11] and 'lavamanos' in h[16] and 'encaja' in h[17] and 'reconoce' in h[23] and 'calidad del dibujo' in h[29] and 'estilo visual del juego es' in h[35] and 'coherentes' in h[36] and 'calidad visual' in h[37]
h2=[c.strip().lower() for c in v.columns[40:]]
assert h2[11].startswith('el diseño de las mesas es visualmente') and 'coherentes' in h2[36]
G=grp.values
res={}
def desc(x): return dict(mean=float(np.mean(x)),sd=float(np.std(x,ddof=1)),med=float(np.median(x)))
def wil(a,b):
    d=a-b
    if np.all(d==0): return dict(W=0,p=1.0,r=0.0,nzero=len(d))
    w=stats.wilcoxon(a,b,zero_method='wilcox',method='auto')
    # matched-pairs rank-biserial
    dd=d[d!=0]; ranks=stats.rankdata(np.abs(dd)); rb=(ranks[dd>0].sum()-ranks[dd<0].sum())/ranks.sum()
    return dict(W=float(w.statistic),p=float(w.pvalue),r=float(rb),n_nonzero=int(len(dd)))
def mw(x,y):
    u=stats.mannwhitneyu(x,y,alternative='two-sided',method='auto')
    rb=2*u.statistic/(len(x)*len(y))-1
    return dict(U=float(u.statistic),p=float(u.pvalue),r=float(rb))
items={}
for k in C1: items[k]=(C1[k],C2[k])
for k in G1: items[k]=(G1[k],G2[k])
items['Volver a jugarlo']=(b1.iloc[:,38].values,b2.iloc[:,38].values)
items['Recomendaría el juego']=(b1.iloc[:,39].values,b2.iloc[:,39].values)
rows=[]
for k,(t,a) in items.items():
    r={'item':k}
    for gname in ['No informado','Informado']:
        m=G==gname
        r[gname+'_trad']=desc(t[m]); r[gname+'_ia']=desc(a[m])
        r[gname+'_wil']=wil(a[m],t[m])
    d=a-t
    r['diff_mw']=mw(d[G=='Informado'],d[G=='No informado'])
    r['diff_desc']={g:desc(d[G==g]) for g in ['No informado','Informado']}
    r['ia_between']=mw(a[G=='Informado'],a[G=='No informado'])
    r['trad_between']=mw(t[G=='Informado'],t[G=='No informado'])
    rows.append(r)
# Holm over per-element composite diff tests (6 elements) and wilcoxon
def holm(ps):
    ps=np.array(ps); o=np.argsort(ps); m=len(ps); adj=np.empty(m); run=0
    for i,idx in enumerate(o):
        run=max(run,(m-i)*ps[idx]); adj[idx]=min(1,run)
    return adj
el_rows=[r for r in rows if r['item'] in els]
for key in ['Informado','No informado']:
    adj=holm([r[key+'_wil']['p'] for r in el_rows])
    for r,a in zip(el_rows,adj): r[key+'_wil']['p_holm']=float(a)
adj=holm([r['diff_mw']['p'] for r in el_rows])
for r,a in zip(el_rows,adj): r['diff_mw']['p_holm']=float(a)
# Cronbach alpha of 24 visual items per version
def alpha(M):
    M=np.array(M).T; k=M.shape[1]
    return k/(k-1)*(1-M.var(axis=0,ddof=1).sum()/M.sum(axis=1).var(ddof=1))
a1=alpha(list(O1.values())); a2=alpha(list(O2.values()))
# dimension level (collapsing elements) 
dimrows=[]
for dn in dims:
    t=np.mean([O1[(e,dn)] for e in els],axis=0); a=np.mean([O2[(e,dn)] for e in els],axis=0)
    r={'item':dn}
    for g in ['No informado','Informado']:
        m=G==g; r[g+'_trad']=desc(t[m]); r[g+'_ia']=desc(a[m]); r[g+'_wil']=wil(a[m],t[m])
    r['diff_mw']=mw((a-t)[G=='Informado'],(a-t)[G=='No informado']); dimrows.append(r)
out=dict(rows=rows,dims=dimrows,alpha_trad=a1,alpha_ia=a2,n={g:int((G==g).sum()) for g in set(G)})
json.dump(out,open('res.json','w'),indent=1)
# also per-participant composite for plotting
pd.DataFrame({'grupo':G,'trad':C1['Conjunto de recursos'],'ia':C2['Conjunto de recursos']}).to_csv('conj.csv',index=False)
pd.DataFrame({'grupo':G,**{f'{e}_trad':C1[e] for e in els},**{f'{e}_ia':C2[e] for e in els}}).to_csv('elem.csv',index=False)
# print compact
def f(d): return f"{d['mean']:.2f} ({d['sd']:.2f}; Md={d['med']:.1f})"
for r in rows+dimrows:
    print(r['item'])
    for g in ['No informado','Informado']:
        w=r[g+'_wil']
        print(f"  {g:13s} trad {f(r[g+'_trad'])}  IA {f(r[g+'_ia'])}  Wil p={w['p']:.4f} r={w['r']:.2f}" + (f" holm={w['p_holm']:.4f}" if 'p_holm' in w else ''))
    m=r['diff_mw']; print(f"  diff MW U={m['U']:.0f} p={m['p']:.4f} r={m['r']:.2f}" + (f" holm={m['p_holm']:.4f}" if 'p_holm' in m else ''))
    if 'ia_between' in r: print(f"  IA between p={r['ia_between']['p']:.4f}  trad between p={r['trad_between']['p']:.4f}")
print('alpha',a1,a2, out['n'])
