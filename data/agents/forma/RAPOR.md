# Forma fiyatı ve TÜFE alt-ajanı raporu

Hazırlanma tarihi: 2026-10-06 · Klasör: `data/agents/forma/`

## Çıktılar

| Dosya | İçerik |
|---|---|
| `forma_fiyat.csv` | 19 takım × 10 sezon = 190 satır (`takim,sezon,fiyat_TL,urun_adi,kaynak_url,kaynak_tarihi,not`). Bulunamayan hücrelerde `fiyat_TL` boş, `not` sütununda neden yazıyor. |
| `tufe.csv` | TÜFE (2003=100) aylık endeks, 2016-01 … 2026-09 (129 ay). |
| `RAPOR.md` | Bu rapor. |

## A) Yetişkin iç saha forması lansman fiyatı – kapsam

**64 / 190 hücre dolu.** Değerler TL, KDV dahil perakende (lansman) fiyatıdır.

İşaretler: `g` = goal.com fiyat galerisi (2019-08-21, kulüp resmi sitelerinden 20 Ağustos 2019 fiyatları; ürün tipi belirtilmemiş) ·
`†` = lansman penceresi dışında bir kaynaktan (sonraki indirim haberindeki liste fiyatı ya da bir sonraki sezonun haberindeki "geçen sezon" fiyatı) ·
`?` = hangi formanın iç saha olduğu kaynakta net değil · `*` = ikincil anma (başka bir kulübün haberinde geçen fiyat) · `–` = bulunamadı.

| Takım | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 | n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Galatasaray | – | 179 | 189,90 | 249,90 | 279 | 399 | 799,90 | 1.449 | 2.999 | 4.499,99 | 9 |
| Fenerbahçe | 155 | 169 | 189 | 249 | 289 | 319 | 629 | 1.399* | 2.999 | 4.249 | 10 |
| Beşiktaş | 155 | 169 | 189 | 249g | 289 | 359 | 599 | 1.399 | 2.999 | 4.250 | 10 |
| Trabzonspor | – | – | – | 199,99g | – | 329* | 599,99 | 961 | 1.967 | 3.199 | 6 |
| İstanbul Başakşehir | – | – | – | – | – | – | – | – | – | – | 0 |
| Konyaspor | – | – | – | – | – | 192,20 | – | 650† | 1.449,95 | 1.242 | 4 |
| Antalyaspor | – | – | – | – | 139 | 229 | 497† | – | 1.690† | 1.966 | 5 |
| Alanyaspor | – | 79,50 | – | – | – | – | – | – | – | – | 1 |
| Kasımpaşa | – | – | – | – | – | – | – | – | – | – | 0 |
| Kayserispor | – | – | – | 149g | – | – | 500? | 699 | 1.966 | – | 4 |
| Sivasspor | – | – | – | – | – | – | – | 558 | 1.058 | 1.458 | 3 |
| Çaykur Rizespor | 120 | – | – | 189,90g | 149 | – | – | 500 | – | – | 4 |
| Gaziantep FK | – | – | – | – | – | – | – | – | – | – | 0 |
| Göztepe | – | – | – | 190 | – | – | – | – | – | – | 1 |
| Gençlerbirliği | – | – | – | – | – | – | – | – | 1.350 | – | 1 |
| Fatih Karagümrük | – | – | – | – | – | – | – | 699,90 | – | – | 1 |
| Ankaragücü | – | – | – | – | – | – | – | 749 | 1.399 | – | 2 |
| Hatayspor | – | – | – | – | – | – | – | 1.000 | – | – | 1 |
| Yeni Malatyaspor | – | – | – | 130g | – | 170 | – | – | – | – | 2 |
| **Dolu hücre** | 3 | 4 | 3 | 8 | 5 | 7 | 6 | 11 | 10 | 7 | **64** |

### Takım bazında durum
- **En iyi kapsam:** Fenerbahçe (10/10), Beşiktaş (10/10), Galatasaray (9/10; yalnızca 2016-17 eksik), Trabzonspor (6/10).
- **Orta:** Antalyaspor (5), Konyaspor (4), Kayserispor (4), Çaykur Rizespor (4), Sivasspor (3).
- **En zayıf:** İstanbul Başakşehir, Kasımpaşa ve Gaziantep FK (0/10); Alanyaspor, Göztepe, Gençlerbirliği, Fatih Karagümrük, Hatayspor (1/10); Ankaragücü ve Yeni Malatyaspor (2/10).
- Sezon bazında en iyi kapsam 2023-24'te (AA'nın 2023-07-14 tarihli toplu haberi sayesinde); en zayıf 2016-17 ve 2018-19.

### Kullanılan kaynak türleri
1. **Ulusal spor/haber siteleri** (fanatik, cnnturk, milliyet, sabah, hürriyet, habertürk, ntv, karar, cumhuriyet, star, onedio, ensonhaber, diken vb.): lansman günü "formalar X TL'den satışa çıktı" haberleri. Büyük kulüplerin çoğu bunlardan geldi.
2. **Anadolu Ajansı (aa.com.tr)**: kulüp bazlı lansman haberleri ve 2023-07-14 tarihli toplu haber ("Süper Lig'de takımlar yeni sezon formalarıyla sahaları renklendirecek"; TS, Sivasspor, Ankaragücü, Kayserispor, Rizespor, Karagümrük). aa.com.tr yalnızca `curl` ile okunabildi (Python requests bağlantıyı kesiyor).
3. **goal.com Türkçe**: 2018-07-31 BJK/FB fiyat yazıları, 2022 kulüp forma yazıları ve **2019-08-21 "Süper Lig ve Avrupa'da forma fiyatları" galerisi** (resmi sitelerden 20 Ağustos 2019 fiyatları; 2019-20 için 5 hücre yalnızca buna dayanıyor).
4. **Yerel basın** (Konya: pusulahaber, konyaimza; Antalya: akdenizmanset, antalyaekspres; Kayseri: kayseriyerelhaber; Sivas: gundemsivas; Rize: rizedeyiz, bolgegundem; Hatay: antakyagazetesi; Ankara: haberankara, ticarihayat).
5. **Kulüp resmi kanalları**: antalyaspor.com.tr (2020-09-30 duyurusu), Sivasspor resmi X hesabı (2025-07-05; tarih tweet kimliğinden çözüldü). Kulüp açıklamaları haberlerde alıntılandığında haberin URL'si verildi.
6. **Habertürk 2025-07-30 karşılaştırma tablosu** (BJK/FB/GS 2021/22–2025/26, yuvarlanmış): yalnızca **çapraz kontrol** için kullanıldı, `not` sütununda belirtildi; hiçbir hücre yalnızca buna dayanmıyor.

