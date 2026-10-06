"""Forma fiyatı paneli: 19 kulüp × 10 sezon, aynı sezonda karşılaştırılabilir.

Gerçek fiyat (kaynaklı) yoksa, kulübün zamanca en yakın gerçek fiyatı, fiyatı bilinen
kulüplerin sezondan sezona medyan artışıyla (zincir endeks) o sezona taşınır:

    endeks[s] = endeks[s-1] × medyan( fiyat[k, s] / fiyat[k, s-1] )   (iki sezonda da fiyatı olan k kulüpleri)
    tahmin[t, s] = fiyat[t, k] × endeks[s] / endeks[k]                  (k = t'nin en yakın gerçek sezonu)

Hiç gerçek fiyatı olmayan kulüp tahmin edilmez. Tahminler `tur=tahmin` ile işaretlenir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

SRC = config.DATA / "agents" / "forma" / "forma_fiyat.csv"


def _real() -> pd.DataFrame:
    f = pd.read_csv(SRC)
    f["fiyat_TL"] = pd.to_numeric(f.fiyat_TL, errors="coerce")
    f = f.dropna(subset=["fiyat_TL"])
    return f[~f["not"].fillna("").str.contains("BELİRSİZ_ÜRÜN")]


def chain_index(f: pd.DataFrame) -> pd.Series:
    piv = f.pivot_table(index="takim", columns="sezon", values="fiyat_TL", aggfunc="first").reindex(columns=config.SEASONS)
    idx, growth = [1.0], {}
    for a, b in zip(config.SEASONS, config.SEASONS[1:]):
        both = piv[[a, b]].dropna()
        if len(both) >= 2:
            g = float((both[b] / both[a]).median())
            how = f"{len(both)} kulübün medyan artışı"
        else:  # ortak kulüp yoksa sezon medyanlarının oranı
            g = float(piv[b].median() / piv[a].median())
            how = "sezon medyanları oranı (ortak kulüp <2)"
        growth[b] = (g, how)
        idx.append(idx[-1] * g)
    s = pd.Series(idx, index=config.SEASONS, name="endeks")
    s.attrs["growth"] = growth
    return s


def build_panel(f: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.Series]:
    from .scorecard import TEAMS19
    f = _real() if f is None else f
    I = chain_index(f)
    pos = {s: i for i, s in enumerate(config.SEASONS)}
    rows = []
    for t in TEAMS19:
        real = f[f.takim == t].set_index("sezon")
        for s in config.SEASONS:
            if s in real.index:
                r = real.loc[s]
                rows.append({"takim": t, "sezon": s, "fiyat_TL": float(r.fiyat_TL), "tur": "gerçek",
                             "dayanak_sezon": s, "kaynak_url": r.kaynak_url})
            elif len(real):
                k = min(real.index, key=lambda x: (abs(pos[x] - pos[s]), x))
                est = float(real.loc[k].fiyat_TL) * I[s] / I[k]
                rows.append({"takim": t, "sezon": s, "fiyat_TL": round(est, 2), "tur": "tahmin",
                             "dayanak_sezon": k, "kaynak_url": ""})
            else:
                rows.append({"takim": t, "sezon": s, "fiyat_TL": np.nan, "tur": "yok",
                             "dayanak_sezon": "", "kaynak_url": ""})
    return pd.DataFrame(rows), I


def backtest(f: pd.DataFrame | None = None) -> dict:
    """Her gerçek fiyatı, o hücre çıkarılmış veriyle tahmin edip hatayı ölçer."""
    f = _real() if f is None else f
    errs = []
    for i, r in f.iterrows():
        rest = f.drop(index=i)
        if (rest.takim == r.takim).sum() == 0:
            continue
        panel, _ = build_panel(rest)
        est = panel[(panel.takim == r.takim) & (panel.sezon == r.sezon)].fiyat_TL.iloc[0]
        errs.append(abs(est - r.fiyat_TL) / r.fiyat_TL)
    return {"n": len(errs), "mape": float(np.mean(errs)), "medyan": float(np.median(errs))}


def run() -> tuple[pd.DataFrame, dict]:
    panel, I = build_panel()
    bt = backtest()
    panel.to_csv(config.DATA / "forma_panel.csv", index=False)
    pd.DataFrame({"sezon": I.index, "endeks": I.values,
                  "artis": [None] + [round(I.attrs["growth"][s][0], 3) for s in I.index[1:]],
                  "yontem": [None] + [I.attrs["growth"][s][1] for s in I.index[1:]]}
                 ).to_csv(config.DATA / "forma_endeks.csv", index=False)
    return panel, bt
