# Süper Lig takım analizi (2016-17 → 2025-26)

On sezonluk Süper Lig maç verisini birden fazla kaynaktan çeken, takım adlarını standartlaştıran,
kaynakları birbirine karşı doğrulayan, puan tablolarını maç sonuçlarından hesaplayan ve
takımları amblemleriyle sıralayan görseller üreten veri hattı.

```bash
pip install -r requirements.txt
python run_pipeline.py          # veri + rapor + görseller + pano
python run_pipeline.py --no-viz # yalnızca veri ve rapor
```

## Çıktılar

| Dosya | İçerik |
|---|---|
| `data/matches.csv` | sezon, tarih, ev, deplasman, ev_gol, dep_gol, kaynak + doğrulayan kaynaklar, çelişki ve hükmen işaretleri |
| `data/team_season.csv` | takım × sezon paneli: oynanan, galibiyet, beraberlik, mağlubiyet, atılan/yenilen gol, averaj, puan, sıra, iç/dış saha puanı. Takım o sezon ligde değilse değerler boş (NaN) |
| `data/attendance.csv` | takım × sezon: ort_seyirci, kapasite, kaynak (aşağıdaki nota bakın) |
| `data/team_mapping.csv` | her kaynaktaki ad yazımı → standart ad, kısa kod |
| `data/celiskiler.csv` | kaynakların farklı değer verdiği maçlar; her kaynağın değeri ve seçim kuralı |
| `data/eksik_veri_raporu.csv` | takım/sezon/alan bazında eksik veri listesi |
| `data/kaynak_kapsami.csv` | sezon × kaynak maç sayıları |
| `data/raw/football-data/` | football-data.co.uk T1 sezon dilimleri (yeniden üretilebilirlik için) |
| `reports/eksik_veri_raporu.md` | kaynak erişimi, kapsam, çelişkiler ve takım/sezon eksik veri ızgarası |
| `reports/pano.html` | sezon ve ölçüt seçilebilen etkileşimli sıralama panosu (tarayıcıda açın) |
| `reports/figures/*.png` | amblemli sıralama görselleri |
| `logs/pipeline.log`, `logs/kaynak_istekleri.csv` | her isteğin sonucu (ok / cache / hata / atlandı) |

## Kaynaklar ve sıra

1. **football-data.co.uk** Turkey `T1` sezon dosyaları (`mmz4281/{1617..2526}/T1.csv`). Erişilemeyen
   sezonlar, aynı dosyaları birleştiren GitHub aynasından (`xgabora/Club-Football-Match-Data-2000-2025`) alınır.
2. **Sofascore** (`datafc`, unique-tournament id 52; sezon id'leri `seasons_data` ile bulunur). Maç
   sonuçları eksik/hatalı sezonları tamamlamak ve çapraz kontrol için; seyirci (`event.attendance`) ve stadyum
   kapasitesi (`event.venue`) için. API erişilemezse maç sonuçları Sofascore event id'li GitHub aynasından
   (`c0ze/super-lig`, `data/site.db`) alınır.
3. **Wikipedia** sezon sayfaları: seyirci/kapasite yedeği.
4. Ek bağımsız çapraz kontrol: `openfootball/europe` (6 sezon) ve Transfermarkt maç raporları
   (`c0ze/super-lig`, `data/super_lig.db`).

Tüm GitHub kaynakları sabit bir commit'e (SHA) iliştirilmiştir (`superlig/config.py`).

**Kurallar:** host başına istekler arası bekleme, tüm yanıtlar `cache/http/` altında önbellekte,
hatalar loglanır ve hat devam eder; bir host art arda 3 kez bağlantı hatası verirse kalan istekleri
denenmez. Çelişkide çoğunluk oyu kullanılır, eşitlikte öncelik
football-data > sofascore > openfootball > transfermarkt; tüm değerler `celiskiler.csv`'de kalır.

### Bu sürümün durumu

- Maç sonuçlarının tamamı resmi football-data.co.uk dosyalarından geliyor; 3.394 maçın hepsi en az iki
  kaynakla karşılaştırıldı ve yalnızca 2 maçta skor çelişkisi var (`data/celiskiler.csv`).
- **Seyirci:** Sofascore'da maç bazında seyirci kaydı çok seyrek (ör. 2016-17'de 306 maçın 43'ünde, 2024-25'te
  hiç yok). Bu yüzden ortalamalar Wikipedia sezon tablolarından alındı. 2016-17, 2018-19, 2022-23 ve 2024-25
  dolu; diğer sezonlar boş. 2020-21 COVID-19 nedeniyle seyircisiz oynandı. Veri uydurulmadı.
