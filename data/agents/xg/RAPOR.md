# Süper Lig xG Raporu (2016-17 … 2025-26)

Üretim: `fetch_xg.py` (Sofascore maç bazlı çekim, önbellekli) + `aggregate_xg.py` (birleştirme). Ham veri: `cache/sofa/*.json`, `cache/fotmob/*.json`.

## 1. Sezon bazlı kapsam

| Sezon | Takım | xG olan takım | Maç kapsamı (maç-takım) | Kaynak |
|---|---|---|---|---|
| 2016-17 | 18 | 0 | 0/612 | **Kaynak yok (boş bırakıldı)** |
| 2017-18 | 18 | 0 | 0/612 | **Kaynak yok (boş bırakıldı)** |
| 2018-19 | 18 | 0 | 0/612 | **Kaynak yok (boş bırakıldı)** |
| 2019-20 | 18 | 0 | 0/612 | **Kaynak yok (boş bırakıldı)** |
| 2020-21 | 21 | 0 | 0/840 | **Kaynak yok (boş bırakıldı)** |
| 2021-22 | 20 | 0 | 0/760 | **Kaynak yok (boş bırakıldı)** |
| 2022-23 | 19 | 19 | 626/684 | FotMob sezon toplamı (Sofascore xG yok) |
| 2023-24 | 20 | 20 | 754/760 | Sofascore maç bazlı + FotMob çapraz kontrol |
| 2024-25 | 19 | 19 | 682/684 | Sofascore maç bazlı + FotMob çapraz kontrol |
| 2025-26 | 18 | 18 | 612/612 | Sofascore maç bazlı + FotMob çapraz kontrol |

`xg_mac.csv`: 1024 maç (yalnız Sofascore, 2023-24 → 2025-26). 2016-17 … 2021-22 için hiçbir takım-sezonda xG değeri **yoktur**; bu 6 sezon boş bırakılmıştır.

### Kaynak bulguları

- **Sofascore** (`/event/{id}/statistics`, dönem ALL, `expectedGoals`): her sezondan rastgele 25 maç yoklandı (tohum sabit). 2016-17 … 2022-23: 0/25 (xG alanı yok); 2023-24, 2024-25, 2025-26: 25/25. Bu yüzden yalnız 2023-24 sonrası tam çekildi (1.026 maç). Hata günlüğü (`fetch_errors.log`) boş: HTTP hatası yok.
- **FotMob** (`data.fotmob.com/stats/71/season/{id}/expected_goals_team.json` ve `expected_goals_conceded_team.json`): 2022-23 → 2025-26 için tüm takımlar neredeyse tam maçla (`StatValueCount`≈oynanan). 2018-19 … 2021-22 için yalnız 1-5 maçlık kırıntı (ör. 2021-22 Yeni Malatyaspor 4/38, 2020-21 yalnız 2 takım 1’er maç); bu değerler sezon toplamı olarak anlamsız olduğundan **kullanılmadı** (ham hali `fotmob_sezon_ham.csv`). 2017-18 (403) ve 2016-17 (sayfada sezon yok) alınamadı.
- understat Türkiye’yi kapsamıyor, fbref 403; footystats ve fotmob.com web arama/WebFetch aracından egress proxy ile engelli, footystats’a curl de 403 (bot koruması). Web aramasında 2016-2022 için tam bir takım xG tablosu bulunamadı (yalnız 2021-22 ara dönem için tek tük haber alıntısı; doğrulanabilir bir tablo değil, kullanılmadı).

## 2. Kaynaklar arası çapraz kontrol (Sofascore toplamı − FotMob sezon toplamı)

Sofascore toplamı yalnız xG değeri olan maçlardan toplanır; FotMob’un sezon toplamı kendi maç sayısıyla verilir. Maç sayıları farklıysa fark kısmen kapsamdan gelir. Sezon özeti:

| Sezon | Takım | Ort. fark xG | Ort. fark xGA | En büyük mutlak fark xG | Ort. fark xG/maç |
|---|---|---|---|---|---|
| 2023-24 | 20 | -0.34 | -0.34 | 3.18 | +0.000 |
| 2024-25 | 19 | -0.10 | -0.10 | 1.19 | -0.003 |
| 2025-26 | 18 | -0.01 | -0.01 | 0.08 | -0.000 |

