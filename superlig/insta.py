"""Instagram görselleri (1080×1350, 4:5): kapak, takım kartları (altıgen radar), metrik sıralamaları."""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyBboxPatch, Polygon
from PIL import Image

from . import config, logos, scorecard, teams

log = logging.getLogger("superlig.insta")
OUT = config.REPORTS / "instagram"
FONTS = config.ROOT / "assets" / "fonts"
for f in FONTS.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
COND, BODY = "Barlow Condensed", "Barlow"

BG = "#0e1311"
PANEL = "#171d1a"
LINE = "#2a322e"
INK = "#f3f5f2"
INK2 = "#b9c0ba"
MUTED = "#7d867f"
GOLD = "#f2c14e"
W, H, DPI = 7.2, 9.0, 150  # 1080×1350 px

HANDLE = "Süper Lig 2016–2026 · 10 sezon analizi"
SOURCE = "Veri: football-data.co.uk · Sofascore · Wikipedia · Transfermarkt · TFF · kulüp hesapları"


def _tr(x, dec=0):
    if x is None or pd.isna(x):
        return "—"
    s = f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def _compact(n):
    if n is None or pd.isna(n):
        return "—"
    if n >= 1e6:
        return _tr(n / 1e6, 1) + " Mn"
    if n >= 1e3:
        return _tr(n / 1e3, 0) + " B"
    return _tr(n)


def _lum(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b


def accent(team):
    c1, c2 = teams.colors(team)
    for c in (c1, c2):
        if 0.25 < _lum(c) < 0.95:
            return c
    return "#e8ece9"


def _logo(team, px):
    im = Image.open(logos.file_for(team)).convert("RGBA").resize((px, px), Image.LANCZOS)
    return np.asarray(im)


def _place_logo(fig, team, x, y, px):
    ab = AnnotationBbox(OffsetImage(_logo(team, px * 2), zoom=0.5 * 72 / DPI), (x, y),  # px = çıktı pikseli
                        xycoords="figure fraction", frameon=False)
    fig.add_artist(ab)


def _fig():
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.patch.set_facecolor(BG)
    return fig


def _text(fig, x, y, s, size, color=INK, font=BODY, weight="regular", ha="left", va="baseline", **kw):
    return fig.text(x, y, s, fontsize=size, color=color, family=font, weight=weight, ha=ha, va=va, **kw)


def _footer(fig, page=None):
    fig.add_artist(plt.Line2D([0.06, 0.94], [0.052, 0.052], color=LINE, lw=0.8))
    _text(fig, 0.06, 0.028, SOURCE, 6.6, MUTED)
    if page:
        _text(fig, 0.94, 0.028, page, 6.6, MUTED, ha="right")


# ------------------------------------------------------------------ radar
def _hex_points(r, n=6, rot=90):
    ang = np.deg2rad(rot - np.arange(n) * 360 / n)
    return np.c_[np.cos(ang) * r, np.sin(ang) * r]


def radar(ax, scores, color, avg=None, labels=None, label_vals=None, lw=2.4, label_size=11, show_rings=True):
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.32, 1.32)
    ax.set_aspect("equal")
    ax.axis("off")
    if show_rings:
        for r in (0.25, 0.5, 0.75, 1.0):
            ax.add_patch(Polygon(_hex_points(r), closed=True, fill=r == 1.0, facecolor=PANEL if r == 1 else "none",
                                 edgecolor=LINE, lw=0.9 if r < 1 else 1.3, zorder=0 if r == 1 else 1))
        for x, y in _hex_points(1.0):
            ax.plot([0, x], [0, y], color=LINE, lw=0.8, zorder=1)
    if avg is not None:
        pa = _hex_points(1)[:, :] * np.nan_to_num(np.asarray(avg) / 100)[:, None]
        ax.add_patch(Polygon(pa, closed=True, fill=False, edgecolor=MUTED, lw=1.1, ls=(0, (3, 2.5)), zorder=2))
    s = np.nan_to_num(np.asarray(scores, float) / 100)
    s = np.maximum(s, 0.03)
    p = _hex_points(1) * s[:, None]
    ax.add_patch(Polygon(p, closed=True, facecolor=color, alpha=0.32, edgecolor="none", zorder=3))
    ax.add_patch(Polygon(p, closed=True, fill=False, edgecolor=color, lw=lw, joinstyle="round", zorder=4))
    for (x, y), v in zip(p, scores):
        ax.scatter([x], [y], s=26 if lw > 2 else 8, color=color if not pd.isna(v) else MUTED,
                   edgecolor=BG, linewidth=1.4, zorder=5)
    if labels:
        for (x, y), lab, v in zip(_hex_points(1.2), labels, label_vals or [None] * 6):
            if y < -1:  # alt etiket köşeye değmesin
                y -= 0.12 if v is None else 0.0
            ha = "center" if abs(x) < 0.1 else ("left" if x > 0 else "right")
            ax.text(x, y + 0.02, lab.upper(), ha=ha, va="bottom", fontsize=label_size * 0.72, color=INK2,
                    family=COND, weight="semibold")
            if v is not None:
                miss = v == "veri yok"
                ax.text(x, y - 0.02, v, ha=ha, va="top", fontsize=label_size * (0.8 if miss else 1.25),
                        color=MUTED if miss else INK, family=COND, weight="semibold" if miss else "bold")


