from common import *
import numpy as np
O=ROOT+'/data/agents/seyirci/'
S=pd.read_pickle(O+'.tmp_S.pkl'); T=pd.read_pickle(O+'.tmp_T.pkl')
A=pd.read_csv(O+'seyirci_10yil.csv'); H=pd.read_csv(O+'seyirci_mac_bazli.csv')
seasons=[sezon(y) for y in range(2016,2026)]
fan=S[S.sezon!='2020-21']
n_total=len(S); n_fan=len(fan)
n_data=fan.ort_seyirci.notna().sum()
n_full=(fan.secilen_kaynak.isin(['mac_birlesik','wikipedia_sezon','efs'])).sum()
n_part=fan.secilen_kaynak.str.contains('kısmi').sum()
L=[]
L.append('# Süper Lig İç Saha Seyirci Araştırması (2016-17 … 2025-26)\n')
L.append(f'Oluşturma tarihi: 2026-10-06. Ajan: seyirci alt-ajanı. Tüm ham sayfalar `cache/` altında saklıdır.\n')
L.append('## Özet\n')
L.append(f'- Toplam takım-sezon: **{n_total}** (10 sezon). 2020-21 sezonundaki {n_total-n_fan} takım-sezon tamamen seyircisiz (COVID) olduğu için kapsam dışı.')
L.append(f'- Seyircili {n_fan} takım-sezonun **{n_data}** tanesi için ortalama bulundu ({n_full} tam/sezon-kaynaklı, {n_part} kısmi maç kapsamlı). Verisiz: {n_fan-n_data}.')
L.append(f'- 189 takım-sezonun tamamı (2020-21 dahil) sınıflandırıldı: {n_data} değer + {n_total-n_fan} "seyircisiz" + {n_fan-n_data} veri yok.')
L.append(f'- Maç bazında: {int(((~H.kapali)&(~H.hukmen)).sum())} seyircili/oynanmış iç saha maçının **{int(H.seyirci.notna().sum())}** tanesinin seyircisi biliniyor (kaynak dağılımı: '+', '.join(f'{k}={v}' for k,v in H.seyirci_kaynak.value_counts().items())+').\n')
L.append('## Kullanılan kaynaklar\n')
L.append('| Kaynak | Ne sağladı | Kapsam / not |\n|---|---|---|')
L.append('| Transfermarkt lig seyirci tablosu (`besucherzahlen/wettbewerb/TR1/saison_id/YYYY`) | Takım başına toplam/ortalama + stadyum kapasitesi | Ortalama yalnızca verisi girilmiş maçlar üzerinden (toplam/ortalama = maç sayısı). 2017-18 çok seyrek, 2025-26 yalnız ~Ocak 2026\'ya kadar. Kapasite güncel stattır (sezona özgü değil). |')
L.append('| Transfermarkt kulüp fikstür sayfaları (`spielplan/verein/ID/saison_id/YYYY/plus/1`) | Maç bazında seyirci | 168 takım-sezon sayfası indirildi; maç bazlı tablonun ana kaynağı. |')
L.append('| ESPN API (`site.api.espn.com/.../soccer/tur.1/scoreboard?dates=`) | Maç bazında seyirci | 2016-17 çok iyi, diğer sezonlarda seyrek; 2025-26 ikinci yarısında bazı maçlar. 0 değerleri "bilinmiyor" sayıldı. |')
L.append('| european-football-statistics.co.uk (EFS) | Sezon ortalaması | 2016-17, 17-18, 18-19, 19-20 (COVID öncesi), 22-23, 23-24, 24-25, 25-26 (05-01-2026 itibarıyla 8-9 maç). 2020-21 ve 2021-22 sayfası yok. |')
L.append('| en.wikipedia sezon sayfaları | Sezon ortalaması tabloları (16-17, 17-18, 18-19, 22-23, 23-24, 24-25) + **sezona özgü stadyum kapasiteleri** (10 sezon) | 2023-24 tablosu 19 maç esaslı; bazı takımlarda EFS/TM\'den farklı. |')
L.append('| tr.wikipedia sezon sayfaları | 2018-19 seyirci tablosu (TM kopyası, kısmi maç sayılı) | Bağımsız kaynak sayılmadı. |')
L.append('| en.wikipedia 2025-26 kulüp sezon sayfaları (GS, FB, BJK, TS) | Maç bazında seyirci | Yalnız Galatasaray sayfası tüm lig maçlarını içeriyor (17/17). |')
L.append('| Sofascore (proje `data/raw/sofascore_mac_seyirci.csv`) | Maç bazında seyirci (seyrek) + stat kapasitesi | 2025-26 için API tekrar denendi: attendance alanı boş. |')
L.append('| Türk basını (ajansspor, haberturk, viralspor; 27 Mayıs 2026) | 2025-26 "sezon sonu" takım ortalamaları | Değerler Transfermarkt\'ın kısmi (~10 maç) ortalamalarıyla birebir aynı → bağımsız değil, yalnız `diger_kaynaklar`da kayıt. |')
L.append('| TFF maç raporları (tff.org pageId=29) | — | Denendi: güncel maç raporlarında "Seyirci" alanı yok; kullanılamadı. |')
L.append('| footystats, web.archive.org, fbref, worldfootball | — | Erişim engelli. |\n')
L.append('## Yöntem\n')
L.append('1. `data/matches.csv` iç saha maçları temel alındı. 2020-21 tüm maçlar ve 2019-20\'de 12 Mart 2020 ve sonrası maçlar **seyircisiz** sayıldı; `hukmen=True` maçlar (ör. 2022-23 deprem sonrası Hatayspor/Gaziantep FK) hariç tutuldu.')
L.append('2. Her maç için seyirci: Transfermarkt > ESPN > Wikipedia kulüp sayfası > Sofascore önceliğiyle seçildi (0 değerleri bilinmiyor sayıldı). Sonuç: `seyirci_mac_bazli.csv`.')
L.append('3. Takım-sezon değeri (koordinatör kararıyla): EFS tam sezon ortalaması varsa **EFS** (2016-17, 17-18, 18-19, 19-20, 22-23, 23-24, 24-25); yoksa maç bazlı kapsam ≥%90 ise maç bazlı ortalama (`mac_birlesik`; 2021-22 tümü ve 2025-26 Galatasaray); değilse kısmi maç ortalaması (`mac_birlesik (kısmi)`, kapsam `n/N`; 2025-26). Tüm diğer kaynak değerleri `diger_kaynaklar` sütununda (`kaynak:değer (n=maç)`).')
L.append('4. Kapasite: Wikipedia sezon sayfasındaki sezona özgü stat kapasitesi; doğrulama ajanının işaretlediği hatalı/çelişkili takım-sezonlarda o sezon gerçekten oynanan stada göre (stat değişimi sezon içindeyse seyircili maç sayısıyla ağırlıklı) düzeltildi (aşağıdaki tablo). Doluluk = ortalama seyirci / o sezonun kapasitesi. Sofascore venue alanı kapasite için kullanılmadı.')
L.append('5. 10 yıllık: seyircili ve verili sezonların basit ortalaması (`ort_seyirci_10y`), kapasite ortalaması, sezonluk doluluk oranlarının ortalaması (`doluluk_10y`) ve seyircili iç saha maç sayısıyla ağırlıklı ortalama (`mac_agirlikli_ort`, 2019-20 için yalnız COVID öncesi maç sayısı). Ek sütunlar: `ort_seyirci_10y_2122_haric`, `doluluk_10y_2122_haric` (COVID kısıtlı 2021-22 hariç).\n')
# coverage table
L.append('## Kapsam tablosu (takım × sezon)\n')
L.append('Gösterim: sayı = seçilen ortalama; **E** EFS sezon ortalaması, **M** maç bazlı tam (≥%90), **K** kısmi (n/N bilinen maç), **C** seyircisiz (COVID), **?** veri yok, boş = ligde değil. 2021-22 sütunu COVID kısıtlı sezondur.\n')
L.append('| Takım | '+' | '.join(seasons)+' |'); L.append('|---|'+'---|'*len(seasons))
code={'mac_birlesik':'M','wikipedia_sezon':'W','efs':'E','seyircisiz':'C','yok':'?'}
for t in sorted(S.takim.unique()):
    cells=[]
    for s in seasons:
        r=S[(S.takim==t)&(S.sezon==s)]
        if not len(r): cells.append(''); continue
        r=r.iloc[0]
        c=code.get(r.secilen_kaynak,'K')
        if c=='C': cells.append('C')
        elif c=='?': cells.append('?')
        elif c=='K': cells.append(f'{int(r.ort_seyirci):,} K {r.mac_kapsami}'.replace(',','.'))
        else: cells.append(f'{int(r.ort_seyirci):,} {c}'.replace(',','.'))
    L.append(f'| {t} | '+' | '.join(cells)+' |')
