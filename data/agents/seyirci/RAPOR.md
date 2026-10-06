# Süper Lig İç Saha Seyirci Araştırması (2016-17 … 2025-26)

Oluşturma tarihi: 2026-10-06. Ajan: seyirci alt-ajanı. Tüm ham sayfalar `cache/` altında saklıdır.

## Özet

- Toplam takım-sezon: **189** (10 sezon). 2020-21 sezonundaki 21 takım-sezon tamamen seyircisiz (COVID) olduğu için kapsam dışı.
- Seyircili 168 takım-sezonun **168** tanesi için ortalama bulundu (151 tam/sezon-kaynaklı, 17 kısmi maç kapsamlı). Verisiz: 0.
- 189 takım-sezonun tamamı (2020-21 dahil) sınıflandırıldı: 168 değer + 21 "seyircisiz" + 0 veri yok.
- Maç bazında: 2891 seyircili/oynanmış iç saha maçının **2445** tanesinin seyircisi biliniyor (kaynak dağılımı: transfermarkt=2395, seyircisiz (COVID)=502, yok=446, espn=35, wikipedia-kulüp=13, sofascore=2, hükmen/oynanmadı=1).

## Kullanılan kaynaklar

| Kaynak | Ne sağladı | Kapsam / not |
|---|---|---|
| Transfermarkt lig seyirci tablosu (`besucherzahlen/wettbewerb/TR1/saison_id/YYYY`) | Takım başına toplam/ortalama + stadyum kapasitesi | Ortalama yalnızca verisi girilmiş maçlar üzerinden (toplam/ortalama = maç sayısı). 2017-18 çok seyrek, 2025-26 yalnız ~Ocak 2026'ya kadar. Kapasite güncel stattır (sezona özgü değil). |
| Transfermarkt kulüp fikstür sayfaları (`spielplan/verein/ID/saison_id/YYYY/plus/1`) | Maç bazında seyirci | 168 takım-sezon sayfası indirildi; maç bazlı tablonun ana kaynağı. |
| ESPN API (`site.api.espn.com/.../soccer/tur.1/scoreboard?dates=`) | Maç bazında seyirci | 2016-17 çok iyi, diğer sezonlarda seyrek; 2025-26 ikinci yarısında bazı maçlar. 0 değerleri "bilinmiyor" sayıldı. |
| european-football-statistics.co.uk (EFS) | Sezon ortalaması | 2016-17, 17-18, 18-19, 19-20 (COVID öncesi), 22-23, 23-24, 24-25, 25-26 (05-01-2026 itibarıyla 8-9 maç). 2020-21 ve 2021-22 sayfası yok. |
| en.wikipedia sezon sayfaları | Sezon ortalaması tabloları (16-17, 17-18, 18-19, 22-23, 23-24, 24-25) + **sezona özgü stadyum kapasiteleri** (10 sezon) | 2023-24 tablosu 19 maç esaslı; bazı takımlarda EFS/TM'den farklı. |
| tr.wikipedia sezon sayfaları | 2018-19 seyirci tablosu (TM kopyası, kısmi maç sayılı) | Bağımsız kaynak sayılmadı. |
| en.wikipedia 2025-26 kulüp sezon sayfaları (GS, FB, BJK, TS) | Maç bazında seyirci | Yalnız Galatasaray sayfası tüm lig maçlarını içeriyor (17/17). |
| Sofascore (proje `data/raw/sofascore_mac_seyirci.csv`) | Maç bazında seyirci (seyrek) + stat kapasitesi | 2025-26 için API tekrar denendi: attendance alanı boş. |
| Türk basını (ajansspor, haberturk, viralspor; 27 Mayıs 2026) | 2025-26 "sezon sonu" takım ortalamaları | Değerler Transfermarkt'ın kısmi (~10 maç) ortalamalarıyla birebir aynı → bağımsız değil, yalnız `diger_kaynaklar`da kayıt. |
| TFF maç raporları (tff.org pageId=29) | — | Denendi: güncel maç raporlarında "Seyirci" alanı yok; kullanılamadı. |
| footystats, web.archive.org, fbref, worldfootball | — | Erişim engelli. |