def _forma_sub(row):
    if pd.isna(row.get("forma_maliyet_10y_TL")):
        return "fiyat verisi bulunamadı"
    return f"10 forma, bugünkü TL · lig ort. ×{_tr(row.forma_lig_orani, 2)} · {int(row.forma_gercek_sezon)}/10 gerçek"


def _pct(x):
    if x is None or pd.isna(x):
        return "—"
    return ("+%" if x >= 0 else "−%") + _tr(abs(x))


# ------------------------------------------------------------------ takım kartı
def team_card(row, avg, rank, n, path):
    team = row.takim
    col = accent(team)
    fig = _fig()
    # üst şerit: kulüp rengi
    fig.add_artist(plt.Rectangle((0, 0.985), 1, 0.015, transform=fig.transFigure, color=col))
    _place_logo(fig, team, 0.115, 0.9, 110)
    _text(fig, 0.2, 0.912, team.upper(), 30, INK, COND, "bold", va="center")
    _text(fig, 0.2, 0.872, "SÜPER LİG 2016–2026 KARNESİ", 9.5, INK2, COND, "semibold", va="center")
    overall = row.genel_skor
    _text(fig, 0.94, 0.918, _tr(overall), 34, col, COND, "bold", ha="right", va="center")
    _text(fig, 0.94, 0.872, f"GENEL SKOR · {rank}/{n}", 8.5, INK2, COND, "semibold", ha="right", va="center")

    ax = fig.add_axes([0.04, 0.375, 0.92, 0.47])
    scores = [row[f"skor_{k}"] for k, _ in scorecard.AXES]
    vals = ["veri yok" if pd.isna(v) else _tr(v) for v in scores]
    radar(ax, scores, col, avg=avg, labels=[l for _, l in scorecard.AXES], label_vals=vals)
    fig.add_artist(plt.Line2D([0.235, 0.275], [0.338, 0.338], color=MUTED, lw=1.1, ls=(0, (3, 2.5))))
    _text(fig, 0.285, 0.338, "lig ortalaması  ·  eksenler gerçek yüzde  ·  genel skor: 6 eksen eşit etkili, lig ort. = 50", 7.2, MUTED,
          va="center")

    g = row.get
    tiles = [
        ("SADAKAT", f"%{_tr(g('doluluk_yuzde'))} doluluk" if pd.notna(g("doluluk_yuzde")) else "—",
         f"sosyal medya %{_tr(g('sosyal_yuzde'))} · {_compact(g('takipci_toplam'))} takipçi"),
        ("BAŞARI", f"{_tr(g('kupa_10y'))} / 30 kupa",
         f"Lig {_tr(g('super_lig'))} · Türkiye K. {_tr(g('turkiye_kupasi'))} · Süper K. {_tr(g('super_kupa'))}"),
        ("GOL + xG", f"{_tr(row.gol_10y)} gol",
         f"gol payı %{_tr(g('gol_payi'))}" + (f" · xG payı %{_tr(g('xg_payi'))} (22-26)" if pd.notna(g("xg_payi")) else "")),
        ("GALİBİYET", f"%{_tr(g('galibiyet_yuzde'))}", f"{_tr(row.galibiyet_10y)} galibiyet / {_tr(row.mac)} maç"),
        ("TARAFTARA MALİYET", (_tr(g("forma_maliyet_10y_reel_TL")) + " TL") if pd.notna(g("forma_maliyet_10y_reel_TL")) else "—",
         _forma_sub(row)),
        ("SON 3 SEZON", f"%{_tr(g('son3_puan_yuzde'))} puan" if pd.notna(g("son3_puan_yuzde")) else "ligde değil",
         (f"{_tr(row.son3_puan_ort, 1)} puan/sezon · ort. sıra {_tr(row.son3_sira_ort, 1)}" if pd.notna(row.son3_sezon) else "son 3 sezonda Süper Lig'de yok")),
    ]
    x0, y0, tw, th, gx, gy = 0.06, 0.075, 0.28, 0.115, 0.02, 0.018
    for i, (lab, big, small) in enumerate(tiles):
        r, c = divmod(i, 3)
        x, y = x0 + c * (tw + gx), y0 + (1 - r) * (th + gy)
        fig.add_artist(FancyBboxPatch((x, y), tw, th, boxstyle="round,pad=0,rounding_size=0.012",
                                      transform=fig.transFigure, facecolor=PANEL, edgecolor=LINE, lw=0.8))
        _text(fig, x + 0.02, y + th - 0.026, lab, 8, INK2, COND, "semibold")
        _text(fig, x + 0.02, y + 0.042, big, 19 if len(big) < 10 else 15, INK, COND, "bold")
        _text(fig, x + 0.02, y + 0.016, small, 6.4, MUTED)
    _footer(fig, HANDLE)
    fig.savefig(path, dpi=DPI, facecolor=BG)
    plt.close(fig)


