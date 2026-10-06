"""Önbellekli, hız sınırlı HTTP katmanı.

- Her yanıt `cache/http/` altında saklanır; aynı URL ikinci kez indirilmez.
- Host bazında istekler arası minimum bekleme uygulanır.
- Hatalar loglanır ve `None` döner; çağıran taraf devam eder.
- Bir host'a art arda bağlantı hatası alınırsa (ör. ağ politikası engeli)
  o host için kalan istekler denenmeden atlanır ve bu bir kez loglanır.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests

from . import config

log = logging.getLogger("superlig.net")

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


@dataclass
class SourceAttempt:
    kaynak: str
    url: str
    durum: str          # ok | cache | hata | atlandi
    mesaj: str = ""


@dataclass
class Fetcher:
    cache_dir = config.CACHE / "http"
    attempts: list[SourceAttempt] = field(default_factory=list)
    _last: dict[str, float] = field(default_factory=dict)
    _fails: dict[str, int] = field(default_factory=dict)
    _down: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def _path(self, url: str):
        return self.cache_dir / hashlib.sha1(url.encode()).hexdigest()

    def _wait(self, host: str):
        gap = config.RATE_LIMITS.get(host, config.RATE_LIMITS["default"])
        elapsed = time.monotonic() - self._last.get(host, 0.0)
        if elapsed < gap:
            time.sleep(gap - elapsed)
        self._last[host] = time.monotonic()

    def host_down(self, url: str) -> bool:
        return urlparse(url).netloc in self._down

    def get(self, url: str, kaynak: str, timeout: int = 60,
            headers: dict | None = None) -> bytes | None:
        path = self._path(url)
        if path.exists():
            self.attempts.append(SourceAttempt(kaynak, url, "cache"))
            return path.read_bytes()

        host = urlparse(url).netloc
        if host in self._down:
            self.attempts.append(SourceAttempt(
                kaynak, url, "atlandi", f"{host} erişilemez olarak işaretli"))
            return None

        self._wait(host)
        try:
            r = self.session.get(url, timeout=timeout, headers=headers)
        except requests.RequestException as e:
            self._fails[host] = self._fails.get(host, 0) + 1
            msg = f"{type(e).__name__}: {str(e)[:200]}"
            log.warning("İstek başarısız [%s] %s -> %s", kaynak, url, msg)
            self.attempts.append(SourceAttempt(kaynak, url, "hata", msg))
            if self._fails[host] >= config.HOST_FAILURE_LIMIT:
                self._down.add(host)
                log.error("%s art arda %d kez erişilemedi; bu host için kalan "
                          "istekler atlanacak.", host, self._fails[host])
            return None

        self._fails[host] = 0
        if r.status_code != 200:
            msg = f"HTTP {r.status_code}"
            log.warning("İstek başarısız [%s] %s -> %s", kaynak, url, msg)
            self.attempts.append(SourceAttempt(kaynak, url, "hata", msg))
            return None

        path.write_bytes(r.content)
        self.attempts.append(SourceAttempt(kaynak, url, "ok"))
        return r.content

    def get_json(self, url: str, kaynak: str, **kw):
        raw = self.get(url, kaynak, **kw)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except ValueError as e:
            log.warning("JSON çözümlenemedi [%s] %s: %s", kaynak, url, e)
            return None

    def note(self, kaynak: str, url: str, durum: str, mesaj: str = ""):
        """Kütüphane (ör. datafc) üzerinden yapılan denemeleri kayda geçirir."""
        self.attempts.append(SourceAttempt(kaynak, url, durum, mesaj))
