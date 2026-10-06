# Süper Lig veri hattı — eksik veri ve kaynak raporu

Oluşturulma: 2026-10-06 16:04 UTC · Kapsam: 2016-17 → 2025-26

## 1. Kaynaklara erişim

| kaynak | host | cache | hata | ok |
|---|---|---|---|---|
| football-data.co.uk | www.football-data.co.uk | 10 | 0 | 0 |
| openfootball | raw.githubusercontent.com | 6 | 4 | 0 |
| sofascore | api.sofascore.com | 3363 | 0 | 1 |
| transfermarkt (ayna: c0ze/super-lig) | raw.githubusercontent.com | 1 | 0 | 0 |
| wikipedia | en.wikipedia.org | 10 | 0 | 0 |

Sofascore sezon id'leri (seasons_data): 2016-17=11927, 2017-18=13575, 2018-19=17762, 2019-20=24407, 2020-21=29506, 2021-22=37466, 2022-23=42632, 2023-24=53190, 2024-25=63814, 2025-26=77805

## 2. Sezon bazında maç kapsamı

Her hücre, o kaynakta skoru bulunan maç sayısıdır. `matches.csv` sütunu birleştirilmiş sonuçtur.

| sezon | football-data | sofascore | openfootball | transfermarkt | matches.csv | kullanilan_kaynak |
|---|---|---|---|---|---|---|
| 2016-17 | 306 | 306 | 0 | 306 | 306 | football-data.co.uk: 305; sofascore: 1 |
| 2017-18 | 306 | 306 | 0 | 306 | 306 | football-data.co.uk: 306 |
| 2018-19 | 306 | 306 | 306 | 306 | 306 | football-data.co.uk: 305; sofascore: 1 |
| 2019-20 | 306 | 306 | 306 | 306 | 306 | football-data.co.uk: 306 |
| 2020-21 | 420 | 420 | 420 | 420 | 420 | football-data.co.uk: 420 |
| 2021-22 | 380 | 380 | 0 | 380 | 380 | football-data.co.uk: 380 |
| 2022-23 | 342 | 313 | 0 | 342 | 342 | football-data.co.uk: 342 |
| 2023-24 | 380 | 379 | 380 | 380 | 380 | football-data.co.uk: 380 |
| 2024-25 | 342 | 341 | 342 | 342 | 342 | football-data.co.uk: 342 |
| 2025-26 | 306 | 306 | 306 | 265 | 306 | football-data.co.uk: 306 |

Hükmen sonuçlanan (kaynakta `[awarded]` işaretli) maçlar:

| sezon | tarih | ev | deplasman | ev_gol | dep_gol | kaynak |
|---|---|---|---|---|---|---|
| 2024-25 | 2025-02-09 | Galatasaray | Adana Demirspor | 3 | 0 | football-data.co.uk |

## 3. Kaynak çelişkileri

**Skor çelişkisi: 2 maç.** Kullanılan skor çoğunluk oyuyla seçildi (eşitlikte öncelik: football-data > sofascore > openfootball > transfermarkt). Tüm kaynak değerleri `data/celiskiler.csv` dosyasında.

| sezon | ev | deplasman | football-data | sofascore | openfootball | transfermarkt | secilen | secim_kurali |
|---|---|---|---|---|---|---|---|---|
| 2016-17 | Adanaspor | Kasımpaşa | 2-0 | 3-0 |  | 3-0 | 3-0 | çoğunluk |
| 2018-19 | Akhisarspor | Beşiktaş | 1-3 | 0-3 | 0-3 | 0-3 | 0-3 | çoğunluk |

Seyirci/kapasite çelişkisi: 59 takım-sezon.

## 4. Takım / sezon bazında eksik veri

Gösterim: `✓` tam · `—` takım o sezon Süper Lig'de değil (tüm değerler NaN) · `S` ortalama seyirci eksik · `K` stadyum kapasitesi eksik · `M` maç skoru eksik

