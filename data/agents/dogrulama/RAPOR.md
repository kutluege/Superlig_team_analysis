# Doğrulama Raporu (team_season, attendance, attendance_tahmini)

Tarih: 2026-10-06. Çıktılar: `standings_check.csv`, `attendance_check.csv`, `capacity_check.csv`, `estimate_check.csv`. İndirilen sayfalar `cache/` altında.

## Kullanılan kaynaklar
- en.wikipedia "YYYY–YY Süper Lig" sayfaları (puan tablosu + stadyum tablosu), tr.wikipedia aynı sayfalar (2022-23, 2023-24, 2024-25 puan silme notları).
- Transfermarkt: `.../super-lig/tabelle/wettbewerb/TR1/saison_id/YYYY` ve `.../besucherzahlen/wettbewerb/TR1/saison_id/YYYY`.
- Sofascore API (`api.sofascore.com/api/v1/unique-tournament/52/season/{id}/standings/total`).
- european-football-statistics.co.uk (EFS) `attn/archive/tur/avetur{17..25}.htm` ve `attn/avetur.htm` (2025-26).
- Wikipedia stadyum makaleleri (infobox "Capacity" ve varsa "Capacity history").
- TFF sitesine erişildi ama puan durumu sayfası ASP.NET postback ile sezon seçtirdiği için otomatik çekilemedi; TFF doğrudan doğrulanamadı (Wikipedia tabloları zaten TFF kaynaklı).

## A) Final puan tabloları (10 sezon, 187 takım-sezon, her biri 8 alan)
Sonuç: **7 sezon (2016-17 … 2021-22 ve 2025-26) tamamen birebir eşleşti** (en.wikipedia + Transfermarkt + Sofascore üçü de aynı). 2022-23, 2023-24, 2024-25'te farklar **yalnızca puan silme cezaları** ve bunların sıralamaya yansıması ile averaj bağları kaynaklı. Oynanan/G/B/M/atılan/yenilen gol alanlarında **hiçbir sezonda fark yok** (hükmen sonuçlar dahil: 2022-23 Gaziantep/Hatayspor çekilmesi, 2024-25 Adana Demirspor hükmen yenilgisi, İstanbulspor 2023-24 hükmen yenilgisi doğru işlenmiş). Takım listeleri her sezon resmi listeyle aynı.

Toplam alan farkı: 11 (en.wikipedia'ya göre). Bunların 4'ü puan (hepsi puan silme), 7'si sıra.

### TFF / FIFA puan silme cezaları (bizim puanlarda UYGULANMAMIŞ)
| Sezon | Takım | Bizim | Resmi | Ceza | Gerekçe / kaynak |
|---|---|---|---|---|---|
| 2022-23 | Kayserispor | 50 | 47 | -3 | TFF Kulüp Lisans Kurulu, lisans şartlarını süresinde tamamlayamadı (karar 23 Aralık 2022). tr.wikipedia 2022-23 Süper Lig; https://www.fanatik.com.tr/futbol/tffden-5-kulube-puan-silme-cezasi-2314541 |
| 2023-24 | Kayserispor | 45 | 42 | -3 | TFF Kulüp Lisans Kurulu, lisans eksiklerini süresinde tamamlamadı (Kasım 2023, 7 kulübe birden). https://www.fanatik.com.tr/futbol/tff-resmen-acikladi-ve-super-lig-ekibinin-3-puani-silindi-2532155 ; Sofascore: "3 points deducted due to decision by the Federation" |
| 2023-24 | İstanbulspor | 19 | 16 | -3 | TFF PFDK: Trabzonspor maçında (Aralık 2023) başkanın takımı sahadan çekmesi, 0-3 hükmen + 3 puan silme. https://www.diken.com.tr/?p=1390749 ; https://beinsports.com.tr/haber/baskan-takimi-sahadan-cekti-mac-durduruldu |
| 2024-25 | Adana Demirspor | 14 | 2 | -12 | Toplam 12 puan (en.wikipedia, tr.wikipedia, Sofascore ile doğrulandı). Basın özetine göre: 3 (Kulüp Lisans Kurulu, 6 Aralık 2024) + 6 (FIFA Disiplin Komitesi) + 3 (PFDK, Galatasaray maçında sahadan çekilme, Şubat 2025). Parça dağılımı birincil kaynaktan doğrulanamadı; 12 toplamı kesin. https://en.wikipedia.org/wiki/2024–25_Adana_Demirspor_season |

Not: 2022-23 Kayserispor cezası bizim 9. sırayı değiştirmiyor; 2023-24'te Kayserispor 11.den 14.ye düşüyor, Gaziantep/Adana Demirspor/Samsunspor birer basamak yükseliyor (sıra farkları buradan).

### Sıralama (averaj/bağ) konuları
- 2024-25: Gaziantep FK, Alanyaspor, Kayserispor 45 puanda eşit. Bizim sıra (Alanyaspor 12, Kayserispor 13, Gaziantep 14) ikili averajla (Alanya 7, Kayseri 5, Gaziantep 4 puan; maç verimizden hesaplandı) örtüşüyor; tr.wikipedia ve Sofascore da bizimle aynı. en.wikipedia ve Transfermarkt genel averajla (Gaziantep 12) sıralamış, ki bu en.wikipedia'nın kendi yazdığı kuralla çelişiyor. TFF resmi tablosu doğrudan görülemedi, bu yüzden "muhtemelen bizimki doğru, kesin değil" olarak işaretlendi (standings_check.csv'de 3 satır).
- 2019-20: 32 puanda üç takım; Transfermarkt Kayserispor/Ankaragücü sırasını ters yazıyor, en.wikipedia ve Sofascore bizimle aynı.
- 2022-23: 41 puanda 4 takım; bizim sıra en.wikipedia (ikili averaj puanları dipnotta) ile aynı, Sofascore farklı (muhtemelen Sofascore hatası).

