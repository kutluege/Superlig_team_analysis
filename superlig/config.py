"""Proje genel ayarları: sezonlar, kaynak URL'leri, dizinler."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CACHE = ROOT / "cache"
LOGS = ROOT / "logs"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
LOGOS = ROOT / "assets" / "logos"

# Sezon başlangıç yılları: 2016 -> 2016-17 ... 2025 -> 2025-26
SEASON_YEARS = list(range(2016, 2026))


def season_label(year: int) -> str:
    return f"{year}-{str(year + 1)[-2:]}"


SEASONS = [season_label(y) for y in SEASON_YEARS]


def season_of_date(ts) -> int:
    """Maç tarihinden sezon başlangıç yılını bulur.

    Sezonlar normalde Temmuz ortasında ayrılır; 2019-20 sezonu COVID nedeniyle
    26 Temmuz 2020'de bittiği ve 2020-21 Eylül'de başladığı için 2020'de
    sınır 15 Ağustos'tur.
    """
    cutoff_month_day = (8, 15) if ts.year == 2020 else (7, 15)
    return ts.year if (ts.month, ts.day) >= cutoff_month_day else ts.year - 1


# ---- Kaynaklar -------------------------------------------------------------
# 1) football-data.co.uk (birincil)
FOOTBALL_DATA_URL = "https://www.football-data.co.uk/mmz4281/{code}/T1.csv"

# 1b) football-data.co.uk verisinin GitHub aynası (birincil site erişilemezse).
#     Bu depo football-data.co.uk sezon dosyalarını tek dosyada birleştirir.
FD_MIRROR_REPO = "xgabora/Club-Football-Match-Data-2000-2025"
FD_MIRROR_SHA = "25882a58a736daf7ece3781940eac17ae1117a66"
FD_MIRROR_URL = f"https://raw.githubusercontent.com/{FD_MIRROR_REPO}/{FD_MIRROR_SHA}/data/Matches.csv"

# 2) Sofascore (Süper Lig unique-tournament id = 52)
SOFASCORE_TOURNAMENT_ID = 52
SOFASCORE_API = "https://api.sofascore.com/api/v1"

# 2b) Sofascore'dan derlenmiş maç veritabanı (GitHub aynası, Sofascore event id'li)
SS_MIRROR_REPO = "c0ze/super-lig"
SS_MIRROR_SHA = "0550f8713e8fba88eff68025c424b700e7b45dc3"
SS_MIRROR_URL = f"https://raw.githubusercontent.com/{SS_MIRROR_REPO}/{SS_MIRROR_SHA}/data/site.db"
# Aynı depodaki ikinci veritabanı Transfermarkt maç raporlarından derlenmiş
TM_MIRROR_URL = f"https://raw.githubusercontent.com/{SS_MIRROR_REPO}/{SS_MIRROR_SHA}/data/super_lig.db"

# 3) openfootball (bağımsız çapraz kontrol)
OPENFOOTBALL_SHA = "0bf83f88e8feb22904c5f9d93c6407574c1347e0"
OPENFOOTBALL_URL = ("https://raw.githubusercontent.com/openfootball/europe/"
                    f"{OPENFOOTBALL_SHA}/turkey/{{label}}_tr1.txt")

# 4) Wikipedia sezon sayfaları (seyirci / stadyum kapasitesi yedeği)
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/{label}_S%C3%BCper_Lig"

# Amblemler
LOGO_REPO_SHA = "2a3978f0b4730645c205d855a4bda54c161183e9"
LOGO_URL = ("https://raw.githubusercontent.com/luukhopman/football-logos/"
            f"{LOGO_REPO_SHA}/{{path}}")

# İstekler arası minimum bekleme (saniye), host bazında
RATE_LIMITS = {
    "api.sofascore.com": 1.5,
    "www.sofascore.com": 2.5,
    "en.wikipedia.org": 1.5,
    "www.football-data.co.uk": 2.0,
    "default": 1.0,
}
# Bir host'a art arda bu kadar bağlantı hatası alınırsa o host atlanır
HOST_FAILURE_LIMIT = 3
