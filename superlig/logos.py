"""Kulüp amblemleri.

Amblemler luukhopman/football-logos deposundan indirilir. Depoda amblemi
olmayan (2021 öncesi ligden düşmüş) kulüpler için kulüp renklerinde, kısa
kodlu bir yer tutucu rozet üretilir; bu rozetler gerçek amblem değildir ve
`assets/logos/KAYNAK.csv` dosyasında "yer_tutucu" olarak işaretlenir.
"""
from __future__ import annotations

import io
import logging
from urllib.parse import quote

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from . import config, teams
from .net import Fetcher

log = logging.getLogger("superlig.logos")
SIZE = 256


def file_for(std: str):
    return config.LOGOS / f"{teams.norm(teams.short_code(std)).upper()}.png"


def _square(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    box = SIZE - 16  # küçük kaynak görselleri de aynı kutuya büyüt (görsel boyut eşitliği)
    scale = box / max(img.width, img.height)
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas.paste(img, ((SIZE - img.width) // 2, (SIZE - img.height) // 2), img)
    return canvas


def _font(size):
    for f in ["DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def placeholder(std: str) -> Image.Image:
    c1, c2 = teams.colors(std)
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 20
    # kalkan biçimi: üstte dikdörtgen, altta sivri uç
    w, h = SIZE - 2 * pad, SIZE - 2 * pad
    shield = [(pad, pad), (pad + w, pad), (pad + w, pad + h * 0.55),
              (SIZE / 2, pad + h), (pad, pad + h * 0.55)]
    d.polygon(shield, fill=c1, outline=c2, width=10)
    code = teams.short_code(std)
    font = _font(78 if len(code) <= 3 else 64)
    rgb = Image.new("RGB", (1, 1), c1).getpixel((0, 0))
    ink = "#FFFFFF" if (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) < 150 else "#111111"
    d.text((SIZE / 2, SIZE * 0.44), code, font=font, fill=ink, anchor="mm")
    return img


def ensure_all(fetcher: Fetcher | None = None) -> pd.DataFrame:
    fetcher = fetcher or Fetcher()
    config.LOGOS.mkdir(parents=True, exist_ok=True)
    rows = []
    for std in teams.CLUBS:
        out = file_for(std)
        rel = teams.logo_path(std)
        kind = "amblem"
        if not out.exists():
            img = None
            if rel:
                raw = fetcher.get(config.LOGO_URL.format(path=quote(rel)), "logo")
                if raw:
                    try:
                        img = _square(Image.open(io.BytesIO(raw)))
                    except Exception as e:
                        log.warning("Amblem okunamadı %s: %s", std, e)
            if img is None:
                img = placeholder(std)
                kind = "yer_tutucu"
                log.info("%s için amblem bulunamadı; yer tutucu rozet üretildi", std)
            img.save(out, optimize=True)
        elif not rel:
            kind = "yer_tutucu"
        rows.append({"takim": std, "dosya": out.name, "tur": kind,
                     "kaynak": f"luukhopman/football-logos/{rel}" if kind == "amblem" else "üretilmiş rozet"})
    df = pd.DataFrame(rows)
    df.to_csv(config.LOGOS / "KAYNAK.csv", index=False)
    return df
