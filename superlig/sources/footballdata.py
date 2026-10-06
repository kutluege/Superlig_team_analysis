"""football-data.co.uk Turkey (T1) sezon dosyaları.

Önce resmi URL denenir (her sezon için ayrı). Erişilemeyen sezonlar,
football-data.co.uk dosyalarını birleştiren GitHub aynasından tamamlanır.
"""
from __future__ import annotations

import io
import logging

import pandas as pd

from .. import config
from ..net import Fetcher

log = logging.getLogger("superlig.footballdata")

SRC = "football-data.co.uk"
SRC_MIRROR = f"football-data.co.uk (ayna: {config.FD_MIRROR_REPO})"
RAW_DIR = config.RAW / "football-data"


def _code(year: int) -> str:
    return f"{str(year)[-2:]}{str(year + 1)[-2:]}"


def _parse_official(raw: bytes, year: int) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(raw), encoding="latin-1")
    df = df.dropna(subset=["HomeTeam", "AwayTeam"])
    return pd.DataFrame({
        "sezon_yil": year,
        "tarih": pd.to_datetime(df["Date"], dayfirst=True, format="mixed").dt.date,
        "ev_raw": df["HomeTeam"].str.strip(),
        "dep_raw": df["AwayTeam"].str.strip(),
        "ev_gol": pd.to_numeric(df["FTHG"], errors="coerce"),
        "dep_gol": pd.to_numeric(df["FTAG"], errors="coerce"),
        "kaynak": SRC,
    })


def _mirror(fetcher: Fetcher) -> pd.DataFrame | None:
    raw = fetcher.get(config.FD_MIRROR_URL, SRC_MIRROR, timeout=300)
    if raw is None:
        return None
    df = pd.read_csv(io.BytesIO(raw), low_memory=False,
                     usecols=["Division", "MatchDate", "HomeTeam", "AwayTeam", "FTHome", "FTAway"])
    df = df[df["Division"] == "T1"].copy()
    df["MatchDate"] = pd.to_datetime(df["MatchDate"])
    df["sezon_yil"] = df["MatchDate"].map(config.season_of_date)
    return pd.DataFrame({
        "sezon_yil": df["sezon_yil"],
        "tarih": df["MatchDate"].dt.date,
        "ev_raw": df["HomeTeam"].str.strip(),
        "dep_raw": df["AwayTeam"].str.strip(),
        "ev_gol": pd.to_numeric(df["FTHome"], errors="coerce"),
        "dep_gol": pd.to_numeric(df["FTAway"], errors="coerce"),
        "kaynak": SRC_MIRROR,
    })


def load(fetcher: Fetcher) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    frames, missing = [], []
    for year in config.SEASON_YEARS:
        url = config.FOOTBALL_DATA_URL.format(code=_code(year))
        raw = fetcher.get(url, SRC)
        if raw is None:
            missing.append(year)
            continue
        try:
            frames.append(_parse_official(raw, year))
            log.info("football-data.co.uk %s indirildi", config.season_label(year))
        except Exception as e:  # bozuk dosya: logla, aynadan dene
            log.warning("football-data.co.uk %s çözümlenemedi: %s", year, e)
            missing.append(year)

    if missing:
        log.warning("football-data.co.uk resmi siteden alınamayan sezonlar: %s -> "
                    "GitHub aynası deneniyor", [config.season_label(y) for y in missing])
        mirror = _mirror(fetcher)
        if mirror is not None:
            for year in missing:
                part = mirror[mirror["sezon_yil"] == year]
                if part.empty:
                    log.warning("Aynada %s sezonu yok", config.season_label(year))
                    continue
                frames.append(part)

    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    # Ham sezon dilimlerini depoda sakla (yeniden üretilebilirlik)
    for year, part in out.groupby("sezon_yil"):
        part.to_csv(RAW_DIR / f"T1_{config.season_label(year)}.csv", index=False)
    return out