- **Kapasite:** 189 takım-sezonun hepsinde var. Wikipedia sezon tablosu önce, yoksa Sofascore kullanıldı;
  Sofascore bazı kulüplerde o sezonki değil güncel stadı gösteriyor.

### Seyirci tahmini (eksik sezonlar)

`data/attendance_tahmini.csv` eksik sezonları tahmin eder; gözlenen değerler `attendance.csv`'de değişmeden kalır.
Tahmin = takımın gözlenen sezonlardaki ortalama doluluk oranı × o sezonun stadyum kapasitesi (takımın hiç gözlenen
sezonu yoksa lig medyanı, %33). `yontem` sütunu her satırın gözlenen mi tahmin mi olduğunu söyler. 2020-21
seyircisiz olduğu için tahmin edilmez. Gözlenen 60 değer üzerinde geriye dönük test: medyan sapma %21, ortalama
sapma %34. Stat kapasitesi dayanak sezonlardan çok farklı olan tahminler `not` sütununda "güvenilmez" olarak
işaretlidir. Görseller: `seyirci_tahminli_isi_haritasi.png`, `seyirci_tahminli_siralama.png`.

## Görseller

Amblemler `luukhopman/football-logos` deposundan. 2021 öncesi ligden düşen yedi kulübün (Adanaspor,
Akhisarspor, Bursaspor, Denizlispor, Gaziantepspor, Karabükspor, Osmanlıspor) amblemi bu depoda yok; bunlar
için kulüp renklerinde, kısa kodlu bir yer tutucu rozet üretildi (`assets/logos/KAYNAK.csv`).

| | |
|---|---|
| ![Podyum](reports/figures/podyum.png) | ![Sıra ısı haritası](reports/figures/sira_isi_haritasi.png) |
| ![Toplam puan](reports/figures/toplam_puan.png) | ![Maç başı puan](reports/figures/mac_basi_puan.png) |

Ayrıca: her sezon için amblemli puan durumu (`puan_durumu_<sezon>.png`), toplam galibiyet, toplam atılan gol,
maç başına gol ve iç sahada maç başına puan sıralamaları.

## Yöntem notları

- Puan ve sıra yalnızca `matches.csv` skorlarından hesaplanır. Sıralama: puan → ikili maçlarda puan →
  ikili averaj → ikili atılan gol → genel averaj → atılan gol. TFF puan silme cezaları maç verisinde
  olmadığı için uygulanmaz; bazı sezonlarda resmi tablodan bu nedenle sapma olabilir.
- Sezon ataması tarihe göre yapılır (15 Temmuz kesim; COVID'li 2020'de 15 Ağustos).
- 2022-23'te deprem sonrası çekilen Gaziantep FK ve Hatayspor'un kalan 29 maçı hükmen 3-0 olarak dahildir.

## Forma ve kombine fiyatları (Wayback Machine)

```bash
python collect_prices.py                  # kaldığı yerden devam eder
python collect_prices.py --retry-missing  # 'bulunamadi' olanları da yeniden dene
python -m pytest -q tests/                # ağ gerektirmeyen testler
```

- `data/sources.csv` (takim, alan_adi, tur): 19 kulübün resmi site ve mağaza alan adları; eski alan adları
  `*_eski` türüyle. Her alan adının kanıt bağlantısı `data/sources_kanit.csv` içinde.
