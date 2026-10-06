# Resmi kulüp hesapları: takipçi sayıları (6 Ekim 2026)

Tüm değerler `takipci.csv` dosyasından gelir (takim, platform, hesap, takipci, olcum_tarihi, kaynak_url, not). Hiçbir sayı tahmin edilmedi; bulunamayan hücreler `—` ile boş bırakıldı. Toplayıcı betik: `collect.py` + `plan.json` (aynı klasörde).

## Takım × platform tablosu

Instagram ve X sütunları öncelikli veridir. "IG+X" sütununda yalnızca ana X hesabı sayılır (Galatasaray'ın İngilizce hesabı hariç).

| Takım | Instagram | X | Facebook | TikTok | YouTube | IG+X |
|---|---|---|---|---|---|---|
| Galatasaray | 18,14 mn | 14,93 mn | 12,00 mn | 4,80 mn | 3,97 mn | 33,08 mn |
| Fenerbahçe | 11,95 mn | 12,75 mn | 8,90 mn | 2,30 mn | 3,18 mn | 24,70 mn |
| Beşiktaş | 7,94 mn | 5,91 mn | 5,50 mn | 1,60 mn | 1,76 mn | 13,85 mn |
| Trabzonspor | 2,98 mn | 2,04 mn | 4,10 mn | 1,40 mn | 428,0 bin | 5,01 mn |
| İstanbul Başakşehir | 335,5 bin | 176,6 bin | 150,0 bin | 52,9 bin | 17,8 bin | 512,1 bin |
| Konyaspor | 372,9 bin | 291,5 bin | 338,0 bin | 73,4 bin | 39,9 bin | 664,4 bin |
| Antalyaspor | 199,5 bin | 216,4 bin | 80,0 bin | — | 8,2 bin | 415,9 bin |
| Alanyaspor | 128,1 bin | 68,6 bin | 75,0 bin | 1,4 bin | 3,6 bin | 196,7 bin |
| Kasımpaşa | — | 63,6 bin | — | 7,6 bin | 3,1 bin | eksik (yalnız X) |
| Kayserispor | 190,0 bin | — | — | — | — | eksik (yalnız IG) |
| Sivasspor | 229,0 bin | 142,2 bin | — | 44,0 bin | 12,3 bin | 371,2 bin |
| Çaykur Rizespor | 172,1 bin | 110,5 bin | — | 4,1 bin | 10,0 bin | 282,6 bin |
| Gaziantep FK | — | 105,9 bin | 68,0 bin | — | 6,2 bin | eksik (yalnız X) |
| Göztepe | 403,4 bin | 268,3 bin | 200,0 bin | 12,7 bin | 40,1 bin | 671,7 bin |
| Gençlerbirliği | — | 79,0 bin | 110,0 bin | 9,1 bin | 9,4 bin | eksik (yalnız X) |
| Fatih Karagümrük | — | 47,0 bin | 25,0 bin | 23 | — | eksik (yalnız X) |
| Ankaragücü | — | 150,1 bin | 103,0 bin | — | 23,0 bin | eksik (yalnız X) |
| Hatayspor | — | 109,0 bin | 138,0 bin | — | 8,1 bin | eksik (yalnız X) |
| Yeni Malatyaspor | 188,5 bin | — | 52,0 bin | — | — | eksik (yalnız IG) |

Ek satır: `X_EN`, Galatasaray'ın İngilizce resmi hesabı (@galatasaray) = 1,11 mn. Ana hesap @GalatasaraySK = 14,93 mn.

## Kapsam

| Platform | Dolu / 19 | Yöntem |
|---|---|---|
| X | 17 | FxTwitter genel API (tam sayı) |
| Instagram | 13 (11 3. taraf izleyici, 2 haber) | instastatistics.com; Kayserispor ve Sivasspor haberden |
| Facebook | 15 | Facebook sayfa eklentisi (yuvarlak) + Fenerbahçe için CIES |
| TikTok | 13 | TikTok profil sayfası (yuvarlak) |
| YouTube | 16 | YouTube kanal sayfası (yuvarlak) |

Instagram + X birlikte olan 11 takım: Galatasaray, Fenerbahçe, Beşiktaş, Trabzonspor, Başakşehir, Konyaspor, Antalyaspor, Alanyaspor, Sivasspor, Çaykur Rizespor, Göztepe.

## Eksikler

- **Instagram yok (6 takım):** Kasımpaşa, Gaziantep FK, Gençlerbirliği, Fatih Karagümrük, Ankaragücü, Hatayspor. instagram.com giriş duvarı arkasında (302 → login), Instastatistics bu hesapları izlemiyor, haber/Wikipedia/başka izleyicide sayı bulunamadı. Kulüp sitelerindeki hesap adları: kasimpasask, gaziantepfk, genclerbirligisk, karagumruk_sk, ankaragucu (Hatayspor'un resmi IG adı bulunamadı).
- **X yok (2 takım):** Kayserispor (resmi @kayserispor hesabı askıya alınmış; @Kayserispor_FK 25 takipçili önemsiz hesap, alınmadı) ve Yeni Malatyaspor (resmi hesap bulunamadı; kulüp sitesi yok).
- **Kayserispor:** yalnızca Instagram (haberden). **Yeni Malatyaspor:** Instagram + Facebook; kulübün güncel statüsü doğrulanmadı.
- **Tek platformda X'e sahip, IG yok olan 6 takımın** IG+X toplamı hesaplanamaz. Log-normalizasyonda IG için ayrı bir yedek (ör. Facebook veya X oranı) gerekebilir; bu karar sende.

## Dikkat edilmesi gerekenler

1. **Tarihler:** X, Facebook, TikTok, YouTube = 2026-10-06 (çekim günü). Instagram = Instastatistics'in gösterdiği tarih: Galatasaray/Fenerbahçe/Beşiktaş/Trabzonspor 2026-10-06, Başakşehir 09-23, Konyaspor/Antalyaspor/Alanyaspor/Rizespor 09-24, Göztepe 09-21, Yeni Malatyaspor 09-20. Kayserispor ve Sivasspor 2026-08-22 haberinden (bin düzeyinde yuvarlak).
2. **Instagram 3. taraf kaynaktan:** doğrudan platformdan değil. Çapraz kontrol: CIES (Mayıs 2026) Galatasaray 18,1 / Fenerbahçe 11,7 / Beşiktaş 7,6 mn; Instastatistics ile uyumlu. Antalyaspor için haber 194 bin, Instastatistics 199 bin (Eylül).
3. **X hesap seçimi:** Galatasaray'ın ana hesabı @GalatasaraySK (galatasaray.org bağlantısı); @galatasaray İngilizce hesaptır. CIES'in Galatasaray X = 16,2 mn değeri iki hesabın toplamına yakındır (14,93 + 1,11). Fenerbahçe için CIES 13,47 mn, doğrudan @Fenerbahce 12,75 mn: CIES muhtemelen ek resmi hesapları da sayıyor; ana hesap değeri alındı. Beşiktaş benzer (CIES 6,26 / @Besiktas 5,91).
4. **Yuvarlama:** Facebook (100 bin / 1 bin düzeyi), TikTok (büyük hesaplarda 100 bin düzeyi), YouTube (3 anlamlı hane) yuvarlak gelir; log-normalizasyon için yeterli ama tam sayı sanılmamalı. Instagram ve X tam sayıdır.
5. **Fenerbahçe Facebook** doğrudan alınamadı; CIES Mayıs 2026 değeri (8,9 mn) kullanıldı.
6. **Trabzonspor Instagram sıçraması:** Mart-Nisan 2026 haberinde ~1,5 mn, şimdi 2,98 mn. Basın özetleri bunu Mohamed Salah transferine bağlıyor; ben doğrulamadım. Loyalty skorunda bu ani artış etkili olabilir.
7. **Düşük güvenilirlikli satırlar** (`not` sütunu "DOĞRULANMAMIŞ" içerir): TikTok Alanyaspor (@alanyasporkulubu), Çaykur Rizespor (@crizesporas), Fatih Karagümrük (@karagumruk_sk, 23 takipçi); Facebook Hatayspor ("Hatayspor") ve Yeni Malatyaspor. Bu hesapların resmî olduğu kulüp sitesinden teyit edilemedi. Skorda dışarıda tutmak daha güvenli.
8. **Hariç tutulan bulgular:** Çaykur Rizespor Facebook sayfası (372 takipçi, resmî olduğu belirsiz), Kasımpaşa ve Sivasspor Facebook sayfaları (eklenti veri vermedi), Beşiktaş TikTok'ta sahte @besiktas (3,8 bin; resmî hesap @besiktasjk).
9. **YouTube kanal seçimi:** Konyaspor için kulüp sitesinin bağlantılı kanalı (@KonyasporTVorg, 39,9 bin). Antalyaspor için siteyle bağlantılı kanal (@AntalyasporOriginals, 8,25 bin). Kayserispor ve Fatih Karagümrük için resmî kanal bulunamadı.
10. **Erişilemeyen kaynaklar:** socialblade, hypeauditor, starngage, trackalytics 403; WebFetch instagram.com/hypeauditor'u engelliyor; X'in kendi sayfası takipçi sayısını sunucu tarafında vermiyor. X için FxTwitter API'si, resmi olmayan ama x.com profil verisini yansıtan bir hizmettir; zaman zaman geçici 404 döndü, yeniden denendi.

## Kaynaklar

- Instagram: https://instastatistics.com/<hesap>
- X: https://api.fxtwitter.com/<hesap>
- Facebook: https://www.facebook.com/plugins/page.php?href=...
- TikTok: https://www.tiktok.com/@<hesap>
- YouTube: https://www.youtube.com/@<kanal>
- CIES çapraz kontrol: https://football-observatory.com/IMG/sites/b5wp/2025/wp548/en/data/data.js
- Haber (Kayserispor, Sivasspor IG): https://sivas360.com/spor/sivasspor-sosyal-medyada-zirve-yarisinda-ilk-3te/26764429
- Resmi hesap adları: kulüp siteleri (galatasaray.org, ibfk.com.tr, konyaspor.org.tr, antalyaspor.com.tr, alanyaspor.org.tr, kasimpasa.com.tr, sivasspor.org.tr, gaziantepfk.org, goztepe.org.tr, genclerbirligi.org.tr, ankaragucu.org.tr, karagumruk.com)