## Yöntem

1. `data/matches.csv` iç saha maçları temel alındı. 2020-21 tüm maçlar ve 2019-20'de 12 Mart 2020 ve sonrası maçlar **seyircisiz** sayıldı; `hukmen=True` maçlar (ör. 2022-23 deprem sonrası Hatayspor/Gaziantep FK) hariç tutuldu.
2. Her maç için seyirci: Transfermarkt > ESPN > Wikipedia kulüp sayfası > Sofascore önceliğiyle seçildi (0 değerleri bilinmiyor sayıldı). Sonuç: `seyirci_mac_bazli.csv`.
3. Takım-sezon değeri (koordinatör kararıyla): EFS tam sezon ortalaması varsa **EFS** (2016-17, 17-18, 18-19, 19-20, 22-23, 23-24, 24-25); yoksa maç bazlı kapsam ≥%90 ise maç bazlı ortalama (`mac_birlesik`; 2021-22 tümü ve 2025-26 Galatasaray); değilse kısmi maç ortalaması (`mac_birlesik (kısmi)`, kapsam `n/N`; 2025-26). Tüm diğer kaynak değerleri `diger_kaynaklar` sütununda (`kaynak:değer (n=maç)`).
4. Kapasite: Wikipedia sezon sayfasındaki sezona özgü stat kapasitesi; doğrulama ajanının işaretlediği hatalı/çelişkili takım-sezonlarda o sezon gerçekten oynanan stada göre (stat değişimi sezon içindeyse seyircili maç sayısıyla ağırlıklı) düzeltildi (aşağıdaki tablo). Doluluk = ortalama seyirci / o sezonun kapasitesi. Sofascore venue alanı kapasite için kullanılmadı.
5. 10 yıllık: seyircili ve verili sezonların basit ortalaması (`ort_seyirci_10y`), kapasite ortalaması, sezonluk doluluk oranlarının ortalaması (`doluluk_10y`) ve seyircili iç saha maç sayısıyla ağırlıklı ortalama (`mac_agirlikli_ort`, 2019-20 için yalnız COVID öncesi maç sayısı). Ek sütunlar: `ort_seyirci_10y_2122_haric`, `doluluk_10y_2122_haric` (COVID kısıtlı 2021-22 hariç).

## Kapsam tablosu (takım × sezon)

Gösterim: sayı = seçilen ortalama; **E** EFS sezon ortalaması, **M** maç bazlı tam (≥%90), **K** kısmi (n/N bilinen maç), **C** seyircisiz (COVID), **?** veri yok, boş = ligde değil. 2021-22 sütunu COVID kısıtlı sezondur.