L.append('')
# per-season coverage summary
L.append('### Sezon bazında kapsam\n')
L.append('| Sezon | Takım | Değer var | Tam/sezon kaynağı | Kısmi | Veri yok | Bilinen maç / seyircili maç |'); L.append('|---|---|---|---|---|---|---|')
for s in seasons:
    g=S[S.sezon==s]; h=H[(H.sezon==s)&(~H.kapali)&(~H.hukmen)]
    L.append(f'| {s} | {len(g)} | {g.ort_seyirci.notna().sum()} | {g.secilen_kaynak.isin(["mac_birlesik","wikipedia_sezon","efs"]).sum()} | {g.secilen_kaynak.str.contains("kısmi").sum()} | {(g.secilen_kaynak=="yok").sum()} | {h.seyirci.notna().sum()}/{len(h)} |')
L.append('')
# conflicts
L.append('## Kaynaklar arası çelişkiler\n')
c=S[S.not_.str.contains('ÇELİŞKİ')]
L.append(f'Seçilen değerden >%10 farklı EFS/Wikipedia sezon değeri olan {len(c)} takım-sezon:\n')
L.append('| Takım | Sezon | Seçilen | Kaynak | Diğer kaynaklar |'); L.append('|---|---|---|---|---|')
for _,r in c.iterrows(): L.append(f'| {r.takim} | {r.sezon} | {int(r.ort_seyirci)} | {r.secilen_kaynak} | {r.diger_kaynaklar} |')
L.append('')