Takım-sezon bazında fark (|xG farkı| ≥ 0,5 olanlar):

| Sezon | Takım | Sofa maç | FotMob maç | Sofa xG | FotMob xG | Fark | Sofa xGA | FotMob xGA | Fark |
|---|---|---|---|---|---|---|---|---|---|
| 2024-25 | Adana Demirspor | 35 | 35 | 30.65 | 30.6 | +0.05 | 79.75 | 80.9 | -1.15 |
| 2024-25 | Galatasaray | 35 | 35 | 77.91 | 79.1 | -1.19 | 38.88 | 38.9 | -0.02 |
| 2023-24 | Konyaspor | 37 | 38 | 38.80 | 39.4 | -0.60 | 50.12 | 52.1 | -1.98 |
| 2024-25 | Samsunspor | 36 | 36 | 50.25 | 50.2 | +0.05 | 40.59 | 41.2 | -0.61 |
| 2023-24 | Sivasspor | 37 | 38 | 40.26 | 41.1 | -0.84 | 49.78 | 50.8 | -1.02 |
| 2023-24 | Trabzonspor | 37 | 38 | 45.84 | 47.3 | -1.46 | 46.83 | 47.5 | -0.67 |
| 2023-24 | Çaykur Rizespor | 36 | 38 | 47.42 | 50.6 | -3.18 | 55.27 | 56.6 | -1.33 |
| 2024-25 | Çaykur Rizespor | 36 | 36 | 54.79 | 55.5 | -0.71 | 46.01 | 46.1 | -0.09 |
| 2023-24 | İstanbulspor | 37 | 38 | 37.84 | 38.5 | -0.66 | 69.67 | 71.1 | -1.43 |

Tüm takım-sezonlar: `capraz_kontrol.csv`. 2025-26’da iki kaynak neredeyse özdeş (|fark| ≤ 0,08); farklar eski sezonlarda ve Sofascore’da xG’si eksik maçı olan takımlarda toplanıyor (Sofascore’da maç eksiği → toplam FotMob’dan düşük). Her iki kaynak da aynı veri sağlayıcıya (Opta türevi model) dayanıyor olabilir, bu nedenle uyum bağımsız doğrulama sayılmamalıdır. 2022-23’te çapraz kontrol mümkün değil (tek kaynak).

## 3. 10 yıllık özet (xG’si olan sezonlar toplamı)

