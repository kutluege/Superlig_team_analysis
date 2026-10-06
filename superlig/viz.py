"""Amblemli sıralama görselleri (PNG) ve etkileşimli HTML pano."""
from __future__ import annotations

import base64
import io
import json
import logging

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import transforms
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

from . import config, logos, teams

log = logging.getLogger("superlig.viz")

# Görsel dil: tek seri = tek renk (mavi), metin her zaman nötr mürekkep,
# ızgara çok silik; kimliği amblem taşır, renk değil.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#8a8985"
GRID = "#e6e5e1"
BLUE = "#2a78d6"
BLUE_SOFT = "#9ec5f4"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

_logo_cache: dict[str, np.ndarray] = {}


def logo_img(team: str, px: int = 64) -> np.ndarray:
    key = f"{team}:{px}"
    if key not in _logo_cache:
        im = Image.open(logos.file_for(team)).convert("RGBA").resize((px, px), Image.LANCZOS)
        _logo_cache[key] = np.asarray(im)
    return _logo_cache[key]


def add_logo(ax, team, x, y, px=28, xycoords="data"):
    ab = AnnotationBbox(OffsetImage(logo_img(team, px * 2), zoom=0.5), (x, y),
                        xycoords=xycoords, frameon=False, box_alignment=(0.5, 0.5),
                        annotation_clip=False)
    ax.add_artist(ab)


def _title(fig, title, subtitle):
    fig.text(0.02, 0.985, title, fontsize=17, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.985 - 0.035 * (12 / fig.get_figheight()), subtitle, fontsize=10.5,
             color=INK_2, va="top")


def _footer(fig, text):
    fig.text(0.02, 0.008, text, fontsize=8, color=MUTED, va="bottom")


def _clean(ax):
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


SOURCE_NOTE = ("Kaynak: football-data.co.uk (GitHub aynası) · Sofascore, openfootball ve Transfermarkt ile çapraz kontrol\n"
               "Puanlar matches.csv'den hesaplanmıştır; TFF puan silme cezaları dahil değildir.")


# ---------------------------------------------------------------- yatay sıralama
def ranking_bar(df, value, title, subtitle, fname, fmt="{:.0f}", extra=None, note=SOURCE_NOTE):
    """df: takim + value; büyükten küçüğe amblemli yatay çubuk sıralaması."""
    df = df.sort_values(value, ascending=False).reset_index(drop=True)
    n = len(df)
    h = max(4.5, 0.36 * n + 1.9)
    fig, ax = plt.subplots(figsize=(10, h))
    fig.subplots_adjust(left=0.30, right=0.90, top=1 - 1.25 / h, bottom=0.75 / h)
    y = np.arange(n)
    vmax = df[value].max()
    ax.barh(y, df[value], height=0.62, color=BLUE, zorder=2)
    ax.set_ylim(n - 0.4, -0.6)
    ax.set_xlim(0, vmax * 1.12)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.10g}".replace(",", " ").replace(".", ",")))
    ax.set_yticks([])
    _clean(ax)
    blend = transforms.blended_transform_factory(fig.transFigure, ax.transData)
    for i, r in df.iterrows():
        ax.text(0.045, i, f"{i + 1}", transform=blend, ha="right", va="center",
                color=MUTED, fontsize=9.5, fontweight="bold")
        ax.text(0.06, i, r.takim, transform=blend, ha="left", va="center", color=INK, fontsize=10)
        add_logo(ax, r.takim, -0.035, i, px=22, xycoords=ax.get_yaxis_transform())
        label = fmt.format(r[value]).replace(".", ",")
        if extra is not None:
            label += f"  {extra(r)}"
        ax.text(r[value] + vmax * 0.01, i, label, va="center", ha="left", color=INK_2, fontsize=9)
    _title(fig, title, subtitle)
    _footer(fig, note)
    fig.savefig(config.FIGURES / fname, dpi=150)
    plt.close(fig)
    log.info("görsel: %s", fname)


