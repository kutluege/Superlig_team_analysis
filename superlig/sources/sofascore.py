"""Sofascore: maç sonuçları, seyirci ve stadyum kapasitesi.

Süper Lig unique-tournament id = 52. Sezon id'leri `datafc.seasons_data`
ile bulunur, haftalar `season_rounds_data`, maçlar `match_data` ile çekilir.
Seyirci (`event.attendance`) ve stadyum kapasitesi (`event.venue`) datafc
tarafından ayrıştırılmadığı için `/api/v1/event/{id}` yanıtından okunur.

Sofascore API'sine erişilemezse maç sonuçları, Sofascore event id'leriyle
derlenmiş GitHub aynasından (c0ze/super-lig, data/site.db) alınır. Aynada
seyirci bilgisi yoktur; bu durumda seyirci verisi boş kalır.
"""
from __future__ import annotations

import logging
import sqlite3
import tempfile

import pandas as pd

from .. import config
from ..net import Fetcher

log = logging.getLogger("superlig.sofascore")

SRC = "sofascore"
SRC_MIRROR = f"sofascore (ayna: {config.SS_MIRROR_REPO})"
SRC_TM_MIRROR = f"transfermarkt (ayna: {config.SS_MIRROR_REPO})"
TZ = "Europe/Istanbul"


def _datafc():
    try:
        import datafc
        return datafc
    except ImportError:
        log.error("datafc kurulu değil (pip install datafc)")
        return None


def season_ids(fetcher: Fetcher) -> dict[int, int]:
    """{sezon_başlangıç_yılı: sofascore_season_id}"""
    datafc = _datafc()
    url = f"{config.SOFASCORE_API}/unique-tournament/{config.SOFASCORE_TOURNAMENT_ID}/seasons"
    if datafc is None or fetcher.host_down(url):
        fetcher.note(SRC, url, "atlandi", "datafc yok ya da host erişilemez")
        return {}
    try:
        df = datafc.seasons_data(config.SOFASCORE_TOURNAMENT_ID, rate_limit=config.RATE_LIMITS["api.sofascore.com"])
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)[:200]}"
        log.warning("Sofascore seasons_data başarısız: %s", msg)
        fetcher.note(SRC, url, "hata", msg)
        fetcher._down.add("api.sofascore.com")
        return {}
    fetcher.note(SRC, url, "ok")
    out = {}
    for _, r in df.iterrows():
        yr = str(r["season_year"])  # ör. "16/17"
        if "/" in yr:
            out[2000 + int(yr.split("/")[0])] = int(r["season_id"])
    return {y: sid for y, sid in out.items() if y in config.SEASON_YEARS}


def _matches_api(fetcher: Fetcher, sids: dict[int, int]) -> pd.DataFrame:
    datafc = _datafc()
    frames = []
    for year, sid in sids.items():
        try:
            rounds = datafc.season_rounds_data(config.SOFASCORE_TOURNAMENT_ID, sid)
            col = "round_number" if "round_number" in rounds else "round"
            weeks = sorted({int(w) for w in rounds[col] if str(w).isdigit()})
        except Exception as e:
            log.warning("Sofascore %s hafta listesi alınamadı: %s", year, e)
            continue
        for w in weeks:
            try:
                df = datafc.match_data(config.SOFASCORE_TOURNAMENT_ID, sid, week_number=w)
            except Exception as e:
                log.warning("Sofascore %s hafta %s alınamadı: %s", year, w, e)
                continue
            df = df[df["status"].str.lower().eq("ended")]
            frames.append(pd.DataFrame({
                "sezon_yil": year,
                "tarih": pd.to_datetime(df["start_timestamp"], unit="s", utc=True)
                           .dt.tz_convert(TZ).dt.date,
                "ev_raw": df["home_team"], "dep_raw": df["away_team"],
                "ev_gol": df["home_score_current"], "dep_gol": df["away_score_current"],
                "sofascore_id": df["game_id"], "kaynak": SRC,
            }))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _sqlite(fetcher: Fetcher, url: str, kaynak: str) -> pd.DataFrame | None:
    raw = fetcher.get(url, kaynak, timeout=300)
    if raw is None:
        return None
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        f.write(raw)
        f.flush()
        con = sqlite3.connect(f"file:{f.name}?mode=ro", uri=True)
        try:
            return pd.read_sql("SELECT * FROM matches", con)
        finally:
            con.close()