| Takım | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 |
|---|---|---|---|---|---|---|---|---|---|---|
| Adana Demirspor |  |  |  |  |  | 13.514 M | 16.929 E | 11.444 E | 5.173 E |  |
| Adanaspor | 4.594 E |  |  |  |  |  |  |  |  |  |
| Akhisarspor | 2.501 E | 5.795 E | 5.624 E |  |  |  |  |  |  |  |
| Alanyaspor | 4.541 E | 5.415 E | 4.774 E | 5.309 E | C | 1.934 M | 3.668 E | 3.074 E | 3.852 E | 4.310 K 9/17 |
| Altay |  |  |  |  |  | 4.105 M |  |  |  |  |
| Ankaragücü |  |  | 12.365 E | 10.773 E | C |  | 11.164 E | 7.606 E |  |  |
| Antalyaspor | 12.645 E | 14.554 E | 10.226 E | 11.534 E | C | 6.322 M | 10.414 E | 8.862 E | 7.996 E | 8.084 K 11/17 |
| Beşiktaş | 30.448 E | 29.562 E | 28.863 E | 28.542 E | C | 18.506 M | 32.775 E | 23.663 E | 28.393 E | 29.330 K 10/17 |
| Bodrum FK |  |  |  |  |  |  |  |  | 2.588 E |  |
| Bursaspor | 16.106 E | 20.723 E | 20.952 E |  |  |  |  |  |  |  |
| Denizlispor |  |  |  | 8.612 E | C |  |  |  |  |  |
| Erzurumspor |  |  | 11.161 E |  | C |  |  |  |  |  |
| Eyüpspor |  |  |  |  |  |  |  |  | 2.648 E | 3.860 K 10/17 |
| Fatih Karagümrük |  |  |  |  | C | 601 M | 1.353 E | 2.684 E |  | 1.686 K 10/17 |
| Fenerbahçe | 16.485 E | 29.035 E | 35.035 E | 39.352 E | C | 24.722 M | 38.322 E | 38.210 E | 33.571 E | 34.224 K 12/17 |
| Galatasaray | 21.351 E | 40.778 E | 36.160 E | 34.990 E | C | 21.425 M | 45.186 E | 43.133 E | 43.039 E | 44.654 M |
| Gaziantep FK |  |  |  | 8.343 E | C | 3.183 M | 4.679 E | 8.207 E | 6.237 E | 10.926 K 10/17 |
| Gaziantepspor | 4.236 E |  |  |  |  |  |  |  |  |  |
| Gençlerbirliği | 2.625 E | 3.262 E |  | 4.863 E | C |  |  |  |  | 11.357 K 10/17 |
| Giresunspor |  |  |  |  |  | 5.679 M | 6.331 E |  |  |  |
| Göztepe |  | 6.775 E | 8.013 E | 8.911 E | C | 8.978 M |  |  | 15.212 E | 19.163 K 12/17 |
| Hatayspor |  |  |  |  | C | 5.236 M | 7.147 E | 5.821 E | 4.235 E |  |
| Karabükspor | 4.422 E | 3.554 E |  |  |  |  |  |  |  |  |
| Kasımpaşa | 1.416 E | 2.450 E | 2.877 E | 3.076 E | C | 1.295 M | 2.269 E | 2.470 E | 2.172 E | 2.283 K 9/17 |
| Kayserispor | 5.524 E | 10.894 E | 8.694 E | 9.536 E | C | 4.563 M | 7.838 E | 7.297 E | 9.568 E | 10.962 K 10/17 |
| Kocaelispor |  |  |  |  |  |  |  |  |  | 19.774 K 11/17 |
| Konyaspor | 15.723 E | 12.151 E | 16.446 E | 16.005 E | C | 7.993 M | 10.307 E | 12.219 E | 12.700 E | 15.904 K 13/17 |
| Osmanlıspor | 3.792 E | 1.718 E |  |  |  |  |  |  |  |  |
| Pendikspor |  |  |  |  |  |  |  | 1.501 E |  |  |
| Samsunspor |  |  |  |  |  |  |  | 15.075 E | 16.099 E | 12.978 K 12/17 |
| Sivasspor |  | 10.414 E | 8.111 E | 11.912 E | C | 3.268 M | 4.215 E | 4.145 E | 5.957 E |  |
| Trabzonspor | 17.252 E | 20.128 E | 24.700 E | 29.833 E | C | 28.874 M | 21.694 E | 15.394 E | 17.210 E | 28.143 K 11/17 |
| Yeni Malatyaspor |  | 9.410 E | 7.672 E | 8.929 E | C | 1.811 M |  |  |  |  |
| Çaykur Rizespor | 3.369 E |  | 8.050 E | 6.439 E | C | 2.728 M |  | 5.103 E | 5.871 E | 6.614 K 12/17 |
| Ümraniyespor |  |  |  |  |  |  | 2.028 E |  |  |  |
| İstanbul Başakşehir | 3.208 E | 5.112 E | 3.860 E | 2.892 E | C | 1.034 M | 2.584 E | 2.597 E | 2.433 E | 4.174 K 9/17 |
| İstanbulspor |  |  |  |  |  |  | 2.475 E | 2.013 E |  |  |

