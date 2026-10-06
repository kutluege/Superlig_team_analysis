import sys,re,pandas as pd
from bs4 import BeautifulSoup
rows=[]
for y in range(2016,2026):
    s=BeautifulSoup(open(f'cache/tm_{y}.html').read(),'lxml')
    for tr in s.select('table.items')[0].select('tbody > tr'):
        tds=tr.find_all('td',recursive=False)
        if len(tds)<5: continue
        inner=tds[1]
        stad=inner.select_one('td.hauptlink a').get_text(strip=True)
        club_a=inner.select('tr')[1].find('a')
        club=club_a.get_text(strip=True); vid=re.search(r'/verein/(\d+)',club_a['href']).group(1)
        num=lambda x:int(x.get_text(strip=True).replace('.','') or 0)
        rows.append(dict(sezon_yil=y,tm_club=club,tm_id=vid,stadyum=stad,kapasite=num(tds[2]),toplam=num(tds[3]),ort=num(tds[4])))
df=pd.DataFrame(rows); df.to_csv('tm_raw.csv',index=False); print(df.to_string())
