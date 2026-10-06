from common import *
import re,io
from bs4 import BeautifulSoup
C=ROOT+'/data/agents/seyirci/cache/'
def tabs(f):
    html=re.sub(r'(colspan|rowspan)="(\d+)\.\d+"',r'\1="\2"',open(f).read())
    return pd.read_html(io.StringIO(html))
def num(x):
    x=re.sub(r'\[.*?\]','',str(x)); x=re.sub(r'[^\d]','',x); return int(x) if x else None
lt=league_teams()
att=[];cap=[]
for y in range(2016,2026):
    sz=sezon(y); teams=set(lt[lt.sezon==sz].takim)
    url=f'https://en.wikipedia.org/wiki/{y}%E2%80%93{str(y+1)[2:]}_S%C3%BCper_Lig'
    for t in tabs(C+f'wiki_en_{y}.html'):
        cols=[str(c) for c in t.columns]; lc=' '.join(cols).lower()
        if 'capacity' in lc and 'stadium' in lc and len(t)>=17:
            tc=[c for c in cols if 'team' in c.lower()][0]; cc=[c for c in cols if 'capacity' in c.lower()][0]; sc=[c for c in cols if 'stadium' in c.lower()][0]
            for _,r in t.iterrows():
                k=std(r[tc],sz)
                if k in teams: cap.append(dict(takim=k,sezon=sz,wiki_kapasite=num(r[cc]),wiki_stadyum=r[sc],wiki_cap_url=url))
        if 'attendance' in lc and len(t)>=17:
            cc=[c for c in cols if 'club' in c.lower() or 'team' in c.lower()][0]; ac=[c for c in cols if 'average' in c.lower()][0]
            hg=[c for c in cols if 'home games' in c.lower()]
            for _,r in t.iterrows():
                k=std(r[cc],sz)
                if k in teams: att.append(dict(takim=k,sezon=sz,wiki_ort=num(r[ac]),wiki_mac=num(r[hg[0]]) if hg else None,wiki_url=url))
# 2016-17 special section
s=BeautifulSoup(open(C+'wiki_en_2016.html').read(),'lxml')
tb=s.find(id='Attendances').find_parent().find_next('table')
for tr in tb.find_all('tr'):
    tds=[td.get_text(' ',strip=True) for td in tr.find_all(['td','th'])]
    if len(tds)>=2:
        k=std(tds[1],'2016-17')
        if k: att.append(dict(takim=k,sezon='2016-17',wiki_ort=num(tds[2]),wiki_mac=None,wiki_url='https://en.wikipedia.org/wiki/2016%E2%80%9317_S%C3%BCper_Lig'))
A=pd.DataFrame(att).drop_duplicates(['takim','sezon']); K=pd.DataFrame(cap).drop_duplicates(['takim','sezon'])
print(A.groupby('sezon').size()); print(K.groupby('sezon').size())
miss=lt.merge(K,how='left'); print(miss[miss.wiki_kapasite.isna()])
A.to_csv(ROOT+'/data/agents/seyirci/kaynak_wiki_sezon.csv',index=False); K.to_csv(ROOT+'/data/agents/seyirci/kaynak_wiki_kapasite.csv',index=False)
# tr 2018-19 table (TM-derived)
t=tabs(C+'wiki_tr_2018.html')[15]; print(t.columns.tolist())