# 10y
fmt=lambda v: '—' if pd.isna(v) else f'{int(v):,}'
pct=lambda v: '—' if pd.isna(v) else f'%{v*100:.1f}'
L.append('## 10 yıllık takım ortalamaları\n')
L.append('| # | Takım | Seyircili sezon (veri) | Ort. seyirci | Maç ağırlıklı | Ort. kapasite | Doluluk | 2021-22 hariç ort. | 2021-22 hariç doluluk |'); L.append('|---|---|---|---|---|---|---|---|---|')
for i,(_,r) in enumerate(A.iterrows(),1):
    L.append(f'| {i} | {r.takim} | {r.sezon_sayisi_seyircili} | {int(r.ort_seyirci_10y):,} | {int(r.mac_agirlikli_ort):,} | {int(r.ort_kapasite_10y):,} | %{r.doluluk_10y*100:.1f} | {fmt(r.ort_seyirci_10y_2122_haric)} | {pct(r.doluluk_10y_2122_haric)} |'.replace(',','.'))
L.append('')
L.append('### 2021-22 (COVID kısıtlı) sezonunun etkisi\n')
B=A[(A.ort_seyirci_10y!=A.ort_seyirci_10y_2122_haric)&A.ort_seyirci_10y_2122_haric.notna()].copy(); B['fark']=(B.ort_seyirci_10y-B.ort_seyirci_10y_2122_haric)/B.ort_seyirci_10y_2122_haric*100
L.append('2021-22\'de ligde olan takımlar için dahil/hariç farkı (dahil − hariç, %):\n')
L.append('| Takım | Dahil | Hariç | Fark % | 2021-22 değeri |'); L.append('|---|---|---|---|---|')
for _,r in B.sort_values('fark').iterrows():
    v=S[(S.takim==r.takim)&(S.sezon=='2021-22')].ort_seyirci.iloc[0]
    L.append(f'| {r.takim} | {int(r.ort_seyirci_10y)} | {int(r.ort_seyirci_10y_2122_haric)} | {r.fark:+.1f} | {int(v)} |')
L.append(f'\nLig geneli 2021-22 takım ortalamalarının ortalaması: {int(S[S.sezon=="2021-22"].ort_seyirci.mean())}; diğer seyircili sezonların: {int(fan[fan.sezon!="2021-22"].ort_seyirci.mean())}.\n')
# capacity overrides
L.append('## Kapasite düzeltmeleri (doğrulama ajanı bulgularına göre)\n')
L.append('| Takım | Sezon | Kullanılan kapasite | Gerekçe/kaynak |'); L.append('|---|---|---|---|')
for _,r in S[S.kap_kaynak.str.contains('ağırlıklı|makale|Olimpiyat|Mersin|Pendik|haberturk|Gürsel',regex=True)].iterrows():
    L.append(f'| {r.takim} | {r.sezon} | {int(r.kapasite)} | {r.kap_kaynak} |')
L.append('')
open(O+'.rapor_auto.md','w').write('\n'.join(L))
print('\n'.join(L)[:3000])
