"""Arşiv kopyalarından fiyat çıkarma.

Bu modül tahmin yapmaz: sayfada okunabilir bir TL tutarı yoksa None döner ve
nedenini not olarak verir.
"""
from __future__ import annotations

import json
import re
import unicodedata

from bs4 import BeautifulSoup

# "1.299,90 TL", "449,99 ₺", "₺499.90", "499 TL", "1 299 TL"
_NUM = r"\d{1,3}(?:[.\s ]\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?"
_TL_AFTER = re.compile(rf"({_NUM})\s*(?:TL|TRY|₺|tl\b)", re.I)
_TL_BEFORE = re.compile(rf"(?:₺|TL|TRY)\s*({_NUM})", re.I)

LIST_HINT = re.compile(r"old|eski|list|regular|strike|before|liste|prev|was|original|del|line-through", re.I)
SALE_HINT = re.compile(r"sale|indirim|discount|special|new|current|final|now|campaign|kampanya", re.I)
JS_HINT = re.compile(r"__NEXT_DATA__|window\.__NUXT__|ng-app|data-reactroot|id=\"app\"|id=\"root\"|"
                     r"<noscript>[^<]*javascript", re.I)


def ascii_lower(s: str) -> str:
    s = s.replace("ı", "i").replace("İ", "i")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def parse_tl(s: str) -> float | None:
    s = s.strip().replace(" ", " ").replace(" ", "")
    if not s:
        return None
    if "." in s and "," in s:            # 1.299,90
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:                        # 449,99 | 1,299
        head, tail = s.rsplit(",", 1)
        s = f"{head}.{tail}" if len(tail) <= 2 else s.replace(",", "")
    elif "." in s:                        # 1.299 | 499.90
        head, tail = s.rsplit(".", 1)
        s = s.replace(".", "") if len(tail) == 3 else s
    try:
        return float(s)
    except ValueError:
        return None


def amounts(text: str) -> list[float]:
    out = []
    for rx in (_TL_AFTER, _TL_BEFORE):
        for m in rx.finditer(text):
            v = parse_tl(m.group(1))
            if v is not None:
                out.append(v)
    return out


def season_tokens(y: int) -> list[str]:
    a, b = str(y), str(y + 1)
    return [f"{a}-{b}", f"{a}/{b}", f"{a}_{b}", f"{a} {b}", f"{a}-{b[2:]}", f"{a}/{b[2:]}",
            f"{a[2:]}-{b[2:]}", f"{a[2:]}/{b[2:]}", f"{a}{b}", f"{a[2:]}{b[2:]}"]


def has_season(text: str, y: int) -> bool:
    t = ascii_lower(text)
    return any(tok in t for tok in season_tokens(y))


def heading(html: str) -> str:
    """Sayfa başlığı + ilk h1 (ürün adı)."""
    soup = BeautifulSoup(html, "lxml")
    parts = [soup.title.get_text(" ") if soup.title else ""]
    h1 = soup.find("h1")
    if h1:
        parts.append(h1.get_text(" "))
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def _jsonld_prices(soup) -> list[float]:
    out = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (ValueError, TypeError):
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            d = stack.pop()
            if isinstance(d, list):
                stack.extend(d)
                continue
            if not isinstance(d, dict):
                continue
            offers = d.get("offers")
            if offers:
                stack.extend(offers if isinstance(offers, list) else [offers])
            if "@graph" in d:
                stack.extend(d["@graph"])
            for k in ("price", "lowPrice", "highPrice"):
                if k in d and str(d.get("priceCurrency", "TRY")).upper() in ("TRY", "TL"):
                    v = parse_tl(str(d[k])) if not isinstance(d[k], (int, float)) else float(d[k])
                    if v:
                        out.append(v)
    return out