### Neden oluyor?
`superlig/standings.py` puanı maç skorlarından hesaplıyor ve ikili averajı uyguluyor ama TFF puan silme cezalarını uygulamıyor. Öneri: 3 takım-sezon (+ Adana 2024-25) için `puan` alanına ceza düşen bir düzeltme tablosu ekleyip sıralamayı yeniden hesaplamak.

## B) Seyirci ortalaması (attendance.csv, 72 takım-sezon: 2016-17, 2018-19, 2022-23, 2024-25)
- **european-football-statistics (EFS): 72/72 birebir aynı.** Yani bizim Wikipedia kaynaklı değerler EFS ile aynı kaynaktan geliyor (Wikipedia'nın kendi kaynağı EFS); bu ikisi "bağımsız" doğrulama sayılmaz.
- **Transfermarkt (bağımsız kaynak):** 26 birebir, 37 tanesi ≤%1, 61 tanesi ≤%5, 11 tanesi >%5 fark (medyan mutlak fark %0,9). Sezon bazında ortalama mutlak fark: 2016-17 %1,3; 2018-19 %5,1; 2022-23 %0,3; 2024-25 %3,1.
- En büyük farklar (hepsi 2018-19 ağırlıklı): Kayserispor 2018-19 +%13,5 (TM 9869), Erzurumspor 2018-19 +%12,2, Ankaragücü 2018-19 -%17,2 (TM 10242), Hatayspor 2024-25 -%10,4 (TM 3795). TM'nin maç sayısı ve hangi maçları saydığı farklı olabilir. Hangisinin doğru olduğunu üçüncü bir kaynakla (maç bazlı TFF raporları) ayrıştıramadık.
- Dikkat: 2016-17'de bazı kulüplerin ortalaması çok düşük (Fenerbahçe 16.485, Galatasaray 21.351); EFS ve TM aynı sayıyı veriyor, yani kaynakta bu şekilde (muhtemelen seyircisiz/cezalı maçlar ve eksik maç verisi); doğru "gerçek ortalama" olarak yorumlamamak gerekir. TM bu sezon için Galatasaray'da 15, Fenerbahçe'de ~17 maç verisi gösteriyor.

## C) Kapasite (189 takım-sezon kontrol edildi, istenen 40'ın çok üstünde)
Karşılaştırma ölçütü: Wikipedia stadyum makalesi (varsa "Capacity history" ile o sezona denk gelen değer: 43 satır; yoksa güncel infobox: 144 satır). Ayrıca her satırda Wikipedia sezon sayfası, Transfermarkt (güncel kapasite) ve Sofascore mekan/kapasite yan yana `not` sütununda.
- Wikipedia sezon sayfası tablolarıyla birebir aynı: 165/189. Aynı olmayan 24 satır (2017-18 ve 2020-21 sezonlarının çoğu + Erzurumspor 2018-19, Rizespor 2023-26) Wikipedia'dan değil başka kaynaktan (muhtemelen Sofascore) gelmiş.
- Stadyum makalesine göre: 124 satır ≤%2 (uyumlu), 44 satır %2-10 fark, 21 satır >%10 fark.
- Kapasite zaten yıldan yıla değişen, kaynaklar arası tutarsız bir sayı; "güncel" tipteki farkların çoğu yenilemelerden kaynaklanıyor olabilir. Asıl kuşkulu olanlar (stadyum yanlış ya da çelişkili):
  - **Fatih Karagümrük 2020-21: bizim 6500 (Vefa)**; Wikipedia hem lig hem kulüp sezon sayfasında Atatürk Olimpiyat Stadyumu (75.145-76.761) diyor. Büyük olasılıkla yanlış.
  - **Fatih Karagümrük 2023-24: bizim 12000 (Vefa)**; Wikipedia lig sayfası Vefa diyor ama kulüp sezon sayfası maçları Atatürk Olimpiyat'ta gösteriyor (77.563). Çelişkili; belirsiz.
  - **Ankaragücü 2018-19: bizim 20071 (Eryaman)**; Eryaman 28 Ocak 2019'da açıldı, Wikipedia Osmanlı Stadyumu kiracı listesinde Ankaragücü 2018-2019 var (18.029), Sofascore'da 17 iç sahadan 15'i Osmanlı. Muhtemelen yanlış (+%11).
  - **Akhisarspor 2017-18: 16597 (Manisa)**; yeni stadyum 28 Ocak 2018'de açıldı (Wikipedia), sezon karışık (Sofascore 14 Manisa, 3 Akhisar). Tek değer sezonu tam temsil etmiyor.
  - **Göztepe 2019-20 / 2021-22: 25035**; stadyum makalesi geçmişi 19.713 (2018-2024). Gürsel Aksel 26 Ocak 2020'de açıldı (2019-20'nin ilk yarısı Bornova). Wikipedia sezon sayfalarıyla stadyum makalesi birbirini tutmuyor (+%27).
  - **İstanbulspor 2022-23/2023-24: 7500**; Wikipedia stadyum makalesi 4.488, Transfermarkt 4.274 (-%40 olası fazlalık; 7500 Wikipedia sezon sayfası ve Sofascore'da var).
  - **Hatayspor 2024-25: 25000 (Yeni Hatay)**; Hatayspor 2023-2025 Mersin Stadyumu'nda (25.497, Sofascore 25.534); fark küçük (%2).
  - Karabükspor 2016-17/2017-18 (14200/15000 vs makale 11.378), Pendikspor 2023-24 (2500 vs 4.105), Gaziantep FK 2019-24 (33502 vs güncel 30.320; muhtemelen renovasyon öncesi gerçek değer), Gaziantepspor 2016-17, Adanaspor 2016-17: makale güncel kapasitesine göre %17-32 fark, ama bunlar tarihsel doğrulama değil.
- Sofascore'un `venue` alanı maçın gerçek yeri değil takımın varsayılan stadyumu olabiliyor (ör. Eyüpspor 2024-25'te Sofascore hep "Eyüp Stadium 2500" diyor, oysa kulüp Recep Tayyip Erdoğan Stadyumu'nda oynadı: https://www.takvim.com.tr/spor/2024/06/10/eyupspor-maclarini-oynayacagi-stadyumu-acikladi-iki-takim-ayni-stadi-kullanacak). Bu nedenle Sofascore'dan türeyen kapasite değerleri (2017-18, 2020-21 satırları) güvenilmez sayılmalı.

## D) Tahmin (attendance_tahmini.csv: 96 tahmin satırı) ile gerçek karşılaştırma
Gerçek değerler EFS (2017-18, 2018-19, 2019-20, 2022-23, 2023-24, 2025-26) ve Transfermarkt (2017-18 … 2025-26) sayfalarından; 172 karşılaştırma satırı (bazı takım-sezonlar iki kaynakta).
- Tam sezonlar (2017-18, 2019-20, 2023-24; EFS): 58 takım-sezon. Ortalama mutlak hata **%24,8**, medyan **%19**; 15'i ≤%10, 35'i ≤%25, 4'ü >%50. Net yanlılık küçük (ortalama -%2,7; ancak 2017-18 ve 2019-20'de aşağı yönlü %10-17, 2023-24'te +%4).
- **2021-22 (Transfermarkt, 20 takım): ortalama mutlak hata %86, medyan %71; tahminler sistematik olarak aşırı yüksek (+%81).** 2021-22'de COVID kısıtları/kapasite sınırı vardı; "doluluk × kapasite" yöntemi bu sezon için kullanılmamalı (ya da "güvenilmez" işaretlenmeli). En kötü örnekler: Yeni Malatyaspor (lig medyanı yöntemi) tahmin 8876 / gerçek 1811, Başakşehir 2984 / 1034, Alanyaspor 4168 / 1934.
- 2025-26: EFS ve TM sayfaları yalnızca sezonun ilk ~8-10 iç saha maçını içeriyor (kısmi), bu yüzden bu sezonun karşılaştırması (ort. mutlak hata ~%24-25) sadece göstergedir.
- "Lig medyan doluluk" yöntemi (16 satır): ortalama mutlak hata %50,6, medyan %34 (takım doluluk yönteminde %30,3/%21,4); daha güvensiz.
- Fatih Karagümrük 2023-24 tahmini 212 (gerçek 2684) kapasite belirsizliğinden (12000 vs 77563) kaynaklanıyor.
- Tek tek kayıtlar `estimate_check.csv` içinde; 2020-21 için tahmin yapılmamış (doğru: seyircisiz sezon, TM de 0 gösteriyor).

## Doğrulanamayanlar / sınırlar
- TFF resmi puan durumu doğrudan çekilemedi (postback). Wikipedia/Transfermarkt/Sofascore üçlüsü kullanıldı.
- Adana Demirspor 2024-25 puan silmenin parça dağılımı (3+6+3) yalnızca arama özetlerinden; toplam 12 üç kaynakla doğrulandı.
- 2024-25 üç takımlık bağda resmi TFF sırası görülemedi.
- Seyirci için gerçekten bağımsız ikinci kaynak yalnızca Transfermarkt; Wikipedia ve EFS aynı veri.
- Kapasitelerde sezon-özel resmi kaynak yok; stadyum makalelerinin kapasite geçmişi sadece 7 stadyumda var.