# ------------------------------------------------------------------ kapak
def cover(df, avg, path):
    fig = _fig()
    _text(fig, 0.06, 0.93, "SÜPER LİG'İN", 15, GOLD, COND, "bold")
    _text(fig, 0.06, 0.865, "ALTI YÜZÜ", 44, INK, COND, "bold")
    _text(fig, 0.06, 0.835, "19 kulüp · 10 sezon · 6 boyut: sadakat, başarı, gol+xG, galibiyet, taraftara maliyet, son 3 sezon",
          8.4, INK2)
    cols, rows = 4, 5
    gx0, gy0, cw, ch = 0.04, 0.07, 0.23, 0.148
    for i, r in enumerate(df.itertuples()):
        c, rr = i % cols, i // cols
        x, y = gx0 + c * cw, gy0 + (rows - 1 - rr) * ch
        ax = fig.add_axes([x, y + 0.012, cw, ch - 0.02])
        radar(ax, [getattr(r, f"skor_{k}") for k, _ in scorecard.AXES], accent(r.takim), avg=None, lw=1.4)
        _place_logo(fig, r.takim, x + 0.035, y + 0.009, 24)
        _text(fig, x + 0.06, y + 0.009, f"{i + 1}. {r.takim}", 7, INK2, COND, "semibold", va="center")
    # son hücre: eksen açıklaması
    x, y = gx0 + 3 * cw, gy0
    ax = fig.add_axes([x, y + 0.012, cw, ch - 0.02])
    radar(ax, [100] * 6, MUTED, lw=0.8, labels=["Sadakat", "Başarı", "Gol+xG", "Galibiyet", "Maliyet (ucuz)", "Son 3"],
          label_size=7.5)
    _footer(fig, "Sıralama: genel skor · 6 eksen eşit etkili · lig ortalaması = 50")
    fig.savefig(path, dpi=DPI, facecolor=BG)
    plt.close(fig)