### Erişilemeyen / kullanılmayan kaynaklar
- **web.archive.org** ağ politikasıyla engelli (talimat gereği denenmedi); **archive.ph** bağlantı vermedi. Google cache yok.
- **gsstore.org, fenerium.com, kartalyuvasi.com.tr, trendyol** 403; **bjk.com.tr, trabzonspor.org.tr, hatayspor.org.tr** 403; **kayserispor.org.tr, sivasspor.com.tr, shop.hatayspor.org.tr, alanyasporstore.com** bağlantı yok. WebFetch aracı hurriyet/ajansspor için egress engeli verdi; bunlar `curl` ile okundu.
- Erişilebilen kulüp mağazaları (konyastore, ksstore, store.antalyaspor, gozgoz, ankaragucustore, gfkstore, trabzonspor.com.tr) bugün (2026-10-06) **2026-27** ürünlerini gösteriyor; 2025-26 ürün sayfaları çoğunlukla 404 ya da JS ile render ediliyor. Bu yüzden "güncel mağaza fiyatı" hiçbir hücrede kullanılmadı.
- **Resmi olmayan/sahte görünümlü mağaza alan adları** (alanyaspor-fc.com, istanbul-basaksehir.com, caykur-rizespor.com, goztepe-sk.com, kayserisporfc.com vb.) kullanılmadı.

### Uyarılar (analizde dikkat)
- **Ürün tipi tutarlılığı:** 2024-25'ten itibaren büyük kulüpler çok kademeli satıyor (GS 2024-25: profesyonel / maç / taraftar; BJK 2025-26: "futbolcu" 4.250 vs "taraftar" 3.500). Tabloda her zaman **standart replika (ana maç forması)** alındı, daha ucuz "taraftar forması" ve pahalı "authentic/oyuncu" versiyonu `not`'ta. GS 2023-24'te taraftar forması 1.499,90, orijinal 3.699,90 TL'dir; tabloda 4 Haziran 2023 satış öncesi açıklanan 1.449 TL var.
- **Lansman zamanı:** GS 2017-18 ve 2018-19 formaları Mayıs ayında (sezon bitmeden) çıktı; 2020-21'de pandemi nedeniyle lansmanlar Ağustos-Eylül'e kaydı (Antalyaspor 30 Eylül 2020, Rizespor 2 Eylül 2020). Bazı kaynaklar satıştan birkaç gün önce açıklanan fiyatı veriyor (not'ta belirtildi).
- **Lansman indirimi:** Antalyaspor 2021-22'de ilk hafta 207 TL, liste 229 TL → liste fiyatı alındı.
- **Toplu fiyatlar:** Birçok küçük kulüp tüm formaları aynı fiyata satıyor (Sivasspor, Rizespor 2023-24, Ankaragücü); bu durumda iç saha forması da o fiyattadır.
- **Galeri (g) hücreleri** iç saha/yetişkin ayrımı yapmıyor ve lansmandan ~1-2 ay sonraki fiyattır; **† hücreleri** lansman fiyatından farklı olabilir. Reel analizde bu hücreler duyarlılık testiyle ayrıca ele alınmalı.
- Bir hücre (Kayserispor 2022-23, `?`) için iç saha formasının kırmızı mı sarı mı olduğu belirsiz (kırmızı/siyah 500, sarı 550 TL).
- Formanın satışa çıktığı ay ile kaynak tarihi `kaynak_tarihi` sütunundadır; reel çevirmede bu ayın TÜFE'si kullanılabilir.

## B) TÜFE (2003=100)

- **Kaynak:** TCMB EVDS (yeni arayüz `evds3.tcmb.gov.tr`), seri **TP.GENENDEKS.T1** "Genel Endeks (2003=100)", veri grubu `bie_tukfiy2003`, kaynak TÜİK. EVDS2 API anahtar istiyor; evds3 web arayüzünün kullandığı herkese açık `/igmevdsms-dis/fe` uç noktasından anahtarsız çekildi.
- **Önemli:** TÜİK Ocak 2026'dan itibaren TÜFE'yi **2025=100** bazına geçirdi. EVDS notuna göre 2003=100 **genel endeks** yayımlanmaya devam ediyor (alt kalemler arşivlendi). Arşiv serisi TP.FG.J0 ile 2016-01…2026-01 arasında birebir aynı (kontrol edildi). Doğrulama: 2022-12 = 1.128,45; 2023-12 = 1.859,38; 2024-12 = 2.684,55.
- **Kapsam:** 2016-01 … 2026-09, 129 ay, eksik yok. En son değer: 4368.35 (2026-09) → reel çevirme için baz ay.
- Reel fiyat: `fiyat_reel = fiyat_TL × TÜFE[2026-09] / TÜFE[lansman ayı]`.
