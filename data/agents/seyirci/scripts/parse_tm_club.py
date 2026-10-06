from common import *
from bs4 import BeautifulSoup
import re,glob,os
C=ROOT+'/data/agents/seyirci/cache/tm_club/'
rows=[]
for f in sorted(glob.glob(C+'*.html')):
    vid,y=os.path.basename(f)[:-5].split('_'); y=int(y); sz=sezon(y); club=TM_ID[vid]
    s=BeautifulSoup(open(f).read(),'lxml')
    box=None
    for b in s.select('div.box'):
        h=b.find(['h2','a'],class_=re.compile('content-box-headline'))
        hd=b.get_text(' ',strip=True)[:60]
        ths=[th.get_text(strip=True) for th in b.select('thead th')]
        if 'Matchday' in ths and ('Süper Lig' in hd or 'Super Lig' in hd):
            box=b; break
    if box is None: print('NOBOX',f); continue
    ths=[th.get_text(strip=True) for th in box.select('thead th')]
    for tr in box.select('tbody tr'):
        tds=[td.get_text(' ',strip=True) for td in tr.find_all('td')]
        if len(tds)<9: continue
        m=re.search(r'(\d{2})/(\d{2})/(\d{4})',tds[1])
        if not m: continue
        date=f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
        home=re.sub(r'\s*\(\d+\.\)','',tds[4]).strip(); away=re.sub(r'\s*\(\d+\.\)','',tds[6]).strip()
        hs=std(home,sz)
        if hs!=club: continue
        att=tds[-2].replace('.','')
        rows.append(dict(takim=club,sezon=sz,tarih=date,ev_tm=home,dep_tm=away,dep=std(away,sz),tm_seyirci=int(att) if att.isdigit() else None,sonuc=tds[-1],tm_url=f'https://www.transfermarkt.com/x/spielplan/verein/{vid}/saison_id/{y}/plus/1'))
df=pd.DataFrame(rows); df.to_csv(ROOT+'/data/agents/seyirci/mac_tm.csv',index=False)
print(df.groupby(['takim','sezon']).agg(n=('tarih','size'),att=('tm_seyirci','count')).to_string())