| takim | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 |
|---|---|---|---|---|---|---|---|---|---|---|
| Alanyaspor | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Fenerbahçe | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Galatasaray | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Beşiktaş | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Antalyaspor | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| İstanbul Başakşehir | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Konyaspor | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Kasımpaşa | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Kayserispor | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Trabzonspor | ✓ | S | ✓ | S | S | S | ✓ | S | ✓ | S |
| Çaykur Rizespor | ✓ | — | ✓ | S | S | S | — | S | ✓ | S |
| Sivasspor | — | S | ✓ | S | S | S | ✓ | S | ✓ | — |
| Göztepe | — | S | ✓ | S | S | S | — | — | ✓ | S |
| Gaziantep FK | — | — | — | S | S | S | ✓ | S | ✓ | S |
| Hatayspor | — | — | — | — | S | S | ✓ | S | ✓ | — |
| Ankaragücü | — | — | ✓ | S | S | — | ✓ | S | — | — |
| Fatih Karagümrük | — | — | — | — | S | S | ✓ | S | — | S |
| Yeni Malatyaspor | — | S | S | S | S | S | — | — | — | — |
| Gençlerbirliği | ✓ | S | — | S | S | — | — | — | — | S |
| Adana Demirspor | — | — | — | — | — | S | ✓ | S | ✓ | — |
| Akhisarspor | ✓ | S | ✓ | — | — | — | — | — | — | — |
| Bursaspor | ✓ | S | ✓ | — | — | — | — | — | — | — |
| Samsunspor | — | — | — | — | — | — | — | S | ✓ | S |
| İstanbulspor | — | — | — | — | — | — | ✓ | S | — | — |
| Karabükspor | ✓ | S | — | — | — | — | — | — | — | — |
| Erzurumspor | — | — | ✓ | — | S | — | — | — | — | — |
| Denizlispor | — | — | — | S | S | — | — | — | — | — |
| Eyüpspor | — | — | — | — | — | — | — | — | ✓ | S |
| Giresunspor | — | — | — | — | — | S | ✓ | — | — | — |
| Osmanlıspor | ✓ | S | — | — | — | — | — | — | — | — |
| Adanaspor | ✓ | — | — | — | — | — | — | — | — | — |
| Altay | — | — | — | — | — | S | — | — | — | — |
| Bodrum FK | — | — | — | — | — | — | — | — | ✓ | — |
| Gaziantepspor | ✓ | — | — | — | — | — | — | — | — | — |
| Kocaelispor | — | — | — | — | — | — | — | — | — | S |
| Pendikspor | — | — | — | — | — | — | — | S | — | — |
| Ümraniyespor | — | — | — | — | — | — | S | — | — | — |

- Ligde olunan takım-sezon sayısı: **189**
- Maç skoru eksik takım-sezon: **0**
- Ortalama seyirci eksik: **117 / 189**
- Stadyum kapasitesi eksik: **0 / 189**

## 5. Takım adı standardizasyonu

Tüm kaynaklardaki 176 ad yazımı standart adlara eşlendi (`data/team_mapping.csv`). Örnek: Sofascore'un 2016-17 için kullandığı 'Sincan Belediyesi Ankaraspor' → Osmanlıspor; football-data 'Buyuksehyr' → İstanbul Başakşehir. Gaziantepspor (2016-17) ile Gaziantep FK ayrı kulüplerdir.

## 6. Yöntem notları

- `team_season.csv` puan ve sıraları yalnızca `matches.csv` skorlarından hesaplanır. TFF'nin verdiği puan silme cezaları maç verisinde olmadığı için uygulanmamıştır; bu nedenle bazı sezonlarda resmi puan tablosundan sapma olabilir.
- Sıralama ölçütü: puan → ikili maçlarda puan → ikili averaj → ikili atılan gol → genel averaj → atılan gol.
- Sezon ataması: 15 Temmuz kesim tarihi; 2020'de COVID nedeniyle 15 Ağustos.
- Seyirci: Sofascore ortalaması yalnızca takımın iç saha maçlarının en az yarısında seyirci kaydı varsa kullanılır (`seyirci_mac` / `ev_mac`); aksi halde Wikipedia sezon tablosu. Sofascore'da seyirci kaydı çok seyrek olduğu için bu dönemde tüm değerler Wikipedia'dan geldi. Ham maç bazında Sofascore verisi: `data/raw/sofascore_mac_seyirci.csv`.
- Kapasite: Wikipedia sezon tablosu önce gelir. Sofascore'un etkinlik stadı bazı kulüplerde o sezon oynanan stadı değil güncel stadı gösteriyor (ör. Fatih Karagümrük 2021-22: Sofascore 6.500 / Wikipedia 76.761; Altay 2021-22: 58.008 / 14.000). İki değer de `celiskiler.csv`'de.
- 2022-23'te deprem sonrası ligden çekilen Gaziantep FK ve Hatayspor'un kalan 29 maçı football-data ve Transfermarkt'ta hükmen 3-0 olarak yer alıyor (Sofascore'da yok); hesaplamaya dahil edildi.