# ---------------------------------------------------------------- sezon puan tablosu
def season_table_figure(t: pd.DataFrame, season: str):
    t = t.sort_values("sira").reset_index(drop=True)
    n = len(t)
    h = 0.42 * n + 2.0
    fig = plt.figure(figsize=(12, h))
    top = 1 - 1.3 / h
    bottom = 0.75 / h
    ax = fig.add_axes([0.30, bottom, 0.38, top - bottom])
    ax.barh(np.arange(n), t.puan, height=0.62, color=BLUE, zorder=2)
    ax.set_ylim(n - 0.4, -0.6)
    ax.set_xlim(0, t.puan.max() * 1.1)
    ax.set_yticks([])
    _clean(ax)
    ax.set_facecolor("none")
    cols = [("O", "oynanan"), ("G", "galibiyet"), ("B", "beraberlik"), ("M", "maglubiyet"),
            ("AG", "atilan_gol"), ("YG", "yenilen_gol"), ("AV", "averaj")]
    xs = np.linspace(0.725, 0.965, len(cols))
    blend = transforms.blended_transform_factory(fig.transFigure, ax.transData)
    for x, (lab, _) in zip(xs, cols):
        fig.text(x, -0.85, lab, ha="center", va="center", color=MUTED, fontsize=9,
                 fontweight="bold", transform=blend)
    trans = ax.get_yaxis_transform()
    for i, r in t.iterrows():
        if i % 2 == 0:
            fig.patches.append(plt.Rectangle((0.02, i - 0.5), 0.96, 1, transform=blend,
                                             facecolor="#f3f2ef", zorder=-1, figure=fig))
        ax.text(-0.66, i, f"{int(r.sira)}", transform=trans, ha="right", va="center",
                color=INK, fontsize=11, fontweight="bold")
        add_logo(ax, r.takim, -0.59, i, px=26, xycoords=trans)
        ax.text(-0.53, i, r.takim, transform=trans, ha="left", va="center", color=INK, fontsize=11)
        ax.text(r.puan + t.puan.max() * 0.012, i, f"{int(r.puan)}", va="center", ha="left",
                color=INK, fontsize=10, fontweight="bold")
        for x, (_, c) in zip(xs, cols):
            v = int(r[c])
            fig.text(x, i, f"{v:+d}" if c == "averaj" and v else f"{v}", ha="center",
                     va="center", color=INK_2, fontsize=10, transform=blend)
    _title(fig, f"Süper Lig {season} puan durumu",
           "Sıralama: puan → ikili averaj → genel averaj → atılan gol")
    _footer(fig, SOURCE_NOTE)
    fname = f"puan_durumu_{season}.png"
    fig.savefig(config.FIGURES / fname, dpi=150)
    plt.close(fig)
    log.info("görsel: %s", fname)


# ---------------------------------------------------------------- sıra ısı haritası
def rank_heatmap(ts: pd.DataFrame):
    piv = ts.pivot(index="takim", columns="sezon", values="sira")[config.SEASONS]
    seasons_in = piv.notna().sum(axis=1)
    order = piv.assign(_n=seasons_in, _avg=piv.mean(axis=1)).sort_values(["_n", "_avg"], ascending=[False, True]).index
    piv = piv.loc[order]
    n, m = piv.shape
    h = 0.34 * n + 2.2
    fig = plt.figure(figsize=(11, h))
    top, bottom = 1 - 1.45 / h, 0.75 / h
    ax = fig.add_axes([0.27, bottom, 0.70, top - bottom])
    cmap = LinearSegmentedColormap.from_list("rank", SEQ[::-1])
    maxrank = 21
    for i, team in enumerate(piv.index):
        for j, s in enumerate(piv.columns):
            v = piv.at[team, s]
            if pd.isna(v):
                ax.add_patch(plt.Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, facecolor="none",
                                           edgecolor=GRID, linewidth=0.8, linestyle="-"))
                continue
            frac = (v - 1) / (maxrank - 1)
            col = cmap(frac)
            ax.add_patch(plt.Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, facecolor=col, linewidth=0))
            lum = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
            ax.text(j + 0.5, i + 0.5, f"{int(v)}", ha="center", va="center", fontsize=9,
                    color="white" if lum < 0.55 else INK, fontweight="bold" if v == 1 else "normal")
    ax.set_xlim(0, m)
    ax.set_ylim(n, 0)
    ax.set_xticks(np.arange(m) + 0.5)
    ax.set_xticklabels(piv.columns, fontsize=9)
    ax.xaxis.tick_top()
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    for i, team in enumerate(piv.index):
        add_logo(ax, team, -0.035, i + 0.5, px=26, xycoords=("axes fraction", "data"))
        ax.text(-0.07, i + 0.5, f"{team}", transform=ax.get_yaxis_transform(), ha="right",
                va="center", fontsize=9.5, color=INK)
    _title(fig, "Takımların sezon sonu sıraları (2016-17 → 2025-26)",
           "Koyu mavi = üst sıra · boş kutu = o sezon Süper Lig'de değil (NaN) · "
           "takımlar ligde geçirdiği sezon sayısına göre sıralı")
    _footer(fig, SOURCE_NOTE)
    fig.savefig(config.FIGURES / "sira_isi_haritasi.png", dpi=150)
    plt.close(fig)
    log.info("görsel: sira_isi_haritasi.png")


