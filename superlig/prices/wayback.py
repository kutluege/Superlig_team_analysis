"""Wayback Machine CDX ve kopya istemcisi.

- Her istek öncesi 1-2 sn rastgele bekleme.
- Başarılı yanıtlar `cache/wayback/` altında saklanır; script yeniden
  çalıştırıldığında aynı istek tekrar yapılmaz.
- 429/5xx ve zaman aşımında artan beklemeyle en fazla 3 deneme.
- Bağlantı düzeyinde art arda 3 hata alınırsa (ör. ağ politikası engeli)
  `WaybackUnavailable` fırlatılır; çağıran taraf kalan işleri "hata" olarak
  işaretleyip sonraki çalıştırmaya bırakır.
"""
from __future__ import annotations

import hashlib
import json
import logging
import random
import time
from dataclasses import dataclass
from urllib.parse import urlencode

import requests

from .. import config

log = logging.getLogger("superlig.wayback")

CDX = "https://web.archive.org/cdx/search/cdx"
SNAP = "https://web.archive.org/web/{ts}/{url}"          # kaynak_url olarak yazılan adres
RAW = "https://web.archive.org/web/{ts}id_/{url}"        # Wayback araç çubuğu olmadan ham sayfa
UA = "superlig-analysis/1.0 (research; contact via repository)"


class WaybackUnavailable(RuntimeError):
    pass


@dataclass
class Capture:
    timestamp: str
    original: str
    statuscode: str
    mimetype: str

    @property
    def url(self) -> str:
        return SNAP.format(ts=self.timestamp, url=self.original)

    @property
    def raw_url(self) -> str:
        return RAW.format(ts=self.timestamp, url=self.original)

    @property
    def date(self) -> str:
        t = self.timestamp
        return f"{t[:4]}-{t[4:6]}-{t[6:8]}"


class Wayback:
    def __init__(self, min_wait: float = 1.0, max_wait: float = 2.0):
        self.cache = config.CACHE / "wayback"
        self.cache.mkdir(parents=True, exist_ok=True)
        self.s = requests.Session()
        self.s.headers["User-Agent"] = UA
        self.min_wait, self.max_wait = min_wait, max_wait
        self.conn_fail = 0
        self.requests = 0

    def _path(self, url):
        return self.cache / hashlib.sha1(url.encode()).hexdigest()

    def _get(self, url: str, timeout: int = 60) -> bytes | None:
        p = self._path(url)
        if p.exists():
            return p.read_bytes()
        for attempt in range(3):
            time.sleep(random.uniform(self.min_wait, self.max_wait))
            self.requests += 1
            try:
                r = self.s.get(url, timeout=timeout)
            except (requests.ConnectionError, requests.exceptions.ProxyError) as e:
                self.conn_fail += 1
                log.warning("Bağlantı hatası (%d): %s -> %s", self.conn_fail, url, str(e)[:160])
                if self.conn_fail >= 3:
                    blocked = "403" in str(e) or "Tunnel" in str(e) or "ProxyError" in type(e).__name__
                    raise WaybackUnavailable(
                        "web.archive.org'a bağlanılamadı (ağ politikası engeli, proxy CONNECT 403); denenemedi."
                        if blocked else f"web.archive.org'a bağlanılamadı ({type(e).__name__}); denenemedi.")
                continue
            except requests.Timeout:
                log.warning("Zaman aşımı: %s (deneme %d)", url, attempt + 1)
                time.sleep(5 * 2 ** attempt)
                continue
            self.conn_fail = 0
            if r.status_code == 200:
                p.write_bytes(r.content)
                return r.content
            if r.status_code in (429, 500, 502, 503, 504):
                wait = 10 * 2 ** attempt
                log.warning("HTTP %s, %ds bekleniyor: %s", r.status_code, wait, url)
                time.sleep(wait)
                continue
            log.warning("HTTP %s: %s", r.status_code, url)
            return None
        log.error("3 denemede alınamadı: %s", url)
        return None

    def cdx(self, url: str, start: str, end: str, match: str = "domain",
            url_regex: str | None = None, collapse: str | None = "urlkey", limit: int = 20000) -> list[Capture]:
        params = [("url", url), ("matchType", match), ("from", start), ("to", end),
                  ("output", "json"), ("fl", "timestamp,original,statuscode,mimetype"),
                  ("filter", "statuscode:200"), ("filter", "mimetype:text/html"), ("limit", str(limit))]
        if url_regex:
            params.append(("filter", f"original:{url_regex}"))
        if collapse:
            params.append(("collapse", collapse))
        q = f"{CDX}?{urlencode(params)}"
        raw = self._get(q, timeout=120)
        if not raw:
            return []
        try:
            rows = json.loads(raw)
        except ValueError:
            log.warning("CDX yanıtı JSON değil: %s", q)
            return []
        if not rows:
            return []
        head, body = rows[0], rows[1:]
        caps = [Capture(**dict(zip(head, r))) for r in body]
        return sorted(caps, key=lambda c: c.timestamp)

    def earliest(self, original: str, start: str, end: str) -> Capture | None:
        caps = self.cdx(original, start, end, match="exact", collapse=None, limit=50)
        return caps[0] if caps else None

    def fetch(self, cap: Capture) -> str | None:
        raw = self._get(cap.raw_url)
        if raw is None:
            return None
        for enc in ("utf-8", "windows-1254", "iso-8859-9"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", "replace")
