"""Fiyat çıkarma ve toplama mantığı testleri (ağ gerektirmez)."""
import json

import pandas as pd
import pytest

from superlig import config
from superlig.prices import collect, extract
from superlig.prices.wayback import Capture, WaybackUnavailable


# ------------------------------------------------------------------ extract
@pytest.mark.parametrize("s,v", [("1.299,90", 1299.90), ("449,99", 449.99), ("499.90", 499.90),
                                 ("1.299", 1299.0), ("1 299", 1299.0), ("4500", 4500.0), ("1,299", 1299.0)])
def test_parse_tl(s, v):
    assert extract.parse_tl(s) == pytest.approx(v)


def test_season_tokens():
    assert extract.has_season("galatasaray-2017-2018-ic-saha-formasi", 2017)
    assert extract.has_season("Fenerbahçe 17/18 Çubuklu Forma", 2017)
    assert not extract.has_season("galatasaray-2018-2019-ic-saha-formasi", 2017)


def test_jersey_list_price_when_discounted():
    html = """<html><h1>2019-2020 İç Saha Forması</h1>
      <div class="product-price"><span class="old-price">399,90 TL</span>
      <span class="sale-price">299,90 TL</span></div></html>"""
    price, note = extract.jersey_price(html)
    assert price == pytest.approx(399.90)
    assert "İndirimli" in note and "299.90" in note


def test_jersey_del_tag_and_jsonld():
    html = """<html><script type="application/ld+json">
      {"@type":"Product","offers":{"@type":"Offer","price":"3499.00","priceCurrency":"TRY"}}</script>
      <p>Fiyat: <del>3.999,00 TL</del></p></html>"""
    price, note = extract.jersey_price(html)
    assert price == pytest.approx(3999.0)


def test_jersey_jsonld_only():
    html = """<html><script type="application/ld+json">
      [{"@type":"Product","offers":{"price":2299.9,"priceCurrency":"TRY"}}]</script><p>x</p></html>"""
    assert extract.jersey_price(html)[0] == pytest.approx(2299.9)


def test_jersey_js_page_returns_none():
    html = '<html><body><div id="root"></div><script>window.__NUXT__={}</script></body></html>'
    price, note = extract.jersey_price(html)
    assert price is None and "JS" in note


def test_kombine_min_max_ignores_discounts():
    html = """<html><article><h1>2018-2019 Sezonu Kombine Fiyatları</h1>
      <p>Maraton Üst: 750 TL</p><p>Kapalı Tribün: 2.500 TL</p><p>VIP: 12.000 TL</p>
      <p>Öğrencilere 100 TL indirim</p><p>Passolig kart ücreti 35 TL</p></article></html>"""
    lo, hi, note = extract.kombine_prices(html)
    assert (lo, hi) == (750, 12000)


def test_kombine_image_only():
    html = '<html><article><h1>Kombine</h1><img src="/img/kombine-fiyatlari.jpg"></article></html>'
    lo, hi, note = extract.kombine_prices(html)
    assert lo is None and "görsel" in note


# ------------------------------------------------------------------ collect
class FakeWayback:
    """CDX ve kopya yanıtlarını bellekten veren sahte istemci."""

    def __init__(self, caps, pages, fail=False):
        self.caps, self.pages, self.fail, self.fetched = caps, pages, fail, []

    def cdx(self, url, start, end, **kw):
        if self.fail:
            raise WaybackUnavailable("web.archive.org erişilemiyor: test")
        return [c for c in self.caps.get(url, []) if start <= c.timestamp[:8] <= end]

    def earliest(self, original, start, end):
        allc = [c for cs in self.caps.values() for c in cs if c.original == original
                and start <= c.timestamp[:8] <= end]
        return min(allc, key=lambda c: c.timestamp) if allc else None

    def fetch(self, cap):
        self.fetched.append(cap.timestamp)
        return self.pages.get(cap.timestamp)


def cap(ts, url):
    return Capture(ts, url, "200", "text/html")


