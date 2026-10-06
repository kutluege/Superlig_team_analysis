"""Wikipedia sezon sayfaları: seyirci ortalaması ve stadyum kapasitesi yedeği."""
from __future__ import annotations

import io
import logging
import re

import pandas as pd

from .. import config, teams
from ..net import Fetcher

log = logging.getLogger("superlig.wikipedia")
SRC = "wikipedia"


def _num(x) -> float:
    s = re.sub(r"\[.*?\]", "", str(x))
    s = re.sub(r"[^\d]", "", s)
    return float(s) if s else float("nan")


def _flatten(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" ".join(dict.fromkeys(map(str, c))) for c in df.columns]
    df.columns = [str(c).lower() for c in df.columns]
    return df


def _team_col(df):
    return next((c for c in df.columns if c.startswith(("team", "club", "takım"))), None)


def parse(html: str, year: int) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except ValueError:
        return pd.DataFrame()
    cap, att = {}, {}
    for t in map(_flatten, tables):
        tc = _team_col(t)
        if tc is None:
            continue
        cap_col = next((c for c in t.columns if "capacity" in c), None)
        avg_col = next((c for c in t.columns if "average" in c or "avg" in c), None)
        for _, r in t.iterrows():
            std = teams.standardize(re.sub(r"\[.*?\]|\(.*?\)", "", str(r[tc])).strip())
            if not std:
                continue
            if cap_col is not None and std not in cap:
                cap[std] = _num(r[cap_col])
            if avg_col is not None and std not in att:
                att[std] = _num(r[avg_col])
    names = set(cap) | set(att)
    return pd.DataFrame([{"sezon_yil": year, "takim": n,
                          "ort_seyirci": att.get(n, float("nan")),
                          "kapasite": cap.get(n, float("nan")), "kaynak": SRC} for n in names])


def load(fetcher: Fetcher) -> pd.DataFrame:
    frames = []
    for year in config.SEASON_YEARS:
        label = config.season_label(year).replace("-", "%E2%80%93")  # en dash
        raw = fetcher.get(config.WIKIPEDIA_URL.format(label=label), SRC)
        if raw is None:
            continue
        df = parse(raw.decode("utf-8", "replace"), year)
        if df.empty:
            log.info("Wikipedia %s sayfasında seyirci/kapasite tablosu bulunamadı",
                     config.season_label(year))
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
