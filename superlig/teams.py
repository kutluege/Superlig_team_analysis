"""Takım adı standardizasyonu.

Her kulüp için tek bir standart ad tutulur; kaynaklardaki tüm yazımlar
(football-data, Sofascore, Transfermarkt, openfootball, Wikipedia, logo
deposu) normalize edilip bu ada bağlanır. Eşleşmeyen ad uydurulmaz:
loglanır ve raporda listelenir.
"""
from __future__ import annotations

import re
import unicodedata

# standart_ad: (kısa_kod, logo_yolu | None, ana_renk, ikinci_renk, [takma adlar])
# logo_yolu luukhopman/football-logos deposundaki dosya yoludur.
_L = "logos/Türkiye - Süper Lig/"
_H = "history/{s}/Türkiye - Süper Lig/"

CLUBS: dict[str, tuple] = {
    "Adana Demirspor": ("ADS", _H.format(s="2023-24") + "Adana Demirspor.png", "#0A3D91", "#5BC2E7",
                        ["Ad. Demirspor", "Adana Demir"]),
    "Adanaspor": ("ADN", None, "#F37021", "#FFFFFF", []),
    "Akhisarspor": ("AKH", None, "#00843D", "#000000",
                    ["Akhisar Belediyespor", "Akhisar Bld. Spor", "Akhisar Belediye"]),
    "Alanyaspor": ("ALN", _L + "Alanyaspor.png", "#F58220", "#00953A", ["Aytemiz Alanyaspor"]),
    "Altay": ("ALT", _H.format(s="2021-22") + "Altay SK.png", "#000000", "#FFFFFF", ["Altay SK"]),
    "Amedspor": ("AMD", _L + "Amed SK.png", "#00843D", "#E30613", ["Amed SK", "Amed Sportif"]),
    "Ankaragücü": ("ANK", _H.format(s="2023-24") + "MKE Ankaragücü.png", "#00205B", "#FFD200",
                   ["MKE Ankaragücü", "Ankaragucu", "MKE Ankaragucu"]),
    "Antalyaspor": ("ANT", _H.format(s="2024-25") + "Antalyaspor.png", "#E30613", "#FFFFFF",
                    ["Fraport TAV Antalyaspor"]),
    "Beşiktaş": ("BJK", _L + "Besiktas JK.png", "#000000", "#FFFFFF", ["Besiktas", "Beşiktaş JK"]),
    "Bodrum FK": ("BOD", _H.format(s="2024-25") + "Bodrum FK.png", "#00843D", "#FFFFFF",
                  ["Bodrumspor", "Bodrum"]),
    "Bursaspor": ("BUR", None, "#00843D", "#FFFFFF", []),
    "Çaykur Rizespor": ("RIZ", _L + "Caykur Rizespor.png", "#00843D", "#0057B8",
                        ["Rizespor", "Caykur Rizespor"]),
    "Çorum FK": ("COR", _L + "Corum FK.png", "#E30613", "#000000", ["Corum", "Çorum"]),
    "Denizlispor": ("DEN", None, "#00843D", "#000000", ["Yukatel Denizlispor"]),
    "Erzurumspor": ("ERZ", _L + "Erzurumspor FK.png", "#0057B8", "#FFFFFF",
                    ["Erzurum BB", "BB Erzurumspor", "Büyükşehir Belediye Erzurumspor",
                     "Erzurumspor FK", "Erzurum"]),
    "Eyüpspor": ("EYP", _L + "Eyüpspor.png", "#5B2C83", "#FFD200", ["Eyupspor"]),
    "Fatih Karagümrük": ("FKG", _H.format(s="2023-24") + "Fatih Karagümrük.png", "#E30613", "#000000",
                         ["Karagumruk", "Karagümrük", "Fatih Karagumruk", "VavaCars Fatih Karagümrük"]),
    "Fenerbahçe": ("FB", _L + "Fenerbahce.png", "#FFED00", "#002D72",
                   ["Fenerbahce", "Fenerbahçe SK"]),
    "Galatasaray": ("GS", _L + "Galatasaray.png", "#A90432", "#FDB912",
                    ["Galatasaray SK", "Galatasaray A.S."]),
    "Gaziantep FK": ("GFK", _L + "Gaziantep FK.png", "#E30613", "#000000",
                     ["Gaziantep", "Gazişehir Gaziantep", "Gazisehir Gaziantep", "Gaziantep F.K."]),
    "Gaziantepspor": ("GZS", None, "#E30613", "#000000", []),
    "Gençlerbirliği": ("GB", _L + "Genclerbirligi Ankara.png", "#E30613", "#000000",
                       ["Genclerbirligi", "Gençlerbirliği SK", "Genclerbirligi Ankara"]),
    "Giresunspor": ("GIR", _H.format(s="2022-23") + "Giresunspor.png", "#00843D", "#FFFFFF", []),
    "Göztepe": ("GÖZ", _L + "Göztepe.png", "#FFD200", "#E30613", ["Goztep", "Goztepe", "Göztepe SK"]),
    "Hatayspor": ("HAT", _H.format(s="2024-25") + "Hatayspor.png", "#7B1F2E", "#FFFFFF",
                  ["Atakaş Hatayspor"]),
    "İstanbul Başakşehir": ("İBB", _L + "Basaksehir FK.png", "#F36F21", "#0E2C5B",
                            ["Buyuksehyr", "Basaksehir", "Başakşehir", "Başakşehir FK",
                             "İstanbul Başakşehir FK", "Istanbul Basaksehir", "Medipol Başakşehir"]),
    "İstanbulspor": ("İST", _H.format(s="2023-24") + "Istanbulspor.png", "#FFD200", "#000000",
                     ["Istanbulspor", "İstanbulspor AŞ"]),
    "Karabükspor": ("KAR", None, "#0E2C5B", "#E30613",
                    ["Karabukspor", "Kardemir Karabükspor", "Kardemir Karabukspor"]),
    "Kasımpaşa": ("KAS", _L + "Kasimpasa.png", "#0E2C5B", "#FFFFFF",
                  ["Kasimpasa", "Kasımpaşa SK"]),
    "Kayserispor": ("KAY", _H.format(s="2025-26") + "Kayserispor.png", "#E30613", "#FFD200",
                    ["Kayseri", "Hes Kablo Kayserispor"]),
    "Kocaelispor": ("KOC", _L + "Kocaelispor.png", "#00843D", "#000000", []),
    "Konyaspor": ("KON", _L + "Konyaspor.png", "#00843D", "#FFFFFF", ["Atiker Konyaspor"]),
    "Osmanlıspor": ("OSM", None, "#5B2C83", "#FFFFFF",
                    ["Osmanlispor", "Osmanlıspor FK", "Sincan Belediyesi Ankaraspor", "Ankaraspor"]),
    "Pendikspor": ("PEN", _H.format(s="2023-24") + "Pendikspor.png", "#E30613", "#FFFFFF", []),
    "Samsunspor": ("SAM", _L + "Samsunspor.png", "#E30613", "#FFFFFF", []),
    "Sivasspor": ("SİV", _H.format(s="2024-25") + "Sivasspor.png", "#E30613", "#FFFFFF",
                  ["Demir Grup Sivasspor"]),
    "Trabzonspor": ("TS", _L + "Trabzonspor.png", "#7B1F2E", "#5BC2E7", []),
    "Ümraniyespor": ("ÜMR", _H.format(s="2022-23") + "Ümraniyespor.png", "#E30613", "#FFFFFF",
                     ["Umraniyespor"]),
    "Yeni Malatyaspor": ("YMS", _H.format(s="2021-22") + "Y. Malatyaspor.png", "#FFD200", "#000000",
                         ["Y. Malatyaspor", "Malatyaspor", "BtcTurk Yeni Malatyaspor"]),
}

# Genel önek/sonekler normalize edilirken atılır
_NOISE = r"\b(sk|fk|jk|as|a s|spor kulubu|kulubu|futbol|sportif)\b"


def norm(name: str) -> str:
    s = str(name).replace("ı", "i").replace("İ", "I")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(_NOISE, " ", s)
    return re.sub(r"\s+", " ", s).strip()


_LOOKUP: dict[str, str] = {}
for _std, (_code, _logo, _c1, _c2, _aliases) in CLUBS.items():
    for _a in [_std, *_aliases]:
        _LOOKUP[norm(_a)] = _std


def standardize(raw: str) -> str | None:
    """Ham adı standart ada çevirir; tanınmıyorsa None döner."""
    if raw is None:
        return None
    return _LOOKUP.get(norm(raw))


def short_code(std: str) -> str:
    return CLUBS[std][0]


def logo_path(std: str) -> str | None:
    return CLUBS[std][1]


def colors(std: str) -> tuple[str, str]:
    return CLUBS[std][2], CLUBS[std][3]
