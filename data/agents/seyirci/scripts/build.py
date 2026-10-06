from common import *
import numpy as np
O=ROOT+'/data/agents/seyirci/'
m,_=home_counts()
m['hukmen']=m.hukmen.astype(str).str.lower().eq('true')
lt=league_teams()
# ---------- per-match ----------
H=m[['sezon','tarih','ev','deplasman','kapali','hukmen']].copy()
tmm=pd.read_csv(O+'mac_tm.csv').rename(columns={'takim':'ev','dep':'deplasman'})[['sezon','ev','deplasman','tm_seyirci','tm_url']].drop_duplicates(['sezon','ev','deplasman'])
es=pd.read_csv(O+'mac_espn.csv')[['sezon','ev','deplasman','espn_seyirci','espn_url']]
wc=pd.read_csv(O+'mac_wikiclub.csv')[['sezon','ev','deplasman','wiki_seyirci','wiki_url']]
so=pd.read_csv(ROOT+'/data/raw/sofascore_mac_seyirci.csv'); so['sezon']=so.sezon_yil.map(sezon)
so=so.rename(columns={'seyirci':'sofa_seyirci'}); so['sofa_url']='https://api.sofascore.com/api/v1/event/'+so.sofascore_id.astype('Int64').astype(str)
so=so[['sezon','ev','deplasman','sofa_seyirci','sofa_url','kapasite','stadyum']].rename(columns={'kapasite':'sofa_kapasite','stadyum':'sofa_stadyum'}).drop_duplicates(['sezon','ev','deplasman'])
for d in [tmm,es,wc,so]: H=H.merge(d,on=['sezon','ev','deplasman'],how='left')
def pick(r):
    if r.kapali: return pd.Series([np.nan,'seyircisiz (COVID)'])
    if r.hukmen: return pd.Series([np.nan,'hükmen/oynanmadı'])
    for c,n in [('tm_seyirci','transfermarkt'),('espn_seyirci','espn'),('wiki_seyirci','wikipedia-kulüp'),('sofa_seyirci','sofascore')]:
        v=r[c]
        if pd.notna(v) and v>0: return pd.Series([v,n])
    return pd.Series([np.nan,'yok'])
H[['seyirci','seyirci_kaynak']]=H.apply(pick,axis=1)
H.to_csv(O+'seyirci_mac_bazli.csv',index=False)
# ---------- team-season ----------
g=H.groupby(['ev','sezon']).agg(ev_mac=('tarih','size'),kapali=('kapali','sum'),hukmen=('hukmen','sum'),n_bilinen=('seyirci','count'),mac_ort=('seyirci','mean'),
     n_tm=('tm_seyirci',lambda x:(x>0).sum()),n_espn=('espn_seyirci',lambda x:(x>0).sum()),n_wiki=('wiki_seyirci',lambda x:(x>0).sum()),n_sofa=('sofa_seyirci',lambda x:(x>0).sum()),
     sofa_kap=('sofa_kapasite',lambda x:x.mode().iloc[0] if x.notna().any() else np.nan),tmu=('tm_url',lambda x:x.dropna().iloc[0] if x.notna().any() else None),sofa_stad=('sofa_stadyum',lambda x:x.mode().iloc[0] if x.notna().any() else None)).reset_index().rename(columns={'ev':'takim'})