def jersey_price(html: str, lo: float = 50, hi: float = 30000) -> tuple[float | None, str]:
    """Ürün sayfasından yetişkin forma fiyatı. (fiyat, not) döner."""
    soup = BeautifulSoup(html, "lxml")
    notes = []

    list_prices, sale_prices, plain = [], [], []
    for el in soup.find_all(True, class_=re.compile(r"price|fiyat", re.I)):
        if el.find(class_=re.compile(r"price|fiyat", re.I)):
            continue  # en içteki öğeyi kullan
        vals = [v for v in amounts(el.get_text(" ")) if lo <= v <= hi]
        if not vals:
            txt = el.get_text(" ").strip()
            v = parse_tl(re.sub(r"[^\d.,]", "", txt)) if re.fullmatch(r"[\d.,\s]+", txt or "x") else None
            vals = [v] if v and lo <= v <= hi else []
        if not vals:
            continue
        cls = " ".join(el.get("class", [])) + " " + (el.get("id") or "")
        struck = el.find_parent(["del", "s", "strike"]) is not None or el.name in ("del", "s", "strike")
        if struck or LIST_HINT.search(cls):
            list_prices += vals
        elif SALE_HINT.search(cls):
            sale_prices += vals
        else:
            plain += vals
    for el in soup.find_all(["del", "s", "strike"]):
        list_prices += [v for v in amounts(el.get_text(" ")) if lo <= v <= hi]

    meta = []
    for sel in [("meta", {"itemprop": "price"}), ("meta", {"property": "product:price:amount"}),
                ("meta", {"property": "og:price:amount"})]:
        for m in soup.find_all(*sel):
            v = parse_tl(m.get("content", ""))
            if v and lo <= v <= hi:
                meta.append(v)
    ld = [v for v in _jsonld_prices(soup) if lo <= v <= hi]

    if list_prices:
        price = max(list_prices)
        cur = sale_prices or plain or meta or ld
        cur = [v for v in cur if v < price]
        if cur:
            notes.append(f"İndirimli fiyat {min(cur):.2f} TL gösteriliyordu; üstü çizili liste fiyatı alındı.")
        else:
            notes.append("Üstü çizili liste fiyatı alındı.")
        return price, " ".join(notes)
    for label, vals in (("yapısal veri (JSON-LD)", ld), ("meta etiketi", meta), ("fiyat alanı", sale_prices + plain)):
        if vals:
            distinct = sorted(set(vals))
            if len(distinct) > 1:
                notes.append(f"Sayfada birden fazla tutar vardı ({', '.join(f'{v:.2f}' for v in distinct[:4])}); "
                             f"{label} değeri alındı.")
            return vals[0], " ".join(notes)
    if JS_HINT.search(html) or len(soup.get_text(" ").strip()) < 300:
        return None, "Fiyat HTML'de yok; sayfa JS ile yükleniyor olabilir."
    return None, "Sayfada fiyat okunamadı."


def kombine_prices(html: str, lo: float = 50, hi: float = 2_000_000) -> tuple[float | None, float | None, str]:
    """Kombine duyuru/bilet sayfasından en ucuz ve en pahalı kategori tutarı."""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "nav", "footer", "header"]):
        t.decompose()
    body = soup.find("article") or soup.find(class_=re.compile(r"content|detail|haber|news|icerik", re.I)) or soup
    text = body.get_text("\n")
    vals = []
    for line in text.splitlines():
        if re.search(r"indirim|%|yüzde|kart ücret|passolig kart", line, re.I):
            continue  # indirim tutarları ve kart ücretleri kategori fiyatı değildir
        vals += [v for v in amounts(line) if lo <= v <= hi]
    imgs = [i for i in body.find_all("img") if re.search(r"kombine|fiyat|price", (i.get("src", "") + i.get("alt", "")), re.I)]
    if not vals:
        if imgs:
            return None, None, "Fiyatlar görsel içinde yayımlanmış; metinden okunamadı."
        if JS_HINT.search(html):
            return None, None, "Fiyat HTML'de yok; sayfa JS ile yükleniyor olabilir."
        return None, None, "Sayfada kombine fiyatı okunamadı."
    note = (f"Sayfadaki {len(vals)} TL tutarından en düşük ve en yüksek alındı (otomatik çıkarım; "
            "kategori adlarıyla eşleştirilmedi).")
    if len(set(vals)) == 1:
        note = "Sayfada tek kombine tutarı vardı."
    return min(vals), max(vals), note