### Sezon bazında kapsam

| Sezon | Takım | Değer var | Tam/sezon kaynağı | Kısmi | Veri yok | Bilinen maç / seyircili maç |
|---|---|---|---|---|---|---|
| 2016-17 | 18 | 18 | 18 | 0 | 0 | 277/306 |
| 2017-18 | 18 | 18 | 18 | 0 | 0 | 115/306 |
| 2018-19 | 18 | 18 | 18 | 0 | 0 | 220/306 |
| 2019-20 | 18 | 18 | 18 | 0 | 0 | 224/224 |
| 2020-21 | 21 | 0 | 0 | 0 | 0 | 0/0 |
| 2021-22 | 20 | 20 | 20 | 0 | 0 | 379/380 |
| 2022-23 | 19 | 19 | 19 | 0 | 0 | 313/342 |
| 2023-24 | 20 | 20 | 20 | 0 | 0 | 379/380 |
| 2024-25 | 19 | 19 | 19 | 0 | 0 | 340/341 |
| 2025-26 | 18 | 18 | 1 | 17 | 0 | 198/306 |

## Kaynaklar arası çelişkiler

Seçilen değerden >%10 farklı EFS/Wikipedia sezon değeri olan 5 takım-sezon:

| Takım | Sezon | Seçilen | Kaynak | Diğer kaynaklar |
|---|---|---|---|---|
| Antalyaspor | 2023-24 | 8862 | efs | mac_birlesik:8862 (n=19); transfermarkt:8862 (n=19); espn:8881 (n=19); efs:8862; wikipedia_sezon:11757 (n=19) |
| Göztepe | 2019-20 | 8911 | efs | mac_birlesik:10401 (n=11); transfermarkt:10401 (n=11); espn:10357 (n=11); efs:8911 |
| Hatayspor | 2024-25 | 4235 | efs | mac_birlesik:3795 (n=18); transfermarkt:3795 (n=18); espn:4236 (n=18); efs:4235; wikipedia_sezon:4235 |
| Samsunspor | 2023-24 | 15075 | efs | mac_birlesik:17119 (n=19); transfermarkt:17119 (n=19); espn:15064 (n=19); efs:15075; wikipedia_sezon:17119 (n=19) |
| Trabzonspor | 2017-18 | 20128 | efs | mac_birlesik:24850 (n=17); transfermarkt:24850 (n=17); espn:31152 (n=1); efs:20128; wikipedia_sezon:20128 |

## 10 yıllık takım ortalamaları

