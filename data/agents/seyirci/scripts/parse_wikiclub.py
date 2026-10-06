from common import *
from wikibox import boxes
import glob,os
C=ROOT+'/data/agents/seyirci/cache/'
pages={'Galatasaray':('wikiclub_en_2025_Galatasaray.html','https://en.wikipedia.org/wiki/2025%E2%80%9326_Galatasaray_S.K._season'),
'Beşiktaş':('wikiclub_en_2025_BeC5.html','https://en.wikipedia.org/wiki/2025%E2%80%9326_Be%C5%9Fikta%C5%9F_J.K._season'),
'Fenerbahçe':('wikiclub_en_2025_Fenerb.html','https://en.wikipedia.org/wiki/2025%E2%80%9326_Fenerbah%C3%A7e_S.K._season'),
'Trabzonspor':('wikiclub_en_2025_Trabzo.html','https://en.wikipedia.org/wiki/2025%E2%80%9326_Trabzonspor_season')}
m,_=home_counts(); m=m[m.sezon=='2025-26']
rows=[]
for club,(f,url) in pages.items():
    for b in boxes(C+f):
        if b['section']!='Matches' or b['att'] is None: continue
        h=std(b['home'],'2025-26'); a=std(b['away'],'2025-26')
        if h is None or a is None: continue
        if not ((m.ev==h)&(m.deplasman==a)).any(): continue
        rows.append(dict(sezon='2025-26',ev=h,deplasman=a,tarih_wiki=b['date'],wiki_seyirci=b['att'],wiki_url=url))
W=pd.DataFrame(rows).drop_duplicates(['sezon','ev','deplasman'])
print(W.groupby('ev').size()); W.to_csv(ROOT+'/data/agents/seyirci/mac_wikiclub.csv',index=False)
