from common import *
import json,glob,os
C=ROOT+'/data/agents/seyirci/cache/espn/'
rows=[]
for f in sorted(glob.glob(C+'sb_*.json')):
    d=json.load(open(f))
    for e in d.get('events',[]):
        c=e['competitions'][0]
        h=[x for x in c['competitors'] if x['homeAway']=='home'][0]['team']['displayName']
        a=[x for x in c['competitors'] if x['homeAway']=='away'][0]['team']['displayName']
        rows.append(dict(espn_id=e['id'],espn_tarih=e['date'][:10],ev_espn=h,dep_espn=a,espn_seyirci=c.get('attendance'),espn_stad=c.get('venue',{}).get('fullName')))
E=pd.DataFrame(rows).drop_duplicates('espn_id')
dt=pd.to_datetime(E.espn_tarih); E['sezon']=[sezon(y if mo>=7 else y-1) for y,mo in zip(dt.dt.year,dt.dt.month)]
E['ev']=[std(n,s) for n,s in zip(E.ev_espn,E.sezon)]; E['deplasman']=[std(n,s) for n,s in zip(E.dep_espn,E.sezon)]
print('unmapped:',E[E.ev.isna()|E.deplasman.isna()][['ev_espn','dep_espn']].drop_duplicates().values.tolist())
E=E.dropna(subset=['ev','deplasman']).drop_duplicates(['sezon','ev','deplasman'])
E['espn_url']='https://site.api.espn.com/apis/site/v2/sports/soccer/tur.1/summary?event='+E.espn_id.astype(str)
E[['sezon','ev','deplasman','espn_tarih','espn_id','espn_seyirci','espn_stad','espn_url']].to_csv(ROOT+'/data/agents/seyirci/mac_espn.csv',index=False)
print(E.assign(a=E.espn_seyirci.fillna(0)>0).groupby('sezon').agg(n=('a','size'),att=('a','sum')))