| # | Takım | Seyircili sezon (veri) | Ort. seyirci | Maç ağırlıklı | Ort. kapasite | Doluluk | 2021-22 hariç ort. | 2021-22 hariç doluluk |
|---|---|---|---|---|---|---|---|---|
| 1 | Galatasaray | 9 | 36.746 | 36.731 | 52.727 | %69.6 | 38.661 | %73.2 |
| 2 | Fenerbahçe | 9 | 32.106 | 31.904 | 48.339 | %66.7 | 33.029 | %68.6 |
| 3 | Beşiktaş | 9 | 27.787 | 27.631 | 42.448 | %65.5 | 28.947 | %68.2 |
| 4 | Trabzonspor | 9 | 22.581 | 22.342 | 40.826 | %55.3 | 21.794 | %53.4 |
| 5 | Kocaelispor | 1 | 19.774 | 19.774 | 34.829 | %56.8 | 19.774 | %56.8 |
| 6 | Bursaspor | 3 | 19.260 | 19.260 | 43.705 | %44.1 | 19.260 | %44.1 |
| 7 | Samsunspor | 3 | 14.717 | 14.756 | 33.714 | %43.6 | 14.717 | %43.6 |
| 8 | Konyaspor | 9 | 13.272 | 13.078 | 41.972 | %31.6 | 13.932 | %33.2 |
| 9 | Adana Demirspor | 4 | 11.765 | 11.784 | 32.897 | %35.4 | 11.182 | %33.8 |
| 10 | Göztepe | 6 | 11.175 | 11.309 | 17.110 | %63.9 | 11.615 | %67.5 |
| 11 | Erzurumspor | 1 | 11.161 | 11.161 | 23.277 | %47.9 | 11.161 | %47.9 |
| 12 | Ankaragücü | 4 | 10.477 | 10.378 | 20.045 | %52.5 | 10.477 | %52.5 |
| 13 | Antalyaspor | 9 | 10.071 | 9.948 | 31.929 | %31.4 | 10.539 | %32.9 |
| 14 | Denizlispor | 1 | 8.612 | 8.612 | 18.745 | %45.9 | 8.612 | %45.9 |
| 15 | Kayserispor | 9 | 8.320 | 8.223 | 32.863 | %25.3 | 8.789 | %26.7 |
| 16 | Yeni Malatyaspor | 4 | 6.956 | 6.645 | 27.044 | %25.7 | 8.670 | %32.1 |
| 17 | Gaziantep FK | 6 | 6.929 | 6.799 | 32.441 | %21.6 | 7.678 | %24.0 |
| 18 | Sivasspor | 7 | 6.860 | 6.560 | 27.561 | %24.9 | 7.459 | %27.1 |
| 19 | Giresunspor | 2 | 6.005 | 5.996 | 22.028 | %27.2 | 6.331 | %28.7 |
| 20 | Hatayspor | 4 | 5.610 | 5.608 | 25.248 | %22.2 | 5.734 | %22.7 |
| 21 | Gençlerbirliği | 4 | 5.527 | 5.568 | 19.622 | %27.9 | 5.527 | %27.9 |
| 22 | Çaykur Rizespor | 7 | 5.453 | 5.373 | 15.227 | %35.9 | 5.908 | %38.9 |
| 23 | Akhisarspor | 3 | 4.640 | 4.640 | 14.324 | %34.0 | 4.640 | %34.0 |
| 24 | Adanaspor | 1 | 4.594 | 4.594 | 36.117 | %12.7 | 4.594 | %12.7 |
| 25 | Gaziantepspor | 1 | 4.236 | 4.236 | 35.558 | %11.9 | 4.236 | %11.9 |
| 26 | Altay | 1 | 4.105 | 4.105 | 14.000 | %29.3 | — | — |
| 27 | Alanyaspor | 9 | 4.097 | 4.021 | 10.212 | %40.0 | 4.368 | %42.6 |
| 28 | Karabükspor | 2 | 3.988 | 3.988 | 14.200 | %28.0 | 3.988 | %28.0 |
| 29 | Eyüpspor | 2 | 3.254 | 3.237 | 13.797 | %23.6 | 3.254 | %23.6 |
| 30 | İstanbul Başakşehir | 9 | 3.099 | 3.064 | 17.321 | %17.8 | 3.358 | %19.3 |
| 31 | Osmanlıspor | 2 | 2.755 | 2.755 | 19.626 | %14.0 | 2.755 | %14.0 |
| 32 | Bodrum FK | 1 | 2.588 | 2.588 | 3.925 | %65.9 | 2.588 | %65.9 |
| 33 | Kasımpaşa | 9 | 2.256 | 2.220 | 14.137 | %15.9 | 2.377 | %16.8 |
| 34 | İstanbulspor | 2 | 2.244 | 2.238 | 4.488 | %50.0 | 2.244 | %50.0 |
| 35 | Ümraniyespor | 1 | 2.028 | 2.028 | 3.513 | %57.7 | 2.028 | %57.7 |
| 36 | Fatih Karagümrük | 4 | 1.581 | 1.581 | 77.162 | %2.1 | 1.908 | %2.5 |
| 37 | Pendikspor | 1 | 1.501 | 1.501 | 4.105 | %36.6 | 1.501 | %36.6 |

