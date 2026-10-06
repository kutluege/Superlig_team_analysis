"""Eksik sezonlar için seyirci tahmini (doluluk oranı × o sezonun kapasitesi).

Gözlenen değerler değiştirilmez; tahminler ayrı dosyaya (data/attendance_tahmini.csv)
`yontem` sütunuyla işaretlenerek yazılır.

Yöntem:
  doluluk(takım) = ortalama( gözlenen ort_seyirci / kapasite )  — takımın verisi olan sezonlar
  tahmin(takım, sezon) = doluluk(takım) × kapasite(takım, sezon)
Takımın hiç gözlenen sezonu yoksa lig genelinin medyan doluluk oranı kullanılır (daha zayıf tahmin).
2020-21 seyircisiz oynandığı için tahmin edilmez.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

NO_FANS = {"2020-21": "COVID-19 nedeniyle seyircisiz; tahmin yapılmadı."}
PARTIAL = {"2019-20": "Mart 2020 sonrası maçlar seyircisizdi; tahmin seyircili maçların ortalamasını temsil eder."}

M_OBS = "gözlenen"
M_TEAM = "tahmin: takım doluluk oranı × kapasite"
M_LEAGUE = "tahmin: lig medyan doluluk oranı × kapasite"


def _occupancy(obs: pd.DataFrame) -> tuple[pd.Series, pd.Series, float]:
    occ = obs.ort_seyirci / obs.kapasite
    by_team = occ.groupby(obs.takim).mean()
    seasons = obs.groupby("takim").sezon.apply(lambda s: ", ".join(sorted(s)))
    return by_team, seasons, float(occ.median())


def estimate(att: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    a = att[att.ligde].copy()
    obs = a.dropna(subset=["ort_seyirci", "kapasite"])
    team_occ, team_seasons, league_occ = _occupancy(obs)

    rows = []
    for _, r in a.iterrows():
        out = {"takim": r.takim, "sezon": r.sezon, "kapasite": r.kapasite,
               "gozlenen_seyirci": r.ort_seyirci, "tahmini_seyirci": np.nan, "seyirci": np.nan,
               "yontem": "", "doluluk_orani": np.nan, "dayanak_sezonlar": "", "not": ""}
        if pd.notna(r.ort_seyirci):
            out.update(seyirci=r.ort_seyirci, yontem=M_OBS, kaynak=r.kaynak,
                       doluluk_orani=r.ort_seyirci / r.kapasite if pd.notna(r.kapasite) else np.nan)
        elif r.sezon in NO_FANS:
            out.update(yontem="yok", **{"not": NO_FANS[r.sezon]})
        elif pd.notna(r.kapasite):
            if r.takim in team_occ.index:
                occ, method, basis = team_occ[r.takim], M_TEAM, team_seasons[r.takim]
            else:
                occ, method, basis = league_occ, M_LEAGUE, "lig geneli (takımın gözlenen sezonu yok)"
            est = round(occ * r.kapasite)
            note = PARTIAL.get(r.sezon, "")
            base = obs[obs.takim == r.takim].kapasite
            if not base.empty and (r.kapasite > 2 * base.max() or r.kapasite < 0.5 * base.min()):
                note = (note + " " if note else "") + (
                    f"Stadyum kapasitesi dayanak sezonlardan çok farklı ({int(base.min())}-{int(base.max())} → "
                    f"{int(r.kapasite)}); tahmin güvenilmez.")
            out.update(tahmini_seyirci=est, seyirci=est, yontem=method, doluluk_orani=occ,
                       dayanak_sezonlar=basis, **{"not": note})
        rows.append(out)
    df = pd.DataFrame(rows)
    df["doluluk_orani"] = df.doluluk_orani.round(3)
    for c in ["kapasite", "gozlenen_seyirci", "tahmini_seyirci", "seyirci"]:
        df[c] = df[c].round().astype("Int64")

    # Geriye dönük doğrulama: her gözlenen değeri, o sezon hariç tutularak hesaplanan oranla tahmin et
    errs = []
    for idx, r in obs.iterrows():
        rest = obs[(obs.takim == r.takim) & (obs.index != idx)]
        if rest.empty:
            continue
        occ = (rest.ort_seyirci / rest.kapasite).mean()
        errs.append(abs(occ * r.kapasite - r.ort_seyirci) / r.ort_seyirci)
    stats = {"n_test": len(errs), "mape": float(np.mean(errs)) if errs else np.nan,
             "median_ape": float(np.median(errs)) if errs else np.nan, "league_occ": league_occ,
             "n_obs": int(df.yontem.eq(M_OBS).sum()), "n_team": int(df.yontem.eq(M_TEAM).sum()),
             "n_league": int(df.yontem.eq(M_LEAGUE).sum()), "n_none": int(df.yontem.eq("yok").sum())}
    cols = ["takim", "sezon", "seyirci", "gozlenen_seyirci", "tahmini_seyirci", "yontem", "kapasite",
            "doluluk_orani", "dayanak_sezonlar", "not"]
    return df[cols], stats


def run() -> tuple[pd.DataFrame, dict]:
    att = pd.read_csv(config.DATA / "attendance.csv")
    df, stats = estimate(att)
    df.to_csv(config.DATA / "attendance_tahmini.csv", index=False)
    return df, stats
