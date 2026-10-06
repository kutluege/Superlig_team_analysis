import pandas as pd,requests,time,json,os
ROOT='/home/user/Superlig_team_analysis'; C=ROOT+'/data/agents/seyirci/cache/espn'
os.makedirs(C,exist_ok=True)
m=pd.read_csv(ROOT+'/data/matches.csv')
dates=sorted(m[m.sezon!='2020-21'].tarih.unique())
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
for i,d in enumerate(dates):
    f=f'{C}/sb_{d.replace("-","")}.json'
    if os.path.exists(f): continue
    for k in range(3):
        try:
            r=requests.get(f'https://site.api.espn.com/apis/site/v2/sports/soccer/tur.1/scoreboard?dates={d.replace("-","")}',headers=H,timeout=30)
            if r.status_code==200:
                open(f,'w').write(r.text); break
            print(d,r.status_code,flush=True)
        except Exception as e: print(d,e,flush=True)
        time.sleep(5)
    time.sleep(1.1)
    if i%50==0: print(i,d,flush=True)
print('DONE')
