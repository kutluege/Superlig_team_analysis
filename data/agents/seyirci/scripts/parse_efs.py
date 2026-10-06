from common import *
from bs4 import BeautifulSoup
import re
C=ROOT+'/data/agents/seyirci/cache/'
files={'2016-17':'efs_avetur17.htm','2017-18':'efs_avetur18.htm','2018-19':'efs_avetur19.htm','2019-20':'efs_avetur20.htm','2022-23':'efs_avetur23.htm','2023-24':'efs_avetur24.htm','2024-25':'efs_avetur25.htm','2025-26':'efs_avetur.htm'}
urls={'2025-26':'https://www.european-football-statistics.co.uk/attn/avetur.htm'}
lt=league_teams()
rows=[]
for sz,f in files.items():
    s=BeautifulSoup(open(C+f,'rb').read().decode('cp1254',errors='replace'),'lxml')
    teams=set(lt[lt.sezon==sz].takim)
    for tr in s.find_all('tr'):
        tds=[td.get_text(' ',strip=True) for td in tr.find_all('td')]
        if len(tds)<3 or not re.fullmatch(r'\d+',tds[0] or ''): continue
        name=tds[1]; t=std(name,sz)
        avg=tds[2].replace('.','')
        if not avg.isdigit(): continue
        games=None
        if sz=='2025-26' and len(tds)>3 and tds[3].isdigit(): games=int(tds[3])
        if t in teams:
            rows.append(dict(takim=t,sezon=sz,efs_ort=int(avg),efs_mac=games,efs_isim=name,efs_url=urls.get(sz,'https://www.european-football-statistics.co.uk/attn/archive/tur/'+f.replace('efs_',''))))
        # stop after super lig table: second league table repeats ranks; teams filter handles
df=pd.DataFrame(rows).drop_duplicates(['takim','sezon'],keep='first')
print(df.groupby('sezon').size()); 
miss=lt[lt.sezon.isin(files)].merge(df,how='left'); print(miss[miss.efs_ort.isna()])
df.to_csv(ROOT+'/data/agents/seyirci/kaynak_efs.csv',index=False)
