"""19 kulüp için 6 boyutlu skor kartı (Instagram görselleri bunu kullanır).

Tüm boyutlar GERÇEK yüzdelerdir (kulüpler arası min-max ölçekleme yok):
 1. Sadakat          : ortalama( 10 yıllık doluluk %, sosyal medya % )
                       sosyal %: platform başına sabit log ölçek (1.000 takipçi = 0, 100 milyon = 100),
                       kulübün verisi olan platformların ortalaması
 2. Başarı           : kazanılan kupa ÷ 10 yılda dağıtılan kupa (Süper Lig + Türkiye Kupası + Süper Kupa = 30)
 3. Gol + xG         : ortalama( gol payı = atılan ÷ (atılan + yenilen) [10 yıl],
                                  xG payı = xG ÷ (xG + xGA) [2022-23 – 2025-26] )
 4. Galibiyet        : galibiyet ÷ oynanan maç [10 yıl]
 5. Taraftara maliyet: forma uygunluğu = 50 × lig ortalaması ÷ kulübün 10 sezonluk ortalama forma fiyatı
                       (lig ortalaması = 50, yarı fiyat = 100, iki kat = 25; tavan 100). Fiyatlar aynı
                       sezonda karşılaştırılır: eksik sezonlar zincir endeksle tamamlanır (forma_panel.py)
 6. Son 3 sezon      : alınan resmi puan ÷ alınabilecek puan [2023-24 – 2025-26]
Genel skor: 6 boyutun ortalaması (verisi olmayan boyut hariç).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

TEAMS19 = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "İstanbul Başakşehir", "Konyaspor",
           "Antalyaspor", "Alanyaspor", "Kasımpaşa", "Kayserispor", "Sivasspor", "Çaykur Rizespor",
           "Gaziantep FK", "Göztepe", "Gençlerbirliği", "Fatih Karagümrük", "Ankaragücü", "Hatayspor",
           "Yeni Malatyaspor"]
AG = config.DATA / "agents"
LAST3 = config.SEASONS[-3:]
PLATFORMS = ["Instagram", "X", "Facebook", "TikTok", "YouTube"]
AXES = [("sadakat", "Sadakat"), ("basari", "Başarı"), ("gol", "Gol + xG"), ("galibiyet", "Galibiyet"),
        ("forma", "Taraftara maliyet"), ("form", "Son 3 sezon")]
TOTAL_TROPHIES = 30  # 10 sezon × 3 kupa
SOCIAL_LO, SOCIAL_HI = 3.0, 8.0  # log10 takipçi: 1.000 → %0, 100 milyon → %100


def _read(path, **kw):
    p = AG / path
    return pd.read_csv(p, **kw) if p.exists() else None


def _minmax(s: pd.Series, invert: bool = False) -> pd.Series:
    s = s.astype(float)
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or hi == lo:
        return pd.Series(np.where(s.notna(), 50.0, np.nan), index=s.index)
    out = (s - lo) / (hi - lo) * 100
    return 100 - out if invert else out


def build() -> pd.DataFrame:
    ts = pd.read_csv(config.DATA / "team_season.csv")
    lg = ts[ts.ligde & ts.takim.isin(TEAMS19)]
    df = pd.DataFrame(index=pd.Index(TEAMS19, name="takim"))

    # 3-4: gol ve galibiyet (lig maçları, matches.csv'den)
    g = lg.groupby("takim").agg(sezon_sayisi=("sezon", "size"), mac=("oynanan", "sum"),
                                gol_10y=("atilan_gol", "sum"), yenilen_10y=("yenilen_gol", "sum"),
                                galibiyet_10y=("galibiyet", "sum"))
    df = df.join(g)

    # 6: son 3 sezon
    l3 = lg[lg.sezon.isin(LAST3)].groupby("takim").agg(son3_sezon=("sezon", "size"),
                                                       son3_puan_ort=("resmi_puan", "mean"), son3_sira_ort=("resmi_sira", "mean"),
                                                       son3_puan=("resmi_puan", "sum"), son3_mac=("oynanan", "sum"))
    df = df.join(l3)

    # 2: kupalar
    k = _read("kupalar/kupa_sayilari.csv")
    if k is not None:
        df = df.join(k.set_index("takim")[["super_lig", "turkiye_kupasi", "super_kupa", "toplam"]]
                     .rename(columns={"toplam": "kupa_10y"}))

    # 1: sadakat — doluluk + sosyal medya
    s10 = _read("seyirci/seyirci_10yil.csv")
    if s10 is not None:
        s10 = s10.set_index("takim")
        # 2021-22 COVID kapasite kısıtlı; doluluğu yapay düşürdüğü için hariç tutulan sürüm tercih edilir
        if "doluluk_10y_2122_haric" in s10:
            s10["doluluk_10y"] = s10.doluluk_10y_2122_haric.fillna(s10.doluluk_10y)
            s10["ort_seyirci_10y"] = s10.ort_seyirci_10y_2122_haric.fillna(s10.ort_seyirci_10y)
        df = df.join(s10[["ort_seyirci_10y", "ort_kapasite_10y", "doluluk_10y", "sezon_sayisi_seyircili"]])
    sm = _read("sosyal/takipci.csv")
    if sm is not None:
        # resmi ana hesaplar: ikinci dil hesabı ve resmiyeti doğrulanamayan satırlar dışarıda
        sm = sm.dropna(subset=["takipci"])
        sm = sm[sm.platform.isin(PLATFORMS) & ~sm["not"].fillna("").str.contains("DOĞRULANMAMIŞ")]
        piv = sm.pivot_table(index="takim", columns="platform", values="takipci", aggfunc="max").reindex(df.index)
        df["takipci_toplam"] = piv.sum(axis=1, min_count=1)
        df["takipci_platform"] = piv.notna().sum(axis=1)
        for c in piv.columns:
            df[f"takipci_{c.lower()}"] = piv[c]
        # platform başına log10 → 0-100, kulübün verisi olan platformların ortalaması
        pct = ((np.log10(piv) - SOCIAL_LO) / (SOCIAL_HI - SOCIAL_LO) * 100).clip(0, 100)
        df["sosyal_yuzde"] = pct.mean(axis=1)

    # 5: forma — aynı sezonda karşılaştırılabilir panel (gerçek + zincir endeks tahmini) ve taraftara maliyet
    from . import forma_panel
    if forma_panel.SRC.exists():
        panel, _ = forma_panel.build_panel()
        cpi = _read("forma/tufe.csv")
        if cpi is not None and not cpi.empty:
            cpi = cpi.dropna(subset=["tufe_2003_100"]).sort_values(["yil", "ay"])
            base = float(cpi.tufe_2003_100.iloc[-1])
            df.attrs["reel_baz"] = f"{int(cpi.yil.iloc[-1])}-{int(cpi.ay.iloc[-1]):02d}"

            def deflator(season):  # lansman ayı Temmuz
                y = int(season[:4])
                c = cpi[(cpi.yil == y) & (cpi.ay == 7)]
                return float((c if not c.empty else cpi[cpi.yil == y]).tufe_2003_100.iloc[-1])
            panel["reel_TL"] = panel.fiyat_TL * base / panel.sezon.map(deflator)
        p = panel.dropna(subset=["fiyat_TL"])
        agg = p.groupby("takim").agg(forma_ort_TL=("fiyat_TL", "mean"), forma_maliyet_10y_TL=("fiyat_TL", "sum"),
                                     forma_gercek_sezon=("tur", lambda x: (x == "gerçek").sum()))
        if "reel_TL" in p:
            agg["forma_maliyet_10y_reel_TL"] = p.groupby("takim").reel_TL.sum()
            agg["forma_reel_ort_TL"] = p.groupby("takim").reel_TL.mean()
        first = p[p.sezon == config.SEASONS[0]].set_index("takim").fiyat_TL
        last = p[p.sezon == config.SEASONS[-1]].set_index("takim").fiyat_TL
        agg["forma_ilk_TL"], agg["forma_son_TL"] = first, last
        agg["forma_artis_yuzde"] = (last / first - 1) * 100
        # taraftara maliyet: 10 sezonun toplamı bugünkü TL ile; lig ortalamasına oranı
        cost = agg.forma_maliyet_10y_reel_TL if "forma_maliyet_10y_reel_TL" in agg else agg.forma_maliyet_10y_TL
        agg["forma_lig_orani"] = cost / cost.mean()
        df = df.join(agg)

    # xG (ek bilgi; radarda yok)
    x = _read("xg/xg_10yil.csv")
    if x is not None:
        df = df.join(x.set_index("takim")[["xg_mac_basi", "xga_mac_basi", "xg_toplam", "xga_toplam"]])

    # ---- gerçek yüzdeler (0-100)
    sc = pd.DataFrame(index=df.index)
    df["doluluk_yuzde"] = df.get("doluluk_10y") * 100 if "doluluk_10y" in df else np.nan
    sc["sadakat"] = df[[c for c in ("doluluk_yuzde", "sosyal_yuzde") if c in df]].mean(axis=1)
    sc["basari"] = df.kupa_10y / TOTAL_TROPHIES * 100 if "kupa_10y" in df else np.nan
    df["gol_payi"] = df.gol_10y / (df.gol_10y + df.yenilen_10y) * 100
    if "xg_toplam" in df:
        df["xg_payi"] = df.xg_toplam / (df.xg_toplam + df.xga_toplam) * 100
    sc["gol"] = df[[c for c in ("gol_payi", "xg_payi") if c in df]].mean(axis=1)
    df["galibiyet_yuzde"] = df.galibiyet_10y / df.mac * 100
    sc["galibiyet"] = df.galibiyet_yuzde
    sc["forma"] = (50 / df.forma_lig_orani).clip(upper=100) if "forma_lig_orani" in df else np.nan
    df["son3_puan_yuzde"] = df.son3_puan / (3 * df.son3_mac) * 100
    sc["form"] = df.son3_puan_yuzde.fillna(0.0)  # son 3 sezonda hiç Süper Lig'de değilse 0
    sc.columns = [f"skor_{c}" for c in sc.columns]
    out = df.join(sc)
    # Genel skor: 6 boyutun ortalaması (taraftara maliyet ters yönlü: pahalı forma skoru düşürür).
    # Verisi olmayan boyut (ör. forma fiyatı bulunamayan kulüp) ortalamaya girmez.
    out["genel_skor"] = out[[f"skor_{k}" for k, _ in AXES]].mean(axis=1)
    out["genel_boyut_sayisi"] = out[[f"skor_{k}" for k, _ in AXES]].notna().sum(axis=1)
    out = out.reset_index()
    out.to_csv(config.DATA / "skor_karti.csv", index=False)
    return out
