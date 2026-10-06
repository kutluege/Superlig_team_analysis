"""Forma ve kombine fiyatlarını Wayback Machine'den toplar (yeniden çalıştırılabilir).

Kullanım:
  python collect_prices.py                      # tümü; kaldığı yerden devam eder
  python collect_prices.py --kind forma         # yalnızca forma
  python collect_prices.py --team Galatasaray --season 2019-20
  python collect_prices.py --retry-missing      # 'bulunamadi' olanları da yeniden dene

Girdi : data/sources.csv (takim,alan_adi,tur), data/team_season.csv
Çıktı : data/forma.csv, data/kombine.csv, data/eksikler.txt, data/fiyat_durum.json
Log   : logs/fiyat.log
"""
import argparse
import logging
import sys

from superlig import config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["forma", "kombine"], action="append")
    ap.add_argument("--team", action="append")
    ap.add_argument("--season", action="append")
    ap.add_argument("--retry-missing", action="store_true")
    a = ap.parse_args()

    config.LOGS.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
                        handlers=[logging.FileHandler(config.LOGS / "fiyat.log", encoding="utf-8"),
                                  logging.StreamHandler(sys.stdout)])
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    from superlig.prices.collect import Collector
    c = Collector(retry_missing=a.retry_missing)
    unavailable = c.run(kinds=tuple(a.kind or ("forma", "kombine")), teams=a.team, seasons=a.season)
    if unavailable:
        print(f"\nWayback Machine'e erişilemedi: {unavailable}\n"
              "İlerleme kaydedildi; erişim sağlandığında komutu yeniden çalıştırın.")
        sys.exit(2)


if __name__ == "__main__":
    main()