g['N']=g.ev_mac-g.kapali-g.hukmen
# TM-only per-match mean (for conflicts)
tmonly=H[(~H.kapali)&(~H.hukmen)&(H.tm_seyirci>0)].groupby(['ev','sezon']).tm_seyirci.mean().rename('tm_ort').reset_index().rename(columns={'ev':'takim'})
espnonly=H[(~H.kapali)&(~H.hukmen)&(H.espn_seyirci>0)].groupby(['ev','sezon']).espn_seyirci.mean().rename('espn_ort').reset_index().rename(columns={'ev':'takim'})
T=lt.merge(g,on=['takim','sezon'],how='left').merge(tmonly,how='left').merge(espnonly,how='left')
efs=pd.read_csv(O+'kaynak_efs.csv'); ws=pd.read_csv(O+'kaynak_wiki_sezon.csv'); kap=pd.read_csv(O+'kaynak_wiki_kapasite.csv')
att=pd.read_csv(ROOT+'/data/attendance.csv'); aw=att[(att.ligde==True)&(att.kaynak=='wikipedia')][['takim','sezon','ort_seyirci','kapasite']].rename(columns={'ort_seyirci':'wikiproj_ort','kapasite':'proj_kap'})
ak=att[(att.ligde==True)][['takim','sezon','kapasite']].rename(columns={'kapasite':'proj_kap_all'})
tm=pd.read_csv(O+'tm_raw.csv'); tm=tm[['takim','sezon','ort','n','kapasite','stadyum']].rename(columns={'ort':'tmagg_ort','n':'tmagg_n','kapasite':'tm_kap','stadyum':'tm_stad'})
haber=dict(zip(['Galatasaray','Fenerbahçe','Beşiktaş','Trabzonspor','Kocaelispor','Göztepe','Konyaspor','Samsunspor','Gaziantep FK','Gençlerbirliği','Kayserispor','Antalyaspor','Çaykur Rizespor','Alanyaspor','Eyüpspor','İstanbul Başakşehir','Kasımpaşa','Fatih Karagümrük'],
 [41661,33934,28163,26991,19189,18363,12376,11111,10926,10072,10057,7676,5984,4310,3860,4174,2283,1686]))
T=T.merge(efs[['takim','sezon','efs_ort','efs_mac','efs_url']],how='left').merge(ws,how='left').merge(kap,how='left').merge(aw,how='left').merge(ak,how='left').merge(tm,how='left')
T['haber_ort']=[haber.get(t) if s=='2025-26' else np.nan for t,s in zip(T.takim,T.sezon)]
# wiki season value: en season page table, else project attendance.csv (wikipedia)
T['wiki_ort']=T.wiki_ort.fillna(T.wikiproj_ort)
T.loc[T.wiki_url.isna()&T.wiki_ort.notna(),'wiki_url']=[f'https://en.wikipedia.org/wiki/{s[:4]}%E2%80%93{s[5:]}_S%C3%BCper_Lig' for s in T.loc[T.wiki_url.isna()&T.wiki_ort.notna(),'sezon']]
def wmix(team,sz,cut,cap_before,cap_after):
    h=m[(m.ev==team)&(m.sezon==sz)&(~m.kapali)&(~m.hukmen)]
    nb=(h.tarih<cut).sum(); na=(h.tarih>=cut).sum()
    return round((nb*cap_before+na*cap_after)/(nb+na)), nb, na
def cap_override(team,sz):
    if team=='Ankaragücü' and sz=='2018-19':
        c,nb,na=wmix(team,sz,'2019-01-28',18029,20071); return c,f'maç ağırlıklı: Osmanlı Stadyumu 18.029 ({nb} maç, 28.01.2019 öncesi) + Eryaman 20.071 ({na} maç) [Wikipedia stadyum makaleleri; doğrulama ajanı]'
    if team=='Akhisarspor' and sz=='2017-18':
        c,nb,na=wmix(team,sz,'2018-01-28',16597,12139); return c,f'maç ağırlıklı: Manisa 19 Mayıs 16.597 ({nb} maç, 28.01.2018 öncesi) + Spor Toto Akhisar 12.139 ({na} maç) [Wikipedia]'
    if team=='Göztepe' and sz=='2019-20':
        c,nb,na=wmix(team,sz,'2020-01-26',12500,19713); return c,f'maç ağırlıklı (seyircili maçlar): Bornova 12.500 ({nb} maç) + Gürsel Aksel 19.713 ({na} maç, 26.01.2020 sonrası) [Wikipedia]'
    if team=='Göztepe' and sz in ('2020-21','2021-22'): return 19713,'Gürsel Aksel 19.713 (Wikipedia stadyum makalesi kapasite geçmişi; sezon sayfasındaki 25.035 hatalı görünüyor)'
    if team=='Göztepe' and sz=='2025-26': return 23767,'Gürsel Aksel ek koltuklarla 23.767 (haberturk 3886529; TM 23.376)'
    if team=='Fatih Karagümrük' and sz in ('2020-21','2023-24'): return 76761 if sz=='2020-21' else 77563,'Atatürk Olimpiyat Stadı (kulüp sezon sayfası/TM; lig sezon sayfasındaki Vefa değeri çelişkili — doğrulama ajanı notu). Belirsiz.'
    if team=='İstanbulspor' and sz in ('2022-23','2023-24'): return 4488,'Esenyurt Necmi Kadıoğlu 4.488 (Wikipedia stadyum makalesi; sezon sayfasındaki 7.500 ve Sofascore şüpheli; TM 4.274)'
    if team=='Pendikspor' and sz=='2023-24': return 4105,'Pendik Stadı 4.105 (TM/stadyum makalesi; sezon sayfası 2.500)'
    if team=='Hatayspor' and sz=='2024-25': return 25497,'Mersin Stadyumu 25.497 (Hatayspor 2023-25 Mersin\'de oynadı; Wikipedia 2023-24 sezon sayfası)'
    return None
