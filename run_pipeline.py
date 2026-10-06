"""Süper Lig veri hattı: veri çekme → birleştirme → rapor → görseller.

Kullanım:  python run_pipeline.py            (hepsi)
           python run_pipeline.py --no-viz   (yalnızca veri)
"""
import argparse
import logging
import sys

from superlig import config


def setup_logging():
    config.LOGS.mkdir(exist_ok=True)
    fmt = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt, handlers=[
        logging.FileHandler(config.LOGS / "pipeline.log", mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)])
    for noisy in ("urllib3", "matplotlib", "PIL", "datafc"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-viz", action="store_true")
    args = ap.parse_args()
    setup_logging()

    from superlig import build, report
    res = build.run()
    report.write(res)
    if not args.no_viz:
        from superlig import logos, viz
        from superlig import forma_panel, insta
        logos.ensure_all()
        viz.render_all()
        forma_panel.run()
        insta.render_all()


if __name__ == "__main__":
    main()
