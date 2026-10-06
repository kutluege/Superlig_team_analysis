import pandas as pd
ROOT='/home/user/Superlig_team_analysis'
TM_ID={'114':'Beşiktaş','141':'Galatasaray','36':'Fenerbahçe','449':'Trabzonspor','20':'Bursaspor','2293':'Konyaspor','589':'Antalyaspor','3205':'Kayserispor','11282':'Alanyaspor','2944':'Osmanlıspor','524':'Gaziantepspor','1506':'Karabükspor','6':'Adanaspor','126':'Çaykur Rizespor','6890':'İstanbul Başakşehir','19771':'Akhisarspor','820':'Gençlerbirliği','10484':'Kasımpaşa','1467':'Göztepe','2381':'Sivasspor','19789':'Yeni Malatyaspor','39722':'Erzurumspor','868':'Ankaragücü','2832':'Gaziantep FK','833':'Denizlispor','7775':'Hatayspor','6646':'Fatih Karagümrük','3840':'Adana Demirspor','11688':'Giresunspor','2375':'Altay','924':'İstanbulspor','24245':'Ümraniyespor','152':'Samsunspor','3209':'Pendikspor','7160':'Eyüpspor','44006':'Bodrum FK','120':'Kocaelispor'}
def sezon(y): return f'{y}-{str(y+1)[2:]}'
def home_counts():
    m=pd.read_csv(f'{ROOT}/data/matches.csv')
    m['kapali']=False
    m.loc[m.sezon=='2020-21','kapali']=True
    m.loc[(m.sezon=='2019-20')&(m.tarih>='2020-03-12'),'kapali']=True
    g=m.groupby(['ev','sezon']).agg(ev_mac=('tarih','size'),kapali=('kapali','sum')).reset_index().rename(columns={'ev':'takim'})
    g['seyircili_mac']=g.ev_mac-g.kapali
    return m,g

def fold(s):
    s=str(s).replace('İ','i').replace('I','ı').lower()
    for a,b in zip('çğıöşüâîû','cgiosuaiu'): s=s.replace(a,b)
    return s.replace('i̇','i').replace('̇','')
KEYS=[('adana demir','Adana Demirspor'),('demirspor','Adana Demirspor'),('adanaspor','Adanaspor'),('akhisar','Akhisarspor'),('alanya','Alanyaspor'),('altay','Altay'),
('ankaraguc','Ankaragücü'),('antalya','Antalyaspor'),('besiktas','Beşiktaş'),('bodrum','Bodrum FK'),('bursa','Bursaspor'),('denizli','Denizlispor'),('erzurum','Erzurumspor'),
('eyup','Eyüpspor'),('karagumruk','Fatih Karagümrük'),('fenerbah','Fenerbahçe'),('galatasaray','Galatasaray'),('gaziantepspor','Gaziantepspor'),('gaziantep','GAZI'),
('genclerbir','Gençlerbirliği'),('giresun','Giresunspor'),('goztepe','Göztepe'),('hatay','Hatayspor'),('karabuk','Karabükspor'),('kasimpasa','Kasımpaşa'),('kayseri','Kayserispor'),
('kocaeli','Kocaelispor'),('konya','Konyaspor'),('osmanli','Osmanlıspor'),('ankaraspor','Osmanlıspor'),('pendik','Pendikspor'),('samsun','Samsunspor'),('sivas','Sivasspor'),('trabzon','Trabzonspor'),
('malatya','Yeni Malatyaspor'),('rize','Çaykur Rizespor'),('umraniye','Ümraniyespor'),('basaksehir','İstanbul Başakşehir'),('istanbulspor','İstanbulspor')]
def std(name,sezon=None):
    f=fold(name)
    for k,v in KEYS:
        if k in f:
            if v=='GAZI':
                if sezon and sezon<'2019-20': return 'Gaziantepspor'
                return 'Gaziantep FK'
            return v
    return None
def league_teams():
    t=pd.read_csv(f'{ROOT}/data/team_season.csv'); t=t[t.ligde==True]
    return t[['takim','sezon']]