# ---------------------------------------------------------------- şampiyon/podyum şeridi
def podium_strip(ts: pd.DataFrame):
    n = len(config.SEASONS)
    fig = plt.figure(figsize=(16, 6.2))
    ax = fig.add_axes([0.06, 0.04, 0.93, 0.74])
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(3.55, 0.25)
    ax.axis("off")
    ys = {1: 1.0, 2: 2.05, 3: 2.95}
    for j, s in enumerate(config.SEASONS):
        if j % 2 == 0:
            ax.axvspan(j - 0.5, j + 0.5, color="#f3f2ef", zorder=0)
        g = ts[(ts.sezon == s) & ts.ligde].sort_values("sira").head(3)
        ax.text(j, 0.32, s, ha="center", va="center", fontsize=11, color=INK, fontweight="bold")
        for r in g.itertuples():
            k = int(r.sira)
            add_logo(ax, r.takim, j, ys[k] - 0.12, px=58 if k == 1 else 38)
            off = 0.36 if k == 1 else 0.27
            ax.text(j, ys[k] + off, r.takim, ha="center", va="center", fontsize=9 if k == 1 else 8,
                    color=INK if k == 1 else INK_2, fontweight="bold" if k == 1 else "normal")
            ax.text(j, ys[k] + off + 0.15, f"{int(r.puan)} puan", ha="center", va="center", fontsize=8, color=MUTED)
    for k, lab in [(1, "Şampiyon"), (2, "2."), (3, "3.")]:
        ax.text(-0.62, ys[k] - 0.12, lab, ha="right", va="center", fontsize=11, color=INK_2, fontweight="bold")
    fig.text(0.02, 0.97, "Sezon sezon ilk üç", fontsize=18, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.905, "matches.csv'den hesaplanan puan tablosuna göre şampiyon ve podyum", fontsize=11,
             color=INK_2, va="top")
    fig.savefig(config.FIGURES / "podyum.png", dpi=150)
    plt.close(fig)
    log.info("görsel: podyum.png")


