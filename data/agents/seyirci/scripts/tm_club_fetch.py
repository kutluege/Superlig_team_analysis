import pandas as pd,requests,time,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from common import *
C=ROOT+'/data/agents/seyirci/cache/tm_club'; os.makedirs(C,exist_ok=True)
tm=pd.read_csv(ROOT+'/data/agents/seyirci/tm_raw.csv',dtype={'tm_id':str})
inv={v:k for k,v in TM_ID.items()}
ts=pd.read_csv(ROOT+'/data/team_season.csv'); ts=ts[(ts.ligde==True)&(ts.sezon!='2020-21')]
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
for _,r in ts.iterrows():
    vid=inv.get(r.takim); y=int(r.sezon[:4])
    if vid is None: print('NOID',r.takim,flush=True); continue
    f=f'{C}/{vid}_{y}.html'
    if os.path.exists(f) and os.path.getsize(f)>50000: continue
    for k in range(3):
        try:
            rr=requests.get(f'https://www.transfermarkt.com/x/spielplan/verein/{vid}/saison_id/{y}/plus/1',headers=H,timeout=40)
            if rr.status_code==200: open(f,'w').write(rr.text); break
            print(r.takim,y,rr.status_code,flush=True)
        except Exception as e: print(r.takim,y,e,flush=True)
        time.sleep(6)
    time.sleep(2)
print('DONE')
