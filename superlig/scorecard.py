"""19 kulüp için 6 boyutlu skor kartı (Instagram görselleri bunu kullanır).

Boyutlar:
 1. Sadakat   : 10 yıllık ortalama doluluk (seyirci/kapasite) + sosyal medya takipçisi (log, normalize)
 2. Başarı    : 10 yılda Süper Lig + Türkiye Kupası + Süper Kupa sayısı
 3. Gol       : 10 yılda lig golü toplamı
 4. Galibiyet : 10 yılda lig galibiyeti toplamı
 5. Forma     : 10 yıllık ev forması ortalama fiyatı, ilk→son artış %, TÜFE ile reel fiyat
 6. Form      : son 3 sezon puan ortalaması + sıralama ortalaması

Alt ajan çıktıları data/agents/<ad>/ altından okunur; dosya yoksa ilgili kolonlar boş kalır.
Her boyut 19 takım arasında 0-100'e ölçeklenir (min-max); radar bu skorları çizer.
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
AXES = [("sadakat", "Sadakat"), ("basari", "Başarı"), ("gol", "Gol"), ("galibiyet", "Galibiyet"),
        ("forma", "Forma fiyatı"), ("form", "Son 3 sezon")]


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
                                gol_10y=("atilan_gol", "sum"), galibiyet_10y=("galibiyet", "sum"))
    df = df.join(g)

    # 6: son 3 sezon
    l3 = lg[lg.sezon.isin(LAST3)].groupby("takim").agg(son3_sezon=("sezon", "size"),
                                                       son3_puan_ort=("puan", "mean"), son3_sira_ort=("sira", "mean"))
    df = df.join(l3)

    # 2: kupalar
    k = _read("kupalar/kupa_sayilari.csv")
    if k is not None:
        df = df.join(k.set_index("takim")[["super_lig", "turkiye_kupasi", "super_kupa", "toplam"]]
                     .rename(columns={"toplam": "kupa_10y"}))

    # 1: sadakat — doluluk + sosyal medya
    s10 = _read("seyirci/seyirci_10yil.csv")
    if s10 is not None:
        df = df.join(s10.set_index("takim")[["ort_seyirci_10y", "ort_kapasite_10y", "doluluk_10y"]])
    sm = _read("sosyal/takipci.csv")
    if sm is not None:
        sm = sm.dropna(subset=["takipci"])
        piv = sm.pivot_table(index="takim", columns="platform", values="takipci", aggfunc="max")
        piv.columns = [f"takipci_{c.lower().replace(' ', '_').replace('(', '').replace(')', '')}" for c in piv.columns]
        df = df.join(piv)
        df["takipci_toplam"] = piv.sum(axis=1, min_count=1).reindex(df.index)

    # 5: forma fiyatı + TÜFE
    f = _read("forma/forma_fiyat.csv")
    cpi = _read("forma/tufe.csv")
    if f is not None:
        f = f.dropna(subset=["fiyat_TL"]).copy()
        f["fiyat_TL"] = pd.to_numeric(f.fiyat_TL, errors="coerce")
        f = f.dropna(subset=["fiyat_TL"])
        if cpi is not None and not cpi.empty:
            cpi = cpi.dropna(subset=["tufe_2003_100"]).sort_values(["yil", "ay"])
            base = float(cpi.tufe_2003_100.iloc[-1])
            base_lbl = f"{int(cpi.yil.iloc[-1])}-{int(cpi.ay.iloc[-1]):02d}"
            # sezon fiyatı lansman ayına (Temmuz) göre deflate edilir; Temmuz yoksa o yılın son ayı
            def deflator(season):
                y = int(season[:4])
                c = cpi[(cpi.yil == y) & (cpi.ay == 7)]
                if c.empty:
                    c = cpi[cpi.yil == y]
                return float(c.tufe_2003_100.iloc[-1]) if not c.empty else np.nan
            f["reel_fiyat_TL"] = f.fiyat_TL * base / f.sezon.map(deflator)
            df.attrs["reel_baz"] = base_lbl
        agg = f.groupby("takim").agg(forma_sezon=("sezon", "size"), forma_ort_TL=("fiyat_TL", "mean"),
                                     forma_ilk_sezon=("sezon", "min"), forma_son_sezon=("sezon", "max"))
        first = f.sort_values("sezon").groupby("takim").fiyat_TL.first()
        last = f.sort_values("sezon").groupby("takim").fiyat_TL.last()
        agg["forma_ilk_TL"], agg["forma_son_TL"] = first, last
        agg["forma_artis_yuzde"] = (last / first - 1) * 100
        if "reel_fiyat_TL" in f:
            agg["forma_reel_ort_TL"] = f.groupby("takim").reel_fiyat_TL.mean()
        df = df.join(agg)

    # xG (ek bilgi; radarda yok)
    x = _read("xg/xg_10yil.csv")
    if x is not None:
        df = df.join(x.set_index("takim")[["xg_mac_basi", "xga_mac_basi"]])

    # ---- 0-100 skorlar
    sc = pd.DataFrame(index=df.index)
    parts = []
    if "doluluk_10y" in df:
        parts.append(_minmax(df.doluluk_10y))
    if "takipci_toplam" in df:
        parts.append(_minmax(np.log10(df.takipci_toplam)))
    sc["sadakat"] = pd.concat(parts, axis=1).mean(axis=1) if parts else np.nan
    sc["basari"] = _minmax(df.kupa_10y) if "kupa_10y" in df else np.nan
    sc["gol"] = _minmax(df.gol_10y)
    sc["galibiyet"] = _minmax(df.galibiyet_10y)
    col = "forma_reel_ort_TL" if "forma_reel_ort_TL" in df else ("forma_ort_TL" if "forma_ort_TL" in df else None)
    sc["forma"] = _minmax(df[col]) if col else np.nan
    sc["form"] = pd.concat([_minmax(df.son3_puan_ort), _minmax(df.son3_sira_ort, invert=True)], axis=1).mean(axis=1)
    sc.columns = [f"skor_{c}" for c in sc.columns]
    out = df.join(sc).reset_index()
    out.to_csv(config.DATA / "skor_karti.csv", index=False)
    return out
