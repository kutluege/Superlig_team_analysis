from common import *
import numpy as np
O=ROOT+'/data/agents/seyirci/'
S=pd.read_pickle(O+'.tmp_S.pkl')
rows=[]
for t,g in S.groupby('takim'):
    fan=g[g.sezon!='2020-21']; d=fan[fan.ort_seyirci.notna()]
    miss=fan[fan.ort_seyirci.isna()].sezon.tolist()
    part=d[d.secilen_kaynak.str.contains('kısmi')]
    notes=[f'{len(g)} lig sezonu ({", ".join(g.sezon)})']
    if (g.sezon=='2020-21').any(): notes.append('2020-21 seyircisiz (COVID) hariç')
    if (d.sezon=='2019-20').any(): notes.append('2019-20 yalnız Mart 2020 öncesi seyircili maçlar')
    if (d.sezon=='2021-22').any(): notes.append('2021-22 COVID kısıtlı sezon dahil (hariç versiyonu ayrı sütunda)')
    if len(part): notes.append('kısmi kapsamlı sezonlar: '+', '.join(f'{s} ({k})' for s,k in zip(part.sezon,part.mac_kapsami)))
    w=d[d.N>0]
    rows.append(dict(takim=t,sezon_sayisi_seyircili=len(d),
        ort_seyirci_10y=round(d.ort_seyirci.mean()) if len(d) else np.nan,
        ort_kapasite_10y=round(d.kapasite.mean()) if len(d) else np.nan,
        doluluk_10y=round(d.doluluk.mean(),3) if len(d) else np.nan,
        mac_agirlikli_ort=round((w.ort_seyirci*w.N).sum()/w.N.sum()) if len(w) else np.nan,
        eksik_sezonlar=', '.join(miss) if miss else 'yok',
        ort_seyirci_10y_2122_haric=round(d[d.sezon!='2021-22'].ort_seyirci.mean()) if len(d[d.sezon!='2021-22']) else np.nan,
        doluluk_10y_2122_haric=round(d[d.sezon!='2021-22'].doluluk.mean(),3) if len(d[d.sezon!='2021-22']) else np.nan,
        not_=' | '.join(notes)))
A=pd.DataFrame(rows).sort_values('ort_seyirci_10y',ascending=False)
A['ort_seyirci_10y_2122_haric']=A.ort_seyirci_10y_2122_haric.astype('Int64')
A.rename(columns={'not_':'not'}).to_csv(O+'seyirci_10yil.csv',index=False)
print(A.drop(columns='not_').to_string())
