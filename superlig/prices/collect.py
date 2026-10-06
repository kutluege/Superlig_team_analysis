"""Forma ve kombine fiyatlarını Wayback Machine kopyalarından toplar.

Her takım × sezon × tür (forma/kombine) bir iştir. İlerleme
`data/fiyat_durum.json` dosyasına her işten sonra yazılır; script yeniden
çalıştırıldığında tamamlanan işler atlanır, hata alanlar yeniden denenir.
HTTP yanıtları da önbellekte olduğundan yeniden çalıştırma ucuzdur.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

import pandas as pd

from .. import config
from . import extract
from .wayback import Capture, Wayback, WaybackUnavailable

log = logging.getLogger("superlig.prices")

TEAMS = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir", "Konyaspor", "Antalyaspor",
         "Alanyaspor", "Kasımpaşa", "Kayserispor", "Sivasspor", "Rizespor", "Gaziantep FK", "Göztepe",
         "Gençlerbirliği", "Fatih Karagümrük", "Ankaragücü", "Hatayspor", "Yeni Malatyaspor"]
# team_season.csv'deki standart adlar
STD = {"Başakşehir": "İstanbul Başakşehir", "Rizespor": "Çaykur Rizespor"}
# Ligden çekilme (matches.csv: kalan maçlar hükmen 0-3)
WITHDRAWN = {("Gaziantep FK", "2022-23"): "Şubat 2023 depremi sonrası ligden çekildi; kalan maçlar hükmen.",
             ("Hatayspor", "2022-23"): "Şubat 2023 depremi sonrası ligden çekildi; kalan maçlar hükmen."}

FORMA_COLS = ["takim", "sezon", "fiyat_TL", "kaynak_url", "snapshot_tarihi", "not"]
KOMBINE_COLS = ["takim", "sezon", "en_ucuz_TL", "en_pahali_TL", "kaynak_url", "snapshot_tarihi", "not"]

URL_RX = r"(?i).*(forma|jersey|kombine|abonman|sezonluk).*"
NOT_ADULT_HOME = re.compile(
    r"cocuk|kids?\b|junior|bebek|baby|kadin|women|woman|bayan|deplasman|away|ucuncu|third|3rd|"
    r"alternatif|kaleci|goalkeeper|antrenman|training|isinma|mac-oncesi|prematch|pre-match|retro|"
    r"nostalji|imzali|uzun-kollu|long-sleeve|mini|takim-seti|kit-|baski|tisort|t-shirt|sweat|"
    r"kilif|anahtarlik|magnet|maske|corap|sort|esofman|ceket|bayrak|atki|bere|sapka|canta|bardak", re.I)
HOME = re.compile(r"ic-saha|icsaha|ic_saha|evsahibi|ev-sahibi|home|1-forma|birinci", re.I)
PRODUCT = re.compile(r"-p-|/urun|/product|/p/|\.html|-\d{4,}", re.I)


def window(season: str) -> tuple[str, str]:
    y = int(season[:4])
    return f"{y}0501", f"{y}0930"


def league_note(takim: str, season: str, ts: pd.DataFrame) -> str:
    std = STD.get(takim, takim)
    row = ts[(ts.takim == std) & (ts.sezon == season)]
    if row.empty or not bool(row.ligde.iloc[0]):
        return "Takım bu sezon Süper Lig'de değil."
    return WITHDRAWN.get((takim, season), "")


def _join(*parts) -> str:
    return " ".join(p for p in parts if p)


class Collector:
    def __init__(self, retry_missing: bool = False):
        self.wb = Wayback()
        self.state_path = config.DATA / "fiyat_durum.json"
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        self.retry_missing = retry_missing
        self.sources = pd.read_csv(config.DATA / "sources.csv")
        self.ts = pd.read_csv(config.DATA / "team_season.csv")
        self.cdx_memo: dict[tuple, list[Capture]] = {}

    # ------------------------------------------------------------ yardımcılar
    def _save_state(self):
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=1))

    def _domains(self, takim: str, kinds: tuple[str, ...]) -> list[str]:
        s = self.sources[(self.sources.takim == takim) & self.sources.tur.isin(kinds)]
        s = s.assign(_o=s.tur.map({k: i for i, k in enumerate(kinds)})).sort_values("_o", kind="stable")
        doms = list(dict.fromkeys(s.alan_adi))
        # matchType=domain alt alan adlarını da kapsar: store.x.com.tr, x.com.tr sorgusunda zaten var
        return [d for d in doms if not any(d != o and d.endswith("." + o) for o in doms)]

    def _captures(self, domain: str, season: str) -> list[Capture]:
        key = (domain, season)
        if key not in self.cdx_memo:
            start, end = window(season)
            self.cdx_memo[key] = self.wb.cdx(domain, start, end, url_regex=URL_RX)
        return self.cdx_memo[key]

    # ------------------------------------------------------------ forma
    def _forma_candidates(self, caps: list[Capture], y: int) -> list[tuple[int, Capture]]:
        out = []
        for c in caps:
            u = extract.ascii_lower(c.original)
            if not re.search(r"forma|jersey", u) or NOT_ADULT_HOME.search(u):
                continue
            score = 0
            score += 3 if extract.has_season(u, y) else 0
            score += 2 if HOME.search(u) else 0
            score += 1 if PRODUCT.search(u) else 0
            if extract.has_season(u, y - 1) or extract.has_season(u, y + 1):
                score -= 4  # başka sezonun ürünü
            out.append((score, c))
        return sorted(out, key=lambda x: (-x[0], x[1].timestamp))

    def forma(self, takim: str, season: str) -> dict:
        y = int(season[:4])
        start, end = window(season)
        domains = self._domains(takim, ("magaza", "magaza_eski", "resmi_site", "resmi_site_eski"))
        if not domains:
            return {"durum": "bulunamadi", "neden": "sources.csv'de bu takım için alan adı yok."}
        tried, reasons = 0, []
        for d in domains:
            for score, c in self._forma_candidates(self._captures(d, season), y)[:6]:
                if score < 3 and tried >= 3:
                    break
                cap = self.wb.earliest(c.original, start, end) or c
                html = self.wb.fetch(cap)
                tried += 1
                if html is None:
                    reasons.append(f"{cap.url}: kopya açılamadı")
                    continue
                title = extract.ascii_lower(extract.heading(html))
                if not (extract.has_season(cap.original, y) or extract.has_season(title, y)):
                    reasons.append(f"{cap.url}: sayfada {season} sezon bilgisi yok, atlandı")
                    continue
                if NOT_ADULT_HOME.search(title):
                    reasons.append(f"{cap.url}: yetişkin ev forması değil, atlandı")
                    continue
                price, note = extract.jersey_price(html)
                if price is None:
                    reasons.append(f"{cap.url}: {note}")
                    continue
                return {"durum": "tamam", "fiyat_TL": round(price, 2), "kaynak_url": cap.url,
                        "snapshot_tarihi": cap.date, "not": note}
        if not tried:
            return {"durum": "bulunamadi",
                    "neden": f"{', '.join(domains)} için {start}-{end} aralığında forma ürün sayfası kopyası yok."}
        return {"durum": "bulunamadi", "neden": "; ".join(reasons[:4])}

    # ------------------------------------------------------------ kombine
    def kombine(self, takim: str, season: str) -> dict:
        y = int(season[:4])
        start, end = window(season)
        domains = self._domains(takim, ("resmi_site", "resmi_site_eski", "magaza", "magaza_eski"))
        if not domains:
            return {"durum": "bulunamadi", "neden": "sources.csv'de bu takım için alan adı yok."}
        cands = []
        for d in domains:
            for c in self._captures(d, season):
                u = extract.ascii_lower(c.original)
                if not re.search(r"kombine|abonman|sezonluk", u):
                    continue
                score = (3 if extract.has_season(u, y) else 0) + (1 if "fiyat" in u else 0)
                if extract.has_season(u, y - 1) or extract.has_season(u, y + 1):
                    score -= 4
                cands.append((score, c))
        cands.sort(key=lambda x: (-x[0], x[1].timestamp))
        reasons = []
        for score, c in cands[:6]:
            cap = self.wb.earliest(c.original, start, end) or c
            html = self.wb.fetch(cap)
            if html is None:
                reasons.append(f"{cap.url}: kopya açılamadı")
                continue
            if not extract.has_season(cap.original + " " + html[:200000], y):
                reasons.append(f"{cap.url}: sayfada {season} sezon bilgisi yok, atlandı")
                continue
            lo, hi, note = extract.kombine_prices(html)
            if lo is None:
                reasons.append(f"{cap.url}: {note}")
                continue
            return {"durum": "tamam", "en_ucuz_TL": round(lo, 2), "en_pahali_TL": round(hi, 2),
                    "kaynak_url": cap.url, "snapshot_tarihi": cap.date, "not": note}
        if not cands:
            return {"durum": "bulunamadi",
                    "neden": f"{', '.join(domains)} için {start}-{end} aralığında kombine sayfası kopyası yok."}
        return {"durum": "bulunamadi", "neden": "; ".join(reasons[:4])}

    # ------------------------------------------------------------ çalıştır
    def run(self, kinds=("forma", "kombine"), teams=None, seasons=None):
        teams = teams or TEAMS
        seasons = seasons or config.SEASONS
        protected = {k: _filled(k) for k in kinds}
        unavailable = None
        for kind in kinds:
            for t in teams:
                for s in seasons:
                    key = f"{kind}|{t}|{s}"
                    if (t, s) in protected[kind]:
                        self.state[key] = {"durum": "korundu", "neden": "Mevcut dosyada dolu; dokunulmadı."}
                        continue
                    prev = self.state.get(key, {})
                    if prev.get("durum") == "tamam" or (prev.get("durum") == "bulunamadi" and not self.retry_missing):
                        continue
                    if unavailable:
                        self.state[key] = {"durum": "hata", "neden": unavailable}
                        continue
                    try:
                        res = getattr(self, kind)(t, s)
                    except WaybackUnavailable as e:
                        unavailable = str(e)
                        log.error("%s — kalan işler sonraki çalıştırmaya bırakıldı.", unavailable)
                        res = {"durum": "hata", "neden": unavailable}
                    except Exception as e:  # beklenmeyen hata: logla, devam et
                        log.exception("%s başarısız", key)
                        res = {"durum": "hata", "neden": f"{type(e).__name__}: {e}"}
                    res["zaman"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                    self.state[key] = res
                    self._save_state()
                    log.info("%s -> %s", key, res["durum"])
        self._save_state()
        write_outputs(self.state, self.ts)
        return unavailable


def _filled(kind: str) -> set[tuple[str, str]]:
    path = config.DATA / f"{kind}.csv"
    if not path.exists():
        return set()
    df = pd.read_csv(path, dtype=str)
    col = "fiyat_TL" if kind == "forma" else "en_ucuz_TL"
    df = df[df[col].notna() & (df[col].str.strip() != "")]
    return set(zip(df.takim, df.sezon))


def write_outputs(state: dict, ts: pd.DataFrame):
    rows = {"forma": [], "kombine": []}
    missing = []
    for kind in ("forma", "kombine"):
        path = config.DATA / f"{kind}.csv"
        old = pd.read_csv(path, dtype=str).fillna("") if path.exists() else pd.DataFrame()
        cols = FORMA_COLS if kind == "forma" else KOMBINE_COLS
        for t in TEAMS:
            for s in config.SEASONS:
                st = state.get(f"{kind}|{t}|{s}", {"durum": "beklemede", "neden": "Henüz denenmedi."})
                lg = league_note(t, s, ts)
                if st["durum"] == "korundu":
                    r = old[(old.takim == t) & (old.sezon == s)].iloc[0].to_dict()
                    rows[kind].append({c: r.get(c, "") for c in cols})
                    continue
                r = {c: "" for c in cols}
                r.update(takim=t, sezon=s)
                if st["durum"] == "tamam":
                    for c in cols[2:-1]:
                        r[c] = st.get(c, "")
                    r["not"] = _join(st.get("not", ""), lg)
                else:
                    r["not"] = _join(lg, st.get("neden", ""))
                    missing.append(f"{kind}\t{t}\t{s}\t{st['durum']}\t{_join(lg, st.get('neden', ''))}")
                rows[kind].append(r)
        pd.DataFrame(rows[kind], columns=cols).to_csv(path, index=False)

    lines = ["# Bulunamayan takım-sezonlar", f"# Oluşturulma: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC",
             "# Sütunlar: tür, takım, sezon, durum (bulunamadi | hata | beklemede), neden", ""]
    (config.DATA / "eksikler.txt").write_text("\n".join(lines + missing) + "\n", encoding="utf-8")