def _matches_mirror(fetcher: Fetcher) -> pd.DataFrame:
    df = _sqlite(fetcher, config.SS_MIRROR_URL, SRC_MIRROR)
    if df is None:
        return pd.DataFrame()
    df["sezon_yil"] = pd.to_numeric(df["season"], errors="coerce")
    df = df[df["sezon_yil"].isin(config.SEASON_YEARS)].dropna(subset=["home_score", "away_score"])
    return pd.DataFrame({
        "sezon_yil": df["sezon_yil"].astype(int),
        "tarih": pd.to_datetime(df["start_timestamp"], unit="s", utc=True).dt.tz_convert(TZ).dt.date,
        "ev_raw": df["home_team"], "dep_raw": df["away_team"],
        "ev_gol": df["home_score"].astype(float), "dep_gol": df["away_score"].astype(float),
        "sofascore_id": df["id"].astype("int64"), "kaynak": SRC_MIRROR,
    })


def load_matches(fetcher: Fetcher, sids: dict[int, int]) -> pd.DataFrame:
    api = _matches_api(fetcher, sids) if sids else pd.DataFrame()
    have = set(api["sezon_yil"]) if not api.empty else set()
    missing = [y for y in config.SEASON_YEARS if y not in have]
    if missing:
        log.warning("Sofascore API'den alınamayan sezonlar: %s -> GitHub aynası",
                    [config.season_label(y) for y in missing])
        mirror = _matches_mirror(fetcher)
        if not mirror.empty:
            api = pd.concat([api, mirror[mirror["sezon_yil"].isin(missing)]], ignore_index=True)
    return api


def load_transfermarkt_mirror(fetcher: Fetcher) -> pd.DataFrame:
    """Aynı depodaki Transfermarkt kaynaklı skorlar (yalnızca çapraz kontrol)."""
    df = _sqlite(fetcher, config.TM_MIRROR_URL, SRC_TM_MIRROR)
    if df is None:
        return pd.DataFrame()
    df["sezon_yil"] = pd.to_numeric(df["season"], errors="coerce")
    df = df[df["sezon_yil"].isin(config.SEASON_YEARS)].dropna(subset=["home_score", "away_score"])
    return pd.DataFrame({
        "sezon_yil": df["sezon_yil"].astype(int), "tarih": pd.NaT,
        "ev_raw": df["home_team"], "dep_raw": df["away_team"],
        "ev_gol": df["home_score"].astype(float), "dep_gol": df["away_score"].astype(float),
        "kaynak": SRC_TM_MIRROR,
    })


def load_attendance(fetcher: Fetcher, matches: pd.DataFrame) -> pd.DataFrame:
    """Maç bazında seyirci ve stadyum kapasitesi (event detayından)."""
    rows = []
    ids = matches.dropna(subset=["sofascore_id"]) if "sofascore_id" in matches else pd.DataFrame()
    for _, m in ids.iterrows():
        url = f"{config.SOFASCORE_API}/event/{int(m['sofascore_id'])}"
        if fetcher.host_down(url):
            break  # host engelli: kalan binlerce isteği deneme, bir kez logla
        data = fetcher.get_json(url, SRC)
        if not data:
            continue
        ev = data.get("event", {})
        venue = ev.get("venue") or {}
        cap = (venue.get("stadium") or {}).get("capacity") or venue.get("capacity")
        rows.append({
            "sezon_yil": m["sezon_yil"], "ev": m["ev"], "deplasman": m["deplasman"],
            "sofascore_id": int(m["sofascore_id"]),
            "seyirci": ev.get("attendance"), "kapasite": cap,
            "stadyum": (venue.get("stadium") or {}).get("name") or venue.get("name"),
        })
    if fetcher.host_down(f"{config.SOFASCORE_API}/event/0"):
        skipped = len(ids) - len(rows)
        log.error("Sofascore event detayları alınamadı: %d maç için seyirci/kapasite "
                  "okunamadı (host erişilemez).", skipped)
        fetcher.note(SRC, f"{config.SOFASCORE_API}/event/{{id}}", "atlandi",
                     f"{skipped} maç atlandı: host erişilemez")
    return pd.DataFrame(rows)
