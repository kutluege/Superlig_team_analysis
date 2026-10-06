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