@pytest.fixture
def tmpdata(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA", tmp_path)
    pd.DataFrame([{"takim": "Galatasaray", "alan_adi": "gsstore.org", "tur": "magaza"},
                  {"takim": "Galatasaray", "alan_adi": "galatasaray.org", "tur": "resmi_site"}]
                 ).to_csv(tmp_path / "sources.csv", index=False)
    pd.DataFrame([{"takim": "Galatasaray", "sezon": s, "ligde": True} for s in config.SEASONS]
                 + [{"takim": "Gençlerbirliği", "sezon": "2018-19", "ligde": False}]
                 ).to_csv(tmp_path / "team_season.csv", index=False)
    return tmp_path


def make_collector(fake):
    c = collect.Collector()
    c.wb = fake
    return c


def test_earliest_capture_in_window_and_adult_home(tmpdata):
    u = "https://www.gsstore.org/galatasaray-2017-2018-ic-saha-formasi-p-123"
    kid = "https://www.gsstore.org/galatasaray-2017-2018-cocuk-ic-saha-formasi-p-124"
    caps = {"gsstore.org": [cap("20170410000000", u), cap("20170615000000", u), cap("20170801000000", u),
                            cap("20170601000000", kid)]}
    pages = {"20170615000000": "<h1>2017-2018 İç Saha Forması</h1><span class='price'>249,90 TL</span>",
             "20170801000000": "<h1>2017-2018 İç Saha Forması</h1><span class='price'>199,90 TL</span>",
             "20170601000000": "<h1>Çocuk</h1><span class='price'>149,90 TL</span>"}
    fake = FakeWayback(caps, pages)
    res = make_collector(fake).forma("Galatasaray", "2017-18")
    assert res["durum"] == "tamam"
    assert res["fiyat_TL"] == pytest.approx(249.90)       # Nisan kopyası pencere dışında; Haziran en erken
    assert res["snapshot_tarihi"] == "2017-06-15"
    assert res["kaynak_url"] == f"https://web.archive.org/web/20170615000000/{u}"


def test_other_season_product_rejected(tmpdata):
    u = "https://www.gsstore.org/galatasaray-2016-2017-ic-saha-formasi"
    fake = FakeWayback({"gsstore.org": [cap("20170601000000", u)]},
                       {"20170601000000": "<h1>2016-2017 İç Saha</h1><span class='price'>199 TL</span>"})
    res = make_collector(fake).forma("Galatasaray", "2017-18")
    assert res["durum"] == "bulunamadi"


def test_resume_protect_and_outputs(tmpdata):
    # mevcut forma.csv'de dolu satır: dokunulmamalı
    pd.DataFrame([{"takim": "Galatasaray", "sezon": "2016-17", "fiyat_TL": "179.90",
                   "kaynak_url": "https://web.archive.org/web/2016/x", "snapshot_tarihi": "2016-06-01",
                   "not": "elle girildi"}]).to_csv(tmpdata / "forma.csv", index=False)
    fake = FakeWayback({}, {}, fail=True)
    c = make_collector(fake)
    unavailable = c.run(kinds=("forma",), teams=["Galatasaray"], seasons=["2016-17", "2017-18"])
    assert unavailable
    out = pd.read_csv(tmpdata / "forma.csv", dtype=str)
    row = out[(out.takim == "Galatasaray") & (out.sezon == "2016-17")].iloc[0]
    assert row.fiyat_TL == "179.90" and row["not"] == "elle girildi"
    st = json.loads((tmpdata / "fiyat_durum.json").read_text())
    assert st["forma|Galatasaray|2017-18"]["durum"] == "hata"
    assert "2017-18" in (tmpdata / "eksikler.txt").read_text()

    # ikinci çalıştırma: erişim var, hata alan iş yeniden denenir ve tamamlanır
    u = "https://www.gsstore.org/2017-2018-ic-saha-forma"
    fake2 = FakeWayback({"gsstore.org": [cap("20170701000000", u)]},
                        {"20170701000000": "<h1>2017-2018 İç Saha Forma</h1><span class='price'>229,90 TL</span>"})
    c2 = make_collector(fake2)
    assert c2.run(kinds=("forma",), teams=["Galatasaray"], seasons=["2016-17", "2017-18"]) is None
    out = pd.read_csv(tmpdata / "forma.csv", dtype=str)
    assert out[out.sezon == "2017-18"].fiyat_TL.iloc[0] == "229.9"
    assert out[out.sezon == "2016-17"].fiyat_TL.iloc[0] == "179.90"

    # üçüncü çalıştırma: tamamlanan iş için istek yapılmaz
    fake3 = FakeWayback({}, {}, fail=True)
    c3 = make_collector(fake3)
    assert c3.run(kinds=("forma",), teams=["Galatasaray"], seasons=["2016-17", "2017-18"]) is None
    assert fake3.fetched == []


def test_league_note(tmpdata):
    ts = pd.read_csv(tmpdata / "team_season.csv")
    assert "Süper Lig'de değil" in collect.league_note("Gençlerbirliği", "2018-19", ts)
