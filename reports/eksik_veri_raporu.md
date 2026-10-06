# Süper Lig veri hattı — eksik veri ve kaynak raporu

Oluşturulma: 2026-10-06 13:47 UTC · Kapsam: 2016-17 → 2025-26

## 1. Kaynaklara erişim

| kaynak | host | atlandi | cache | hata |
|---|---|---|---|---|
| football-data.co.uk | www.football-data.co.uk | 7 | 0 | 3 |
| football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025) | raw.githubusercontent.com | 0 | 1 | 0 |
| openfootball | raw.githubusercontent.com | 0 | 6 | 4 |
| sofascore | api.sofascore.com | 1 | 0 | 1 |
| sofascore (ayna: c0ze/super-lig) | raw.githubusercontent.com | 0 | 1 | 0 |
| transfermarkt (ayna: c0ze/super-lig) | raw.githubusercontent.com | 0 | 1 | 0 |
| wikipedia | en.wikipedia.org | 7 | 0 | 3 |

**Erişilemeyen hostlar:** `api.sofascore.com`, `en.wikipedia.org`, `www.football-data.co.uk`

Bu çalıştırmada ortamın ağ politikası bu hostlara bağlantıyı reddetti (HTTP CONNECT 403). Kod bu kaynakları her çalıştırmada önce dener; erişim açıldığında `python run_pipeline.py` yeniden çalıştırılınca resmi kaynaklar otomatik kullanılır, seyirci ve kapasite alanları dolar. Erişilemeyen sezonlar şu GitHub aynalarından alındı:

- football-data.co.uk → `xgabora/Club-Football-Match-Data-2000-2025` @ `25882a58a7` (football-data.co.uk sezon dosyalarının birleştirilmiş kopyası)
- Sofascore → `c0ze/super-lig` @ `0550f8713e` `data/site.db` (Sofascore event id'li maç sonuçları; seyirci alanı yok)
- Ek çapraz kontrol: `openfootball/europe` @ `0bf83f88e8` ve `c0ze/super-lig` `data/super_lig.db` (Transfermarkt maç raporları)

Sofascore sezon id'leri `datafc.seasons_data(52)` ile bulunamadı (API erişilemedi).

## 2. Sezon bazında maç kapsamı

Her hücre, o kaynakta skoru bulunan maç sayısıdır. `matches.csv` sütunu birleştirilmiş sonuçtur.

| sezon | football-data | sofascore | openfootball | transfermarkt | matches.csv | kullanilan_kaynak |
|---|---|---|---|---|---|---|
| 2016-17 | 306 | 306 | 0 | 306 | 306 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 305; sofascore (ayna: c0ze/super-lig): 1 |
| 2017-18 | 306 | 306 | 0 | 306 | 306 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 306 |
| 2018-19 | 306 | 306 | 306 | 306 | 306 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 305; sofascore (ayna: c0ze/super-lig): 1 |
| 2019-20 | 306 | 306 | 306 | 306 | 306 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 306 |
| 2020-21 | 420 | 420 | 420 | 420 | 420 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 420 |
| 2021-22 | 380 | 380 | 0 | 380 | 380 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 380 |
| 2022-23 | 342 | 313 | 0 | 342 | 342 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 342 |
| 2023-24 | 380 | 380 | 380 | 380 | 380 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 380 |
| 2024-25 | 314 | 342 | 342 | 342 | 342 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 314; sofascore (ayna: c0ze/super-lig): 28 |
| 2025-26 | 306 | 306 | 306 | 265 | 306 | football-data.co.uk (ayna: xgabora/Club-Football-Match-Data-2000-2025): 306 |

football-data.co.uk (ayna) verisinde olmayan **28 maç** diğer kaynaklardan tamamlandı (en az iki kaynakla doğrulanmış):

| sezon | kaynak | mac |
|---|---|---|
| 2024-25 | sofascore (ayna: c0ze/super-lig) | 28 |

Hükmen sonuçlanan (kaynakta `[awarded]` işaretli) maçlar:

| sezon | tarih | ev | deplasman | ev_gol | dep_gol | kaynak |
|---|---|---|---|---|---|---|
| 2024-25 | 2025-02-09 | Galatasaray | Adana Demirspor | 3 | 0 | sofascore (ayna: c0ze/super-lig) |

## 3. Kaynak çelişkileri

**Skor çelişkisi: 3 maç.** Kullanılan skor çoğunluk oyuyla seçildi (eşitlikte öncelik: football-data > sofascore > openfootball > transfermarkt). Tüm kaynak değerleri `data/celiskiler.csv` dosyasında.

| sezon | ev | deplasman | football-data | sofascore | openfootball | transfermarkt | secilen | secim_kurali |
|---|---|---|---|---|---|---|---|---|
| 2016-17 | Adanaspor | Kasımpaşa | 2-0 | 3-0 |  | 3-0 | 3-0 | çoğunluk |
| 2018-19 | Akhisarspor | Beşiktaş | 1-3 | 0-3 | 0-3 | 0-3 | 0-3 | çoğunluk |
| 2023-24 | İstanbulspor | Trabzonspor | 0-3 | 1-2 | 0-3 | 0-3 | 0-3 | çoğunluk |

## 4. Takım / sezon bazında eksik veri

Gösterim: `✓` tam · `—` takım o sezon Süper Lig'de değil (tüm değerler NaN) · `S` ortalama seyirci eksik · `K` stadyum kapasitesi eksik · `M` maç skoru eksik

| takim | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 |
|---|---|---|---|---|---|---|---|---|---|---|
| Alanyaspor | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Fenerbahçe | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Galatasaray | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Beşiktaş | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Antalyaspor | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| İstanbul Başakşehir | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Konyaspor | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Kasımpaşa | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Kayserispor | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Trabzonspor | SK | SK | SK | SK | SK | SK | SK | SK | SK | SK |
| Çaykur Rizespor | SK | — | SK | SK | SK | SK | — | SK | SK | SK |
| Sivasspor | — | SK | SK | SK | SK | SK | SK | SK | SK | — |
| Göztepe | — | SK | SK | SK | SK | SK | — | — | SK | SK |
| Gaziantep FK | — | — | — | SK | SK | SK | SK | SK | SK | SK |
| Hatayspor | — | — | — | — | SK | SK | SK | SK | SK | — |
| Ankaragücü | — | — | SK | SK | SK | — | SK | SK | — | — |
| Fatih Karagümrük | — | — | — | — | SK | SK | SK | SK | — | SK |
| Yeni Malatyaspor | — | SK | SK | SK | SK | SK | — | — | — | — |
| Gençlerbirliği | SK | SK | — | SK | SK | — | — | — | — | SK |
| Adana Demirspor | — | — | — | — | — | SK | SK | SK | SK | — |
| Akhisarspor | SK | SK | SK | — | — | — | — | — | — | — |
| Bursaspor | SK | SK | SK | — | — | — | — | — | — | — |
| Samsunspor | — | — | — | — | — | — | — | SK | SK | SK |
| İstanbulspor | — | — | — | — | — | — | SK | SK | — | — |
| Karabükspor | SK | SK | — | — | — | — | — | — | — | — |
| Erzurumspor | — | — | SK | — | SK | — | — | — | — | — |
| Denizlispor | — | — | — | SK | SK | — | — | — | — | — |
| Eyüpspor | — | — | — | — | — | — | — | — | SK | SK |
| Giresunspor | — | — | — | — | — | SK | SK | — | — | — |
| Osmanlıspor | SK | SK | — | — | — | — | — | — | — | — |
| Adanaspor | SK | — | — | — | — | — | — | — | — | — |
| Altay | — | — | — | — | — | SK | — | — | — | — |
| Bodrum FK | — | — | — | — | — | — | — | — | SK | — |
| Gaziantepspor | SK | — | — | — | — | — | — | — | — | — |
| Kocaelispor | — | — | — | — | — | — | — | — | — | SK |
| Pendikspor | — | — | — | — | — | — | — | SK | — | — |
| Ümraniyespor | — | — | — | — | — | — | SK | — | — | — |

- Ligde olunan takım-sezon sayısı: **189**
- Maç skoru eksik takım-sezon: **0**
- Ortalama seyirci eksik: **189 / 189**
- Stadyum kapasitesi eksik: **189 / 189**

## 5. Takım adı standardizasyonu

Tüm kaynaklardaki 176 ad yazımı standart adlara eşlendi (`data/team_mapping.csv`). Örnek: Sofascore'un 2016-17 için kullandığı 'Sincan Belediyesi Ankaraspor' → Osmanlıspor; football-data 'Buyuksehyr' → İstanbul Başakşehir. Gaziantepspor (2016-17) ile Gaziantep FK ayrı kulüplerdir.

## 6. Yöntem notları

- `team_season.csv` puan ve sıraları yalnızca `matches.csv` skorlarından hesaplanır. TFF'nin verdiği puan silme cezaları maç verisinde olmadığı için uygulanmamıştır; bu nedenle bazı sezonlarda resmi puan tablosundan sapma olabilir.
- Sıralama ölçütü: puan → ikili maçlarda puan → ikili averaj → ikili atılan gol → genel averaj → atılan gol.
- Sezon ataması: 15 Temmuz kesim tarihi; 2020'de COVID nedeniyle 15 Ağustos.
- 2022-23'te deprem sonrası ligden çekilen Gaziantep FK ve Hatayspor'un kalan 29 maçı football-data ve Transfermarkt'ta hükmen 3-0 olarak yer alıyor (Sofascore'da yok); hesaplamaya dahil edildi.