| Takım | Sezon | Maç | xG/maç | xGA/maç | Fark/maç | Sezonlar |
|---|---|---|---|---|---|---|
| Fenerbahçe | 4 | 142 | 2.18 | 0.89 | +1.29 | 2022-23,2023-24,2024-25,2025-26 |
| Galatasaray | 4 | 141 | 2.12 | 0.94 | +1.18 | 2022-23,2023-24,2024-25,2025-26 |
| Beşiktaş | 4 | 142 | 1.67 | 1.06 | +0.61 | 2022-23,2023-24,2024-25,2025-26 |
| Göztepe | 2 | 70 | 1.62 | 1.13 | +0.49 | 2024-25,2025-26 |
| Trabzonspor | 4 | 142 | 1.44 | 1.30 | +0.14 | 2022-23,2023-24,2024-25,2025-26 |
| İstanbul Başakşehir | 4 | 142 | 1.42 | 1.30 | +0.12 | 2022-23,2023-24,2024-25,2025-26 |
| Çaykur Rizespor | 3 | 106 | 1.41 | 1.40 | +0.01 | 2023-24,2024-25,2025-26 |
| Ümraniyespor | 1 | 34 | 1.37 | 1.76 | -0.39 | 2022-23 |
| Adana Demirspor | 3 | 107 | 1.35 | 1.74 | -0.39 | 2022-23,2023-24,2024-25 |
| Pendikspor | 1 | 38 | 1.29 | 1.66 | -0.36 | 2023-24 |
| Samsunspor | 3 | 108 | 1.29 | 1.11 | +0.18 | 2023-24,2024-25,2025-26 |
| Alanyaspor | 4 | 142 | 1.27 | 1.36 | -0.09 | 2022-23,2023-24,2024-25,2025-26 |
| Giresunspor | 1 | 34 | 1.26 | 1.60 | -0.34 | 2022-23 |
| Konyaspor | 4 | 141 | 1.25 | 1.38 | -0.13 | 2022-23,2023-24,2024-25,2025-26 |
| Kasımpaşa | 4 | 143 | 1.25 | 1.55 | -0.31 | 2022-23,2023-24,2024-25,2025-26 |
| Kayserispor | 4 | 142 | 1.25 | 1.52 | -0.28 | 2022-23,2023-24,2024-25,2025-26 |
| Eyüpspor | 2 | 70 | 1.23 | 1.50 | -0.27 | 2024-25,2025-26 |
| Gaziantep FK | 4 | 130 | 1.22 | 1.59 | -0.38 | 2022-23,2023-24,2024-25,2025-26 |
| Fatih Karagümrük | 3 | 106 | 1.19 | 1.51 | -0.33 | 2022-23,2023-24,2025-26 |
| Ankaragücü | 2 | 73 | 1.18 | 1.30 | -0.13 | 2022-23,2023-24 |
| Hatayspor | 3 | 95 | 1.16 | 1.79 | -0.62 | 2022-23,2023-24,2024-25 |
| Sivasspor | 3 | 108 | 1.16 | 1.38 | -0.22 | 2022-23,2023-24,2024-25 |
| İstanbulspor | 2 | 71 | 1.07 | 1.74 | -0.67 | 2022-23,2023-24 |
| Gençlerbirliği | 1 | 34 | 1.07 | 1.52 | -0.45 | 2025-26 |
| Bodrum FK | 1 | 36 | 1.06 | 1.28 | -0.22 | 2024-25 |
| Antalyaspor | 4 | 143 | 1.06 | 1.52 | -0.46 | 2022-23,2023-24,2024-25,2025-26 |
| Kocaelispor | 1 | 34 | 0.94 | 1.01 | -0.07 | 2025-26 |

Hiç xG verisi olmayan takımlar (yalnız 2016-17…2021-22 arası Süper Lig’de oynadıkları için): Adanaspor, Akhisarspor, Altay, Bursaspor, Denizlispor, Erzurumspor, Gaziantepspor, Karabükspor, Osmanlıspor, Yeni Malatyaspor.

## 4. Uyarılar

- Yalnız **4 sezon** (2022-23 … 2025-26) xG içerir; “10 yıllık” ortalama aslında 2022-26 ortalamasıdır, uzun dönem kıyası yoktur. Takımlar arası kıyasta sezon sayıları farklıdır (kolon `sezon_sayisi`); ortalamalar yalnız xG’si olan maçlar üzerinden alınmıştır.
- 2022-23: yalnız FotMob sezon toplamı var (maç bazlı yok). `matches.csv`da bu sezon 342 maç var, ama FotMob (ve Sofascore etkinlik listesi) çoğu takım için 34, Hatayspor için 21, Gaziantep FK için 22 maç içeriyor. `matches.csv`deki 29 maç (Hatayspor/Gaziantep ile 2023-02-25 sonrası, tek kaynak football-data.co.uk) Sofascore/FotMob’da yok; bu maçların gerçekten oynanıp oynanmadığı doğrulama ajanına bırakılmalı. `mac_kapsami` bu yüzden `toplam_mac`tan düşüktür.
- 2023-24 … 2025-26: Sofascore’da bazı maçlar (ertelenen/yarıda kalan, ör. İstanbulspor–Trabzonspor 2023-12-19, Galatasaray–Adana Demirspor 2025-02-09) xG’siz veya `matches.csv` ile eşleşmiyor; her takımın notunda belirtildi. Per-maç ortalamalar `mac_kapsami` ile hesaplandı.
- Sofascore xG’si modele dayalıdır; sağlayıcı geçmiş değerleri güncelleyebilir. Penaltı ve kendi kalesine goller model tanımına göre değişebilir.
- Önbellekteki ham JSON `cache/` altında; betikler yeniden çalıştırıldığında ağa gitmeden devam eder (`python3 fetch_xg.py` ardından `python3 aggregate_xg.py`).