# ---------------------------------------------------------------- HTML pano
def _logo_data_uri(team: str) -> str:
    im = Image.open(logos.file_for(team)).convert("RGBA").resize((64, 64), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def dashboard(ts: pd.DataFrame, att: pd.DataFrame, matches: pd.DataFrame, conflicts: pd.DataFrame,
              missing_summary: dict):
    from .dashboard_template import TEMPLATE
    rows = ts[ts.ligde].copy()
    a = att[att.ligde][["takim", "sezon", "ort_seyirci", "kapasite", "kaynak"]]
    rows = rows.merge(a, on=["takim", "sezon"], how="left")
    rows["doluluk"] = rows.ort_seyirci / rows.kapasite
    recs = json.loads(rows.drop(columns=["ligde"]).to_json(orient="records"))
    teams_used = sorted(rows.takim.unique())
    payload = {
        "seasons": config.SEASONS,
        "rows": recs,
        "logos": {t: _logo_data_uri(t) for t in teams_used},
        "placeholder": [t for t in teams_used if not teams.logo_path(t)],
        "conflicts": json.loads(conflicts.fillna("").to_json(orient="records")),
        "summary": missing_summary,
        "n_matches": int(len(matches)),
    }
    body = TEMPLATE.replace("/*__DATA__*/null", json.dumps(payload, ensure_ascii=False))
    html = ('<!doctype html>\n<html lang="tr">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
    out = config.REPORTS / "pano.html"
    out.write_text(html, encoding="utf-8")
    log.info("pano: %s (%.0f KB)", out, out.stat().st_size / 1024)


# ---------------------------------------------------------------- hepsi
def render_all():
    config.FIGURES.mkdir(parents=True, exist_ok=True)
    ts = pd.read_csv(config.DATA / "team_season.csv")
    att = pd.read_csv(config.DATA / "attendance.csv")
    matches = pd.read_csv(config.DATA / "matches.csv")
    conflicts = pd.read_csv(config.DATA / "celiskiler.csv")
    lg = ts[ts.ligde]

    for s in config.SEASONS:
        season_table_figure(lg[lg.sezon == s], s)
    rank_heatmap(ts)
    podium_strip(ts)

    agg = lg.groupby("takim").agg(sezon=("sezon", "size"), oynanan=("oynanan", "sum"),
                                  puan=("puan", "sum"), galibiyet=("galibiyet", "sum"),
                                  atilan_gol=("atilan_gol", "sum"), yenilen_gol=("yenilen_gol", "sum"),
                                  ic=("ic_saha_puan", "sum"), dis=("dis_saha_puan", "sum")).reset_index()
    agg["mbp"] = agg.puan / agg.oynanan
    agg["mb_gol"] = agg.atilan_gol / agg.oynanan
    agg["ic_mbp"] = agg.ic / (agg.oynanan / 2)
    sub = "2016-17 → 2025-26 · {} takım · etiket yanında: Süper Lig'de geçirilen sezon sayısı"
    ranking_bar(agg, "puan", "10 sezonluk toplam puan sıralaması", sub.format(len(agg)),
                "toplam_puan.png", extra=lambda r: f"({r.sezon} sz)")
    ranking_bar(agg, "galibiyet", "10 sezonluk toplam galibiyet sıralaması", sub.format(len(agg)),
                "toplam_galibiyet.png", extra=lambda r: f"({r.sezon} sz)")
    ranking_bar(agg, "atilan_gol", "10 sezonluk toplam atılan gol sıralaması", sub.format(len(agg)),
                "toplam_atilan_gol.png", extra=lambda r: f"({r.sezon} sz)")
    q = agg[agg.sezon >= 3]
    ranking_bar(q, "mbp", "Maç başına puan sıralaması",
                f"En az 3 sezon Süper Lig'de oynayan {len(q)} takım · ligde geçirilen süreden bağımsız karşılaştırma",
                "mac_basi_puan.png", fmt="{:.2f}", extra=lambda r: f"({r.sezon} sz)")
    ranking_bar(q, "mb_gol", "Maç başına atılan gol sıralaması",
                f"En az 3 sezon Süper Lig'de oynayan {len(q)} takım", "mac_basi_gol.png", fmt="{:.2f}")
    ranking_bar(q, "ic_mbp", "İç sahada maç başına puan sıralaması",
                f"En az 3 sezon Süper Lig'de oynayan {len(q)} takım", "ic_saha_mac_basi_puan.png", fmt="{:.2f}")

    a = att[att.ligde & att.ort_seyirci.notna()]
    if not a.empty:
        aa = a.groupby("takim").agg(ort_seyirci=("ort_seyirci", "mean")).reset_index()
        ranking_bar(aa, "ort_seyirci", "Ortalama seyirci sıralaması", "Sezon ortalamalarının ortalaması",
                    "ortalama_seyirci.png", fmt="{:,.0f}")
    else:
        log.warning("Seyirci verisi yok; seyirci görselleri üretilmedi.")

    miss = pd.read_csv(config.DATA / "eksik_veri_raporu.csv")
    summary = {
        "att_missing": int(((miss.durum == "eksik") & (miss.alan == "ort_seyirci")).sum()),
        "cap_missing": int(((miss.durum == "eksik") & (miss.alan == "kapasite")).sum()),
        "match_missing": int(((miss.durum == "eksik") & (miss.alan == "maçlar")).sum()),
        "att_reason": (miss[miss.alan == "ort_seyirci"].aciklama.iloc[0]
                       if (miss.alan == "ort_seyirci").any() else ""),
    }
    dashboard(ts, att, matches, conflicts, summary)
