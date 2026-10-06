"""Eksik veri ve kaynak raporu (reports/eksik_veri_raporu.md)."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from . import config


def _md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |")
    return "\n".join(out)


def write(res: dict):
    m, ts, att = res["matches"], res["team_season"], res["attendance"]
    conflicts, miss, cov, attempts = res["conflicts"], res["missing"], res["coverage"], res["attempts"]

    L = []
    L.append("# Süper Lig veri hattı — eksik veri ve kaynak raporu\n")
    L.append(f"Oluşturulma: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · "
             f"Kapsam: {config.SEASONS[0]} → {config.SEASONS[-1]}\n")

    # ---- kaynak erişimi
    L.append("## 1. Kaynaklara erişim\n")
    if attempts.empty:
        L.append("Kayıtlı istek yok.\n")
    else:
        a = attempts.copy()
        a["host"] = a.url.str.split("/").str[2]
        summ = (a.groupby(["kaynak", "host", "durum"]).size().unstack(fill_value=0).reset_index())
        L.append(_md_table(summ) + "\n")
    if res["blocked"]:
        L.append("**Erişilemeyen hostlar:** " + ", ".join(f"`{h}`" for h in res["blocked"]) + "\n")
        L.append("Bu çalıştırmada ortamın ağ politikası bu hostlara bağlantıyı reddetti (HTTP CONNECT 403). "
                 "Kod bu kaynakları her çalıştırmada önce dener; erişim açıldığında "
                 "`python run_pipeline.py` yeniden çalıştırılınca resmi kaynaklar otomatik kullanılır, "
                 "seyirci ve kapasite alanları dolar. Erişilemeyen sezonlar şu GitHub aynalarından alındı:\n")
        L.append(f"- football-data.co.uk → `{config.FD_MIRROR_REPO}` @ `{config.FD_MIRROR_SHA[:10]}` "
                 "(football-data.co.uk sezon dosyalarının birleştirilmiş kopyası)")
        L.append(f"- Sofascore → `{config.SS_MIRROR_REPO}` @ `{config.SS_MIRROR_SHA[:10]}` `data/site.db` "
                 "(Sofascore event id'li maç sonuçları; seyirci alanı yok)")
        L.append(f"- Ek çapraz kontrol: `openfootball/europe` @ `{config.OPENFOOTBALL_SHA[:10]}` ve "
                 f"`{config.SS_MIRROR_REPO}` `data/super_lig.db` (Transfermarkt maç raporları)\n")
    if res["sids"]:
        L.append("Sofascore sezon id'leri (seasons_data): " +
                 ", ".join(f"{config.season_label(y)}={sid}" for y, sid in sorted(res["sids"].items())) + "\n")
    else:
        L.append("Sofascore sezon id'leri `datafc.seasons_data(52)` ile bulunamadı (API erişilemedi).\n")

    # ---- kapsam
    L.append("## 2. Sezon bazında maç kapsamı\n")
    L.append("Her hücre, o kaynakta skoru bulunan maç sayısıdır. `matches.csv` sütunu birleştirilmiş sonuçtur.\n")
    L.append(_md_table(cov.reset_index().rename(columns={"index": "sezon"})) + "\n")
    filled = m[~m.dogrulayan_kaynaklar.str.contains("football-data") & ~m.celiski]
    if not filled.empty:
        L.append(f"football-data.co.uk (ayna) verisinde olmayan **{len(filled)} maç** diğer kaynaklardan "
                 "tamamlandı (en az iki kaynakla doğrulanmış):\n")
        L.append(_md_table(filled.groupby(["sezon", "kaynak"]).size().rename("mac").reset_index()) + "\n")
    hk = m[m.hukmen]
    if not hk.empty:
        L.append("Hükmen sonuçlanan (kaynakta `[awarded]` işaretli) maçlar:\n")
        L.append(_md_table(hk[["sezon", "tarih", "ev", "deplasman", "ev_gol", "dep_gol", "kaynak"]]) + "\n")

    # ---- çelişkiler
    L.append("## 3. Kaynak çelişkileri\n")
    if conflicts.empty:
        L.append("Çelişki yok.\n")
    else:
        sc = conflicts[conflicts.alan == "skor"]
        L.append(f"**Skor çelişkisi: {len(sc)} maç.** Kullanılan skor çoğunluk oyuyla seçildi "
                 "(eşitlikte öncelik: football-data > sofascore > openfootball > transfermarkt). "
                 "Tüm kaynak değerleri `data/celiskiler.csv` dosyasında.\n")
        cols = ["sezon", "ev", "deplasman", "football-data", "sofascore", "openfootball", "transfermarkt",
                "secilen", "secim_kurali"]
        L.append(_md_table(sc[[c for c in cols if c in sc]]) + "\n")
        tc = conflicts[conflicts.alan == "tarih"]
        if not tc.empty:
            L.append(f"Tarih farkı (2 günden fazla): {len(tc)} maç — "
                     + ", ".join(f"{s}: {n}" for s, n in tc.groupby("sezon").size().items()) + ".\n")
        oc = conflicts[~conflicts.alan.isin(["skor", "tarih"])]
        if not oc.empty:
            L.append(f"Seyirci/kapasite çelişkisi: {len(oc)} takım-sezon.\n")

    # ---- takım/sezon eksik ızgarası
    L.append("## 4. Takım / sezon bazında eksik veri\n")
    L.append("Gösterim: `✓` tam · `—` takım o sezon Süper Lig'de değil (tüm değerler NaN) · "
             "`S` ortalama seyirci eksik · `K` stadyum kapasitesi eksik · `M` maç skoru eksik\n")
    grid = {}
    for _, r in ts.iterrows():
        grid.setdefault(r.takim, {})[r.sezon] = "—" if not r.ligde else ""
    for _, r in miss[miss.durum == "eksik"].iterrows():
        code = {"ort_seyirci": "S", "kapasite": "K", "maçlar": "M"}[r.alan]
        grid[r.takim][r.sezon] += code
    g = pd.DataFrame(grid).T[config.SEASONS].replace("", "✓")
    g = g.loc[ts[ts.ligde].groupby("takim").size().sort_values(ascending=False).index]
    L.append(_md_table(g.reset_index().rename(columns={"index": "takim"})) + "\n")

    n_in = int(ts.ligde.sum())
    s_miss = int(((miss.alan == "ort_seyirci") & (miss.durum == "eksik")).sum())
    k_miss = int(((miss.alan == "kapasite") & (miss.durum == "eksik")).sum())
    mm = miss[(miss.alan == "maçlar") & (miss.durum == "eksik")]
    L.append(f"- Ligde olunan takım-sezon sayısı: **{n_in}**")
    L.append(f"- Maç skoru eksik takım-sezon: **{len(mm)}**")
    L.append(f"- Ortalama seyirci eksik: **{s_miss} / {n_in}**")
    L.append(f"- Stadyum kapasitesi eksik: **{k_miss} / {n_in}**\n")
    if not mm.empty:
        L.append(_md_table(mm[["takim", "sezon", "aciklama"]]) + "\n")

    # ---- isim eşleştirme
    L.append("## 5. Takım adı standardizasyonu\n")
    if res["unmapped"]:
        L.append("Eşleşmeyen adlar (bu maçlar dışarıda bırakıldı):\n")
        L.extend(f"- `{k}`: {n}" for k, n in res["unmapped"])
    else:
        L.append(f"Tüm kaynaklardaki {len(res['mapping'])} ad yazımı standart adlara eşlendi "
                 "(`data/team_mapping.csv`). Örnek: Sofascore'un 2016-17 için kullandığı "
                 "'Sincan Belediyesi Ankaraspor' → Osmanlıspor; football-data 'Buyuksehyr' → İstanbul Başakşehir. "
                 "Gaziantepspor (2016-17) ile Gaziantep FK ayrı kulüplerdir.\n")

    # ---- notlar
    L.append("## 6. Yöntem notları\n")
    L.append("- `team_season.csv` puan ve sıraları yalnızca `matches.csv` skorlarından hesaplanır. "
             "TFF'nin verdiği puan silme cezaları maç verisinde olmadığı için uygulanmamıştır; "
             "bu nedenle bazı sezonlarda resmi puan tablosundan sapma olabilir.")
    L.append("- Sıralama ölçütü: puan → ikili maçlarda puan → ikili averaj → ikili atılan gol → genel averaj → atılan gol.")
    L.append("- Sezon ataması: 15 Temmuz kesim tarihi; 2020'de COVID nedeniyle 15 Ağustos.")
    L.append("- Seyirci: Sofascore ortalaması yalnızca takımın iç saha maçlarının en az yarısında seyirci kaydı "
             "varsa kullanılır (`seyirci_mac` / `ev_mac`); aksi halde Wikipedia sezon tablosu. Sofascore'da "
             "seyirci kaydı çok seyrek olduğu için bu dönemde tüm değerler Wikipedia'dan geldi. "
             "Ham maç bazında Sofascore verisi: `data/raw/sofascore_mac_seyirci.csv`.")
    L.append("- Kapasite: Wikipedia sezon tablosu önce gelir. Sofascore'un etkinlik stadı bazı kulüplerde o sezon "
             "oynanan stadı değil güncel stadı gösteriyor (ör. Fatih Karagümrük 2021-22: Sofascore 6.500 / "
             "Wikipedia 76.761; Altay 2021-22: 58.008 / 14.000). İki değer de `celiskiler.csv`'de.")
    wd = m[(m.sezon == "2022-23") & (pd.to_datetime(m.tarih) >= "2023-02-06")
           & (m.ev.isin(["Gaziantep FK", "Hatayspor"]) | m.deplasman.isin(["Gaziantep FK", "Hatayspor"]))]
    if len(wd):
        L.append(f"- 2022-23'te deprem sonrası ligden çekilen Gaziantep FK ve Hatayspor'un kalan {len(wd)} maçı "
                 "football-data ve Transfermarkt'ta hükmen 3-0 olarak yer alıyor (Sofascore'da yok); "
                 "hesaplamaya dahil edildi.")

    config.REPORTS.mkdir(exist_ok=True)
    (config.REPORTS / "eksik_veri_raporu.md").write_text("\n".join(L) + "\n", encoding="utf-8")