- Her sezon için CDX'te 1 Mayıs–30 Eylül aralığı taranır. Yetişkin ev forması ürün sayfası (çocuk, kadın,
  deplasman, kaleci vb. elenir; sezon ibaresi URL'de ya da sayfa başlığında olmalı) ve kombine duyuru/bilet
  sayfaları seçilir. Pencere içindeki **en erken kopyadan** fiyat okunur. Üstü çizili fiyat varsa liste fiyatı
  alınır ve notta belirtilir.
- Çıktılar: `data/forma.csv`, `data/kombine.csv`, `data/eksikler.txt`. Her dolu değerin bir
  `web.archive.org/web/<zaman>/<url>` kaynağı vardır; kaynak yoksa hücre boş kalır.
- İstekler arasında 1-2 sn bekleme, yanıtlar `cache/wayback/` altında, ilerleme `data/fiyat_durum.json`'da.
  Mevcut `forma.csv`/`kombine.csv` içindeki dolu satırlara dokunulmaz.

**Durum:** Bu ortamda `web.archive.org` ağ politikasıyla engelli olduğu için henüz hiçbir fiyat toplanamadı;
tüm işler "hata" durumunda ve bir sonraki çalıştırmada yeniden denenecek.

## Skor kartı ve Instagram görselleri

```bash
python -c "from superlig import insta; insta.render_all()"   # reports/instagram/*.png (1080×1350)
```

Alt ajan çıktıları `data/agents/<ad>/` altında (her birinde RAPOR.md var):
`dogrulama` (resmi tablolar, seyirci, kapasite kontrolü), `seyirci` (168/168 seyircili takım-sezon),
`xg` (2022-23 – 2025-26), `kupalar`, `sosyal` (5 platform), `forma` (66/190 fiyat + TÜFE 2003=100).
Birleşik tablo: `data/skor_karti.csv`.

| Boyut | Tanım | Kaynak |
|---|---|---|
| Sadakat | 10 yıllık doluluk (2021-22 COVID kısıtlı sezon hariç) ve 5 platform takipçisinin log ölçekli skoru, eşit ağırlık | seyirci + sosyal ajanları |
| Başarı | Süper Lig + Türkiye Kupası + Süper Kupa (2016-17 – 2025-26) | kupalar ajanı |
| Gol + xG | 10 yıllık lig golü ve maç başı xG (2022-23 – 2025-26) eşit ağırlık; xG yoksa yalnız gol | matches.csv + xg ajanı |
| Galibiyet | 10 yılda lig galibiyeti toplamı | matches.csv |
| Forma uygunluğu | **Ters yönlü**: kulübün ev forması fiyatı ÷ aynı sezondaki kulüplerin medyan fiyatı; ortalaması düşük olan yüksek skor alır (dönem yanlılığını giderir). Kartta reel (TÜFE) fiyat ve ilk→son artış da gösterilir | forma ajanı |
| Son 3 sezon | 2023-24 – 2025-26 resmi puan (TFF puan silmeleri dahil) ve sıra ortalaması | team_season.csv |

Her boyut 19 kulüp arasında min-max ile 0-100'e ölçeklenir. **Genel skor 6 boyutun ortalamasıdır**; forma ters yönlü
olduğu için pahalı forma genel skoru düşürür. Verisi olmayan boyut (forma fiyatı bulunamayan 3 kulüp) ortalamaya
girmez. Son 3 sezonda hiç ligde olmayan kulübün o ekseni 0'dır.
Sınırlamalar: forma fiyatı 66/190 hücre (Başakşehir, Kasımpaşa, Gaziantep FK'da hiç yok; tek sezonluk değerler
düşük güvenli olarak işaretli), xG yalnızca son 4 sezon, Fatih Karagümrük doluluğu stat kapasitesi belirsizliği
nedeniyle güvenilir değil.