out=[]
for _,r in T.iterrows():
    sz=r.sezon; N=int(r.N) if pd.notna(r.N) else None
    # capacity
    if pd.notna(r.wiki_kapasite): kp,kk=r.wiki_kapasite,'wikipedia sezon sayfası'
    elif pd.notna(r.proj_kap_all): kp,kk=r.proj_kap_all,'proje attendance.csv'
    elif pd.notna(r.tm_kap): kp,kk=r.tm_kap,'transfermarkt (güncel kapasite)'
    else: kp,kk=r.sofa_kap,'sofascore venue'
    ov=cap_override(r.takim,sz)
    if ov: kp,kk=ov
    notes=[]
    others=[]
    def add(k,v,extra=''):
        if pd.notna(v): others.append(f'{k}:{int(round(v))}{extra}')
    add('mac_birlesik',r.mac_ort,f' (n={int(r.n_bilinen)})' if pd.notna(r.n_bilinen) else '')
    add('transfermarkt',r.tm_ort,f' (n={int(r.n_tm)})' if pd.notna(r.n_tm) else '')
    add('espn',r.espn_ort,f' (n={int(r.n_espn)})' if pd.notna(r.n_espn) else '')
    add('efs',r.efs_ort,f' (n={int(r.efs_mac)})' if pd.notna(r.efs_mac) else '')
    add('wikipedia_sezon',r.wiki_ort,f' (n={int(r.wiki_mac)})' if pd.notna(r.wiki_mac) else '')
    add('haber(TM tabanlı)',r.haber_ort)
    if sz=='2020-21':
        out.append(dict(takim=r.takim,sezon=sz,ort_seyirci=np.nan,kapasite=kp,doluluk=np.nan,mac_kapsami=f'0/{int(r.ev_mac)} (tüm maçlar seyircisiz)',secilen_kaynak='seyircisiz',kaynak_url='',diger_kaynaklar='',not_='COVID-19: 2020-21 sezonu tamamen seyircisiz oynandı; ortalamalara dahil edilmedi.',kap_kaynak=kk,N=0,n=0)); continue
    cov=(r.n_bilinen/N) if N else 0
    nb=int(r.n_bilinen) if pd.notna(r.n_bilinen) else 0
    efs_partial=pd.notna(r.efs_mac) and r.efs_mac<N
    if pd.notna(r.efs_ort) and not efs_partial:
        val=r.efs_ort; src='efs'; url=r.efs_url; kc=f'EFS sezon ort. (maç sayısı belirtilmemiş); maç bazlı bilinen {nb}/{N}'
        notes.append('EFS sezon ortalaması seçildi (koordinatör kararı: EFS tam sezon kaynağı); TM/ESPN maç bazlı değer diger_kaynaklar\'da')
    elif pd.notna(r.wiki_ort) and (pd.isna(r.wiki_mac) or r.wiki_mac>=N):
        val=r.wiki_ort; src='wikipedia_sezon'; url=r.wiki_url; kc=f'Wikipedia sezon ort.; maç bazlı bilinen {nb}/{N}'
    elif cov>=0.9:
        val=r.mac_ort; src='mac_birlesik'; kc=f'{nb}/{N}'; url=r.tmu if isinstance(r.tmu,str) else ''
        notes.append('Maç bazlı birleşik ortalama (öncelik TM > ESPN > Wikipedia kulüp > Sofascore); maç listesi seyirci_mac_bazli.csv')
    elif nb>0 and not (pd.notna(r.efs_mac) and r.efs_mac>nb):
        val=r.mac_ort; src='mac_birlesik (kısmi)'; kc=f'{nb}/{N}'; url=r.tmu if isinstance(r.tmu,str) else ''
        notes.append(f'KISMİ: yalnızca {nb}/{N} iç saha maçının seyircisi biliniyor (maç bazlı: TM+ESPN+Wikipedia kulüp+Sofascore)')
    elif pd.notna(r.efs_ort):
        val=r.efs_ort; src='efs (kısmi)'; url=r.efs_url; kc=f'{int(r.efs_mac)}/{N}'
        notes.append(f'KISMİ: EFS {int(r.efs_mac)} maçlık ara ortalama')
    else:
        val=np.nan; src='yok'; kc=f'0/{N}'; url=''; notes.append('Hiçbir kaynakta veri bulunamadı')
    if sz=='2021-22': notes.append('2021-22 COVID kısıtlı sezon (stada giriş HES kodu + aşı/PCR şartına bağlıydı; seyirci talebi baskılanmış) — 10 yıllık ortalamada ayrıca hariç versiyonu verildi')
    if sz=='2019-20': notes.append(f'2019-20: 12 Mart 2020 sonrası {int(r.kapali)} iç saha maçı seyircisiz (COVID) — hariç tutuldu')
    if r.hukmen: notes.append(f'{int(r.hukmen)} hükmen/oynanmamış maç hariç')
    # conflict
    for k,v in [('efs',r.efs_ort if not efs_partial else np.nan),('wikipedia_sezon',r.wiki_ort),('mac_birlesik(>=%90 kapsam)',r.mac_ort if cov>=0.9 else np.nan),('transfermarkt',r.tm_ort if pd.notna(r.n_tm) and N and r.n_tm/N>=0.9 else np.nan)]:
        if pd.notna(v) and pd.notna(val) and not src.startswith(k[:6]) and abs(v-val)/val>0.10: notes.append(f'ÇELİŞKİ: {k}={int(v)} seçilen değerden %{abs(v-val)/val*100:.0f} farklı')
    if kk!='wikipedia sezon sayfası': notes.append(f'kapasite kaynağı: {kk}')
    out.append(dict(takim=r.takim,sezon=sz,ort_seyirci=round(val) if pd.notna(val) else np.nan,kapasite=kp,doluluk=round(val/kp,3) if pd.notna(val) and kp else np.nan,mac_kapsami=kc,secilen_kaynak=src,kaynak_url=url,diger_kaynaklar='; '.join(others),not_=' | '.join(notes),kap_kaynak=kk,N=N,n=int(r.n_bilinen) if pd.notna(r.n_bilinen) else 0))
S=pd.DataFrame(out)
S.to_pickle(O+'.tmp_S.pkl'); T.to_pickle(O+'.tmp_T.pkl')
S2=S.copy(); S2['ort_seyirci']=S2.ort_seyirci.astype('Int64'); S2['kapasite']=S2.kapasite.round().astype('Int64')
S2.rename(columns={'not_':'not'})[['takim','sezon','ort_seyirci','kapasite','doluluk','mac_kapsami','secilen_kaynak','kaynak_url','diger_kaynaklar','not']].to_csv(O+'seyirci_sezonluk.csv',index=False)
print(S.secilen_kaynak.value_counts())