# ------------------------------------------------------------------ metrik sıralaması
METRIC_SLIDES = [
    ("sadakat", "SADAKAT", "ortalama(10 yıllık doluluk %, sosyal medya %) · sosyal: 1 bin takipçi = %0, 100 Mn = %100 (log)",
     "skor_sadakat",
     lambda r: f"%{_tr(r.skor_sadakat)} · doluluk %{_tr(r.get('doluluk_yuzde'))} · sosyal %{_tr(r.get('sosyal_yuzde'))}"),
    ("basari", "BAŞARI", "10 yılda dağıtılan 30 kupadan alınan pay (Süper Lig + Türkiye Kupası + Süper Kupa)",
     "skor_basari", lambda r: f"%{_tr(r.skor_basari)} · {_tr(r.kupa_10y)} kupa"),
    ("gol", "GOL + xG", "ortalama(gol payı: atılan ÷ atılan+yenilen [10 yıl], xG payı [2022-26])", "skor_gol",
     lambda r: f"%{_tr(r.skor_gol)} · {_tr(r.gol_10y)} gol" + (f" · xG payı %{_tr(r.get('xg_payi'))}" if pd.notna(r.get('xg_payi')) else "")),
    ("galibiyet", "GALİBİYET", "10 yılda galibiyet yüzdesi (Süper Lig maçları)", "skor_galibiyet",
     lambda r: f"%{_tr(r.skor_galibiyet)} · {_tr(r.galibiyet_10y)}/{_tr(r.mac)}"),
    ("forma", "TARAFTARA MALİYET", "10 sezonun ev formalarının toplam maliyeti, bugünkü TL (TÜFE) · ucuzdan pahalıya",
     "skor_forma",
     lambda r: f"{_tr(r.forma_maliyet_10y_reel_TL)} TL · nominal {_tr(r.forma_maliyet_10y_TL)} · uygunluk %{_tr(r.skor_forma)}"),
    ("form", "SON 3 SEZON", "2023-24 – 2025-26: alınan puan ÷ alınabilecek puan (TFF puan silmeleri dahil)", "skor_form",
     lambda r: f"%{_tr(r.skor_form)} · {_tr(r.son3_puan_ort, 1)} p/sezon · ort. sıra {_tr(r.son3_sira_ort, 1)}"
     if pd.notna(r.son3_sezon) else "ligde değil"),
]


def metric_slide(df, key, title, subtitle, col, fmt, path, page, weak=None, weak_label=None):
    if col not in df or df[col].notna().sum() == 0:
        return False
    d = df.dropna(subset=[col]).sort_values(col, ascending=False).reset_index(drop=True)
    missing = [t for t in df.takim if t not in set(d.takim)]
    fig = _fig()
    _text(fig, 0.06, 0.925, title, 34, INK, COND, "bold")
    _text(fig, 0.06, 0.893, subtitle, 9, INK2)
    n = len(d)
    top, bottom = 0.86, 0.105 if (missing or weak_label) else 0.075
    rowh = (top - bottom) / max(n, 1)
    vmax = 100.0  # tüm skorlar gerçek yüzde
    for i, r in d.iterrows():
        y = top - (i + 0.5) * rowh
        _text(fig, 0.075, y, str(i + 1), 13, GOLD if i < 3 else MUTED, COND, "bold", ha="right", va="center")
        _place_logo(fig, r.takim, 0.115, y, 34)
        _text(fig, 0.15, y, r.takim, 12, INK, COND, "semibold", va="center")
        x0, wmax = 0.42, 0.25
        w = wmax * (r[col] / vmax if vmax else 0)
        low = bool(weak(r)) if weak else False
        fig.add_artist(FancyBboxPatch((x0, y - rowh * 0.24), max(w, 0.004), rowh * 0.48,
                                      boxstyle="round,pad=0,rounding_size=0.004", transform=fig.transFigure,
                                      facecolor=GOLD if i < 3 else "#dfe5e1", alpha=0.35 if low else 1,
                                      edgecolor="none"))
        _text(fig, x0 + w + 0.012, y, fmt(r), 8.8, MUTED if low else INK2, va="center")
    notes = []
    if weak_label:
        notes.append(weak_label)
    if missing:
        notes.append("Veri yok: " + ", ".join(missing))
    for j, t in enumerate(notes):
        _text(fig, 0.06, 0.08 - j * 0.017, t, 7.2, MUTED)
    _footer(fig, page)
    fig.savefig(path, dpi=DPI, facecolor=BG)
    plt.close(fig)
    return True