### 2021-22 (COVID kısıtlı) sezonunun etkisi

2021-22'de ligde olan takımlar için dahil/hariç farkı (dahil − hariç, %):

| Takım | Dahil | Hariç | Fark % | 2021-22 değeri |
|---|---|---|---|---|
| Yeni Malatyaspor | 6956 | 8670 | -19.8 | 1811 |
| Fatih Karagümrük | 1581 | 1908 | -17.1 | 601 |
| Gaziantep FK | 6929 | 7678 | -9.8 | 3183 |
| Sivasspor | 6860 | 7459 | -8.0 | 3268 |
| İstanbul Başakşehir | 3099 | 3358 | -7.7 | 1034 |
| Çaykur Rizespor | 5453 | 5908 | -7.7 | 2728 |
| Alanyaspor | 4097 | 4368 | -6.2 | 1934 |
| Kayserispor | 8320 | 8789 | -5.3 | 4563 |
| Giresunspor | 6005 | 6331 | -5.1 | 5679 |
| Kasımpaşa | 2256 | 2377 | -5.1 | 1295 |
| Galatasaray | 36746 | 38661 | -5.0 | 21425 |
| Konyaspor | 13272 | 13932 | -4.7 | 7993 |
| Antalyaspor | 10071 | 10539 | -4.4 | 6322 |
| Beşiktaş | 27787 | 28947 | -4.0 | 18506 |
| Göztepe | 11175 | 11615 | -3.8 | 8978 |
| Fenerbahçe | 32106 | 33029 | -2.8 | 24722 |
| Hatayspor | 5610 | 5734 | -2.2 | 5236 |
| Trabzonspor | 22581 | 21794 | +3.6 | 28874 |
| Adana Demirspor | 11765 | 11182 | +5.2 | 13514 |

Lig geneli 2021-22 takım ortalamalarının ortalaması: 8288; diğer seyircili sezonların: 12504.

## Kapasite düzeltmeleri (doğrulama ajanı bulgularına göre)

