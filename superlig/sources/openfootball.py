"""openfootball/europe Football.TXT dosyaları (bağımsız çapraz kontrol)."""
from __future__ import annotations

import logging
import re
from datetime import date

import pandas as pd

from .. import config
from ..net import Fetcher

log = logging.getLogger("superlig.openfootball")
SRC = "openfootball"

_MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
_DATE = re.compile(r"^\s*(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2})\s+(\d{1,2})(?:\s+(\d{4}))?\s*$")
# "  21:00  Galatasaray  v Hatayspor  2-1 (0-0)  [awarded]"
_MATCH = re.compile(r"^\s+(?:\d{1,2}:\d{2}\s+)?(?P<home>\S.*?)\s+v\s+(?P<away>\S.*?)"
                    r"(?:\s+(?P<hg>\d+)-(?P<ag>\d+)(?:\s+\(\d+-\d+\))?)?\s*(?P<note>\[[^\]]*\])?\s*$")


def parse(text: str, year: int) -> pd.DataFrame:
    rows, current = [], None
    for line in text.splitlines():
        m = _DATE.match(line)
        if m:
            mon, day, yr = _MONTHS[m.group(2)], int(m.group(3)), m.group(4)
            if yr:
                current = date(int(yr), mon, day)
                continue
            # Yıl yazılmamış: Temmuz-Aralık sezonun ilk yılı, Ocak-Haziran ikinci yılı.
            # Ertelenen maçlar hafta sırasında listelendiği için tarihler biraz geri
            # gidebilir; ancak 5 aydan fazla geri gidiyorsa (ör. 2019-20'nin
            # Temmuz 2020 maçları) bir sonraki yıl kastedilmiştir.
            cand = date(year if mon >= 7 else year + 1, mon, day)
            if current is not None and (current - cand).days > 150:
                cand = date(cand.year + 1, mon, day)
            current = cand
            continue
        m = _MATCH.match(line)
        if m and current:
            rows.append({
                "sezon_yil": year, "tarih": current,
                "ev_raw": m["home"].strip(), "dep_raw": m["away"].strip(),
                "ev_gol": float(m["hg"]) if m["hg"] else float("nan"),
                "dep_gol": float(m["ag"]) if m["ag"] else float("nan"),
                "hukmen": bool(m["note"] and "award" in m["note"].lower()),
                "kaynak": SRC,
            })
    return pd.DataFrame(rows)


def load(fetcher: Fetcher) -> pd.DataFrame:
    frames = []
    for year in config.SEASON_YEARS:
        url = config.OPENFOOTBALL_URL.format(label=config.season_label(year))
        raw = fetcher.get(url, SRC)
        if raw is None:
            log.info("openfootball'da %s sezonu yok", config.season_label(year))
            continue
        frames.append(parse(raw.decode("utf-8"), year))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