def overall_slide(df, path):
    d = df.sort_values("genel_skor", ascending=False).reset_index(drop=True)
    fig = _fig()
    _text(fig, 0.06, 0.925, "GENEL SIRALAMA", 34, INK, COND, "bold")
    _text(fig, 0.06, 0.893, "6 eksen eşit etkili (standartlaştırılmış) · lig ortalaması = 50 · sağ: ortalamanın üstü",
          9, INK2)
    n = len(d)
    top, bottom = 0.85, 0.1
    rowh = (top - bottom) / n
    cx, half = 0.66, 0.24          # 50 çizgisinin x'i ve ±20 puanın genişliği
    span = 20.0
    fig.add_artist(plt.Line2D([cx, cx], [bottom, top + 0.01], color=MUTED, lw=0.9, ls=(0, (2, 2))))
    _text(fig, cx, top + 0.016, "50", 8, MUTED, COND, "semibold", ha="center")
    for v in (40, 60):
        x = cx + (v - 50) / span * half
        fig.add_artist(plt.Line2D([x, x], [bottom, top], color=LINE, lw=0.6))
        _text(fig, x, top + 0.016, str(v), 7, MUTED, COND, ha="center")
    for i, r in d.iterrows():
        y = top - (i + 0.5) * rowh
        _text(fig, 0.075, y, str(i + 1), 13, GOLD if i < 3 else MUTED, COND, "bold", ha="right", va="center")
        _place_logo(fig, r.takim, 0.115, y, 32)
        _text(fig, 0.15, y, r.takim, 12, INK, COND, "semibold", va="center")
        dv = (r.genel_skor - 50) / span * half
        x0 = cx if dv >= 0 else cx + dv
        fig.add_artist(FancyBboxPatch((x0, y - rowh * 0.24), max(abs(dv), 0.003), rowh * 0.48,
                                      boxstyle="round,pad=0,rounding_size=0.004", transform=fig.transFigure,
                                      facecolor=GOLD if i < 3 else ("#dfe5e1" if dv >= 0 else "#5b6560"), edgecolor="none"))
        tx = cx + dv + (0.012 if dv >= 0 else -0.012)
        lab = _tr(r.genel_skor, 1) + (" *" if r.genel_boyut_sayisi < 6 else "")
        _text(fig, tx, y, lab, 10, INK, COND, "bold", ha="left" if dv >= 0 else "right", va="center")
    _text(fig, 0.06, 0.075, "* forma fiyatı bulunamadığı için 5 eksenle hesaplandı. Radar eksenleri gerçek yüzdeleri gösterir.",
          7.2, MUTED)
    _footer(fig, "Genel skor = 50 + 10 × (6 eksenin z-skorlarının ortalaması)")
    fig.savefig(path, dpi=DPI, facecolor=BG)
    plt.close(fig)


def render_all():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):  # sıralama değişince eski numaralı dosyalar kalmasın
        old.unlink()
    df = scorecard.build()
    sc_cols = [f"skor_{k}" for k, _ in scorecard.AXES]
    df["genel"] = df["genel_skor"]
    df = df.sort_values("genel", ascending=False).reset_index(drop=True)
    avg = df[sc_cols].mean().values
    cover(df, avg, OUT / "00_kapak.png")
    overall_slide(df, OUT / "01_genel_siralama.png")
    for i, r in df.iterrows():
        team_card(r, avg, i + 1, len(df), OUT / f"takim_{i + 1:02d}_{logos.file_for(r.takim).stem}.png")
    page = 0
    for key, title, sub, col, fmt in METRIC_SLIDES:
        page += 1
        weak, wl = None, None
        if key == "forma":
            weak, wl = (lambda r: r.forma_gercek_sezon < 2), ("Soluk: 10 sezondan yalnız birinin gerçek fiyatı var. Eksik sezonlar diğer kulüplerin"
                                                             " sezonluk artışıyla tamamlandı (test: medyan hata %9).")
        elif key == "sadakat":
            weak, wl = (lambda r: r.get("takipci_platform", 5) < 3), "Soluk çubuk: 3'ten az platformda takipçi verisi · Karagümrük doluluğu belirsiz (hangi stadın kapasitesi esas alınacağı net değil)"
        metric_slide(df, key, title, sub, col, fmt, OUT / f"metrik_{page}_{key}.png", f"{page}/6", weak, wl)
    log.info("Instagram görselleri: %s", OUT)
    return df