| Takım | Sezon | Kullanılan kapasite | Gerekçe/kaynak |
|---|---|---|---|
| Akhisarspor | 2017-18 | 14237 | maç ağırlıklı: Manisa 19 Mayıs 16.597 (8 maç, 28.01.2018 öncesi) + Spor Toto Akhisar 12.139 (9 maç) [Wikipedia] |
| Ankaragücü | 2018-19 | 18990 | maç ağırlıklı: Osmanlı Stadyumu 18.029 (9 maç, 28.01.2019 öncesi) + Eryaman 20.071 (8 maç) [Wikipedia stadyum makaleleri; doğrulama ajanı] |
| Fatih Karagümrük | 2020-21 | 76761 | Atatürk Olimpiyat Stadı (kulüp sezon sayfası/TM; lig sezon sayfasındaki Vefa değeri çelişkili — doğrulama ajanı notu). Belirsiz. |
| Fatih Karagümrük | 2023-24 | 77563 | Atatürk Olimpiyat Stadı (kulüp sezon sayfası/TM; lig sezon sayfasındaki Vefa değeri çelişkili — doğrulama ajanı notu). Belirsiz. |
| Göztepe | 2019-20 | 14467 | maç ağırlıklı (seyircili maçlar): Bornova 12.500 (8 maç) + Gürsel Aksel 19.713 (3 maç, 26.01.2020 sonrası) [Wikipedia] |
| Göztepe | 2020-21 | 19713 | Gürsel Aksel 19.713 (Wikipedia stadyum makalesi kapasite geçmişi; sezon sayfasındaki 25.035 hatalı görünüyor) |
| Göztepe | 2021-22 | 19713 | Gürsel Aksel 19.713 (Wikipedia stadyum makalesi kapasite geçmişi; sezon sayfasındaki 25.035 hatalı görünüyor) |
| Göztepe | 2025-26 | 23767 | Gürsel Aksel ek koltuklarla 23.767 (haberturk 3886529; TM 23.376) |
| Hatayspor | 2024-25 | 25497 | Mersin Stadyumu 25.497 (Hatayspor 2023-25 Mersin'de oynadı; Wikipedia 2023-24 sezon sayfası) |
| Pendikspor | 2023-24 | 4105 | Pendik Stadı 4.105 (TM/stadyum makalesi; sezon sayfası 2.500) |
| İstanbulspor | 2022-23 | 4488 | Esenyurt Necmi Kadıoğlu 4.488 (Wikipedia stadyum makalesi; sezon sayfasındaki 7.500 ve Sofascore şüpheli; TM 4.274) |
| İstanbulspor | 2023-24 | 4488 | Esenyurt Necmi Kadıoğlu 4.488 (Wikipedia stadyum makalesi; sezon sayfasındaki 7.500 ve Sofascore şüpheli; TM 4.274) |
### Kaynak uyumu (çapraz kontrol)

- **EFS ↔ maç bazlı (TM+ESPN, kapsam ≥%90):** 83 takım-sezonda iki değer de var; medyan mutlak fark **%0,04**, yalnız 7'sinde fark >%5 (Trabzonspor 2017-18 −%19 EFS düşük, Göztepe 2019-20, Samsunspor 2023-24, Hatayspor 2024-25, Ankaragücü 2023-24, Kayserispor 2024-25, Trabzonspor 2024-25). Koordinatör kararıyla bu sezonlarda EFS değeri tutuldu, öteki değerler `diger_kaynaklar`da.
- **Transfermarkt ↔ ESPN (maç bazında):** 2.048 ortak maç, 1.770'i birebir aynı, medyan fark %0, 67 maçta >%10 fark. ESPN ve TM büyük ölçüde aynı kaynaktan (muhtemelen resmi maç raporu) besleniyor → bağımsız iki ölçüm sayılmamalı.
- **Transfermarkt ↔ Wikipedia kulüp sayfası (Galatasaray 2025-26 vd.):** 23 ortak maç, 15'i aynı; Galatasaray iç saha maçlarında Wikipedia değerleri birkaç bin yüksek olabiliyor (ör. GS–Konyaspor 40.168 vs TM 34.700). GS 2025-26'nın 10 maçı TM, 7 maçı Wikipedia kulüp sayfasından geliyor → hafif yukarı sapma olası.
- **Basın 2025-26 "sezon sonu" listesi** (ajansspor/haberturk/viralspor, 27 Mayıs 2026) Transfermarkt'ın Ocak 2026'da kalan kısmi (~9-11 maç) ortalamalarıyla birebir aynı; tam sezon değil.
- **Wikipedia 2023-24 tablosu** bazı takımlarda hem EFS hem TM'den ayrışıyor (Antalyaspor 11.757 vs 8.862) → kullanılmadı, kayıtta tutuldu.

## Uyarılar / sınırlamalar

1. **2020-21** (21 takım-sezon) tamamen seyircisiz: `ort_seyirci` boş, `secilen_kaynak=seyircisiz`; 10 yıllık ortalamaya girmez.
2. **2019-20**: 12 Mart 2020 sonrası maçlar seyircisiz (COVID). EFS ve TM ortalamaları yalnız öncesindeki seyircili maçlardır (TM her takımda 11-13 maç, maç bazlı kapsam 224/224). Maç ağırlıklı ortalamada bu sezon yalnız seyircili maç sayısıyla ağırlıklandırıldı.
3. **2021-22 COVID kısıtlı sezon** (stada giriş HES + aşı/PCR şartına bağlı; doğrulama ajanına göre kapasite sınırları/kısmi seyirci). Lig geneli takım ortalaması 8.288 vs diğer sezonlarda 12.504. 10 yıllık tabloda hem dahil hem hariç değer verildi; çoğu takımda dahil etmek ortalamayı %3-20 düşürüyor (en çok Yeni Malatyaspor, Karagümrük). Bu sezonda EFS sayfası yok; değerler Transfermarkt maç bazlı (19/19, Başakşehir 18/19).
4. **2025-26 kısmi:** Transfermarkt ve EFS verisi Ocak 2026'da duruyor; ESPN ikinci yarıdan bazı maçları ekledi. 18 takımın 17'sinde kapsam 9-13/17 (yalnız Galatasaray 17/17). Bu takımların 2025-26 değeri sezonun ağırlıkla ilk yarısını yansıtır (`mac_birlesik (kısmi)`); 10 yıllık ortalamaya kısmi olarak dahil edildi ve `not` sütununda belirtildi. Sofascore ve TFF maç raporlarında 2025-26 seyirci bilgisi yok.
5. **EFS'nin maç kapsamı bilinmiyor.** 2016-17'de EFS değerleri TM'nin kısmi ortalamalarıyla aynı (ör. Galatasaray 21.351 = TM'nin 15 maçlık ortalaması). 2016-17'de Galatasaray/Fenerbahçe ortalamaları alışılmadık düşük (21.351/16.485) — kaynakta böyle; cezalı/seyircisiz maçlar ve eksik maç verisi içeriyor olabilir.
6. **Kapasite** sezona özgü resmi kaynakta yok; Wikipedia sezon sayfaları (yer yer hatalı) + stadyum makaleleri + doğrulama ajanının bulgularıyla düzeltildi. **Fatih Karagümrük** doluluk (~%2) Atatürk Olimpiyat Stadı'nın 77 bin kapasitesinden; 2023-24'te maçların Vefa'da (≈12.000) oynandığı iddiası doğrulanamadı — Vefa varsayılırsa 2023-24 doluluğu %22 olur. Eyüpspor 2024-26 Recep Tayyip Erdoğan Stadı (13.797) varsayıldı.
7. **0 seyirci** değerleri (ESPN'de sık) "bilinmiyor" sayıldı; ceza nedeniyle seyircisiz oynanan maçlar ayırt edilemedi (bu maçlar maç bazlı ortalamalarda dışarıda, EFS/TM ortalamalarında ise kaynağın tercihine bağlı).
8. Hükmen/oynanmamış maçlar (2022-23 deprem sonrası Hatayspor ve Gaziantep FK) seyircili maç sayısına girmedi; TM'de bu takımların 2022-23 kapsamı 10/10.
9. Hiçbir sayı uydurulmadı/tahmin edilmedi; proje dosyası `data/attendance_tahmini.csv`'deki tahminler kullanılmadı.

## Dosyalar

- `seyirci_sezonluk.csv` — 189 takım-sezon (istenen sütunlar).
- `seyirci_10yil.csv` — 37 takım, 10 yıllık ortalamalar (+ `ort_seyirci_10y_2122_haric`, `doluluk_10y_2122_haric`).
- `seyirci_mac_bazli.csv` — 3.394 maç: TM/ESPN/Wikipedia kulüp/Sofascore değerleri, seçilen değer, seyircisiz/hükmen bayrakları.
- Ara kaynak tabloları: `tm_raw.csv` (TM lig tablosu), `mac_tm.csv`, `mac_espn.csv`, `mac_wikiclub.csv`, `kaynak_efs.csv`, `kaynak_wiki_sezon.csv`, `kaynak_wiki_kapasite.csv`.
- Ham sayfalar: `cache/` (TM lig + 168 kulüp sayfası, 1.159 ESPN günlük JSON, EFS, Wikipedia, haber sayfaları).
- Betikler: `scripts/` (sıra: parse_tm_club → parse_espn → parse_efs → parse_wiki → parse_wikiclub → build → agg → rapor).
