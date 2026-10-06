"""Tüm kaynakları çeker, birleştirir, çelişkileri ve eksikleri raporlar."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import config, standings, teams
from .net import Fetcher
from .sources import footballdata, openfootball, sofascore, wikipedia

log = logging.getLogger("superlig.build")

# Kaynak grupları ve çelişki çözümünde öncelik sırası (eşit oyda ilk gelen kazanır)
GROUPS = ["football-data", "sofascore", "openfootball", "transfermarkt"]


def _group(kaynak: str) -> str:
    return next(g for g in GROUPS if kaynak.startswith(g.replace("football-data", "football-data.co.uk")))


# ---------------------------------------------------------------- isimler
def standardize_frame(df: pd.DataFrame, mapping: list, unmapped: list) -> pd.DataFrame:
    if df.empty:
        return df
    for raw in pd.unique(pd.concat([df.ev_raw, df.dep_raw])):
        std = teams.standardize(raw)
        mapping.append({"kaynak": df["kaynak"].iloc[0], "kaynak_adi": raw, "standart_ad": std})
        if std is None:
            unmapped.append((df["kaynak"].iloc[0], raw))
            log.error("Eşleşmeyen takım adı [%s]: %r — bu maçlar dışarıda bırakıldı",
                      df["kaynak"].iloc[0], raw)
    df = df.assign(ev=df.ev_raw.map(teams.standardize), deplasman=df.dep_raw.map(teams.standardize))
    return df.dropna(subset=["ev", "deplasman"])


def team_mapping(mapping: list) -> pd.DataFrame:
    tm = pd.DataFrame(mapping).drop_duplicates()
    tm["kaynak"] = tm["kaynak"].map(_group)
    tm = tm.drop_duplicates().sort_values(["standart_ad", "kaynak", "kaynak_adi"], na_position="first")
    # logo deposundaki dosya adı da bir kaynak yazımıdır
    logos = [{"kaynak": "logo (luukhopman/football-logos)",
              "kaynak_adi": teams.logo_path(s).rsplit("/", 1)[-1].removesuffix(".png"),
              "standart_ad": s} for s in teams.CLUBS if teams.logo_path(s)]
    tm = pd.concat([tm, pd.DataFrame(logos)], ignore_index=True)
    tm["kisa_kod"] = tm["standart_ad"].map(lambda s: teams.short_code(s) if s else None)
    return tm.sort_values(["standart_ad", "kaynak"], na_position="first").reset_index(drop=True)


# ---------------------------------------------------------------- maçlar
def merge_matches(sources: dict[str, pd.DataFrame]):
    key = ["sezon_yil", "ev", "deplasman"]
    by_group = {}
    for g, df in sources.items():
        if df.empty:
            continue
        dup = df.duplicated(key, keep=False)
        if dup.any():
            log.warning("%s: %d tekrar eden maç kaydı (ilk kayıt tutuldu)", g, dup.sum())
        by_group[g] = df.drop_duplicates(key).set_index(key)

    all_keys = sorted(set().union(*[set(d.index) for d in by_group.values()]))
    rows, conflicts = [], []
    for k in all_keys:
        vals = {}
        for g in GROUPS:
            d = by_group.get(g)
            if d is not None and k in d.index:
                r = d.loc[k]
                if pd.notna(r.ev_gol) and pd.notna(r.dep_gol):
                    vals[g] = (int(r.ev_gol), int(r.dep_gol), r.tarih, r.kaynak,
                               bool(r.get("hukmen", False)) if "hukmen" in r else False)
        if not vals:
            continue
        scores = [(v[0], v[1]) for v in vals.values()]
        counts = {s: scores.count(s) for s in scores}
        best = max(counts.values())
        chosen_score = next((v[0], v[1]) for g, v in vals.items() if counts[(v[0], v[1])] == best)
        chosen_group = next(g for g, v in vals.items() if (v[0], v[1]) == chosen_score)
        agree = [g for g, v in vals.items() if (v[0], v[1]) == chosen_score]
        date_src = next((g for g in ["football-data", "sofascore", "openfootball"]
                         if g in vals and pd.notna(vals[g][2])), None)
        tarih = vals[date_src][2] if date_src else pd.NaT
        hukmen = any(v[4] for v in vals.values())
        conflict = len(counts) > 1
        rows.append({
            "sezon": config.season_label(k[0]), "tarih": tarih, "ev": k[1], "deplasman": k[2],
            "ev_gol": chosen_score[0], "dep_gol": chosen_score[1],
            "kaynak": vals[chosen_group][3],
            "dogrulayan_kaynaklar": ";".join(agree), "kaynak_sayisi": len(vals),
            "celiski": conflict, "hukmen": hukmen,
        })
        if conflict:
            c = {"sezon": config.season_label(k[0]), "ev": k[1], "deplasman": k[2], "alan": "skor",
                 "secilen": f"{chosen_score[0]}-{chosen_score[1]}", "secilen_kaynak": chosen_group,
                 "secim_kurali": "çoğunluk" if sorted(counts.values())[-2] < best
                                 else "öncelik (football-data > sofascore > openfootball > transfermarkt)",
                 "hukmen": hukmen}
            for g in GROUPS:
                c[g] = f"{vals[g][0]}-{vals[g][1]}" if g in vals else ""
            conflicts.append(c)
        # tarih çelişkisi (2 günden fazla fark: ertelenen maç vb.)
        dates = {g: pd.Timestamp(v[2]) for g, v in vals.items() if pd.notna(v[2])}
        if len(dates) > 1 and (max(dates.values()) - min(dates.values())).days > 1:
            c = {"sezon": config.season_label(k[0]), "ev": k[1], "deplasman": k[2], "alan": "tarih",
                 "secilen": str(tarih), "secilen_kaynak": date_src, "secim_kurali": "öncelik",
                 "hukmen": hukmen}
            for g in GROUPS:
                c[g] = str(dates[g].date()) if g in dates else ""
            conflicts.append(c)

    m = pd.DataFrame(rows).sort_values(["sezon", "tarih", "ev"], na_position="last").reset_index(drop=True)
    return m, pd.DataFrame(conflicts)


# ---------------------------------------------------------------- tablolar
def season_teams(m: pd.DataFrame) -> dict[str, set]:
    return {s: set(g.ev) | set(g.deplasman) for s, g in m.groupby("sezon")}


def team_season(m: pd.DataFrame) -> pd.DataFrame:
    tables = []
    for s, g in m.groupby("sezon"):
        t = standings.season_table(g)
        t.insert(1, "sezon", s)
        tables.append(t)
    t = pd.concat(tables, ignore_index=True)
    panel = pd.MultiIndex.from_product([sorted(set(t.takim)), config.SEASONS], names=["takim", "sezon"])
    t = t.set_index(["takim", "sezon"]).reindex(panel).reset_index()
    t["ligde"] = t["oynanan"].notna()
    cols = ["takim", "sezon", "oynanan", "galibiyet", "beraberlik", "maglubiyet", "atilan_gol",
            "yenilen_gol", "averaj", "puan", "sira", "ic_saha_puan", "dis_saha_puan", "ligde"]
    t = t[cols]
    for c in cols[2:-1]:
        t[c] = t[c].astype("Int64")
    return t


# COVID-19: 2020-21'in tamamı ve 2019-20'nin Mart 2020 sonrası seyircisiz oynandı
COVID_NOTE = {"2019-20": "Mart 2020 sonrası maçlar COVID-19 nedeniyle seyircisiz oynandı.",
              "2020-21": "Sezon COVID-19 nedeniyle büyük ölçüde seyircisiz oynandı."}
MIN_ATT_SHARE = 0.5  # Sofascore ortalaması için seyirci kaydı olan iç saha maçı oranı alt sınırı


def attendance(ss_att: pd.DataFrame, wiki: pd.DataFrame, in_league: dict[str, set], conflicts: list,
               matches: pd.DataFrame):
    """Seyirci: Sofascore (iç saha maçlarının en az yarısında kayıt varsa) → Wikipedia.
    Kapasite: Wikipedia sezon tablosu → Sofascore. Sofascore'un etkinlik stadı bazı kulüplerde
    o sezon oynanan stadı değil kulübün güncel stadını gösterdiği için kapasitede Wikipedia önce gelir.
    İki kaynak %5'ten fazla farklıysa ikisi de celiskiler.csv'ye yazılır."""
    home_n = matches.groupby(["ev", "sezon"]).size()
    ss = pd.DataFrame(columns=["takim", "sezon", "ort_seyirci", "seyirci_mac", "kapasite"])
    if not ss_att.empty:
        ss_att = ss_att.assign(sezon=ss_att.sezon_yil.map(config.season_label))
        ss = ss_att.groupby(["ev", "sezon"]).agg(
            ort_seyirci=("seyirci", "mean"), seyirci_mac=("seyirci", "count"),
            kapasite=("kapasite", lambda x: x.mode().iloc[0] if x.notna().any() else np.nan),
        ).reset_index().rename(columns={"ev": "takim"})
    wk = (wiki.assign(sezon=wiki.sezon_yil.map(config.season_label)) if not wiki.empty
          else pd.DataFrame(columns=["takim", "sezon", "ort_seyirci", "kapasite"]))

    def pick(t, s, field, order):
        vals = {}
        r = ss[(ss.takim == t) & (ss.sezon == s)]
        if not r.empty and pd.notna(r[field].iloc[0]):
            vals[sofascore.SRC] = float(r[field].iloc[0])
        r = wk[(wk.takim == t) & (wk.sezon == s)]
        if not r.empty and pd.notna(r[field].iloc[0]):
            vals[wikipedia.SRC] = float(r[field].iloc[0])
        usable = {k: v for k, v in vals.items() if k in order}
        if not usable:
            return None, None, vals
        src = next(k for k in order if k in usable)
        for other, v in vals.items():
            if other != src and abs(v - usable[src]) > 0.05 * max(usable[src], 1):
                conflicts.append({"sezon": s, "ev": t, "deplasman": "", "alan": field,
                                  "secilen": round(usable[src]), "secilen_kaynak": src,
                                  "secim_kurali": f"öncelik ({' > '.join(order)})",
                                  sofascore.SRC: vals.get(sofascore.SRC, ""), wikipedia.SRC: vals.get(wikipedia.SRC, "")})
        return usable[src], src, vals

    out = []
    for t in sorted(set().union(*in_league.values())):
        for s in config.SEASONS:
            lig = t in in_league.get(s, set())
            row = {"takim": t, "sezon": s, "ort_seyirci": np.nan, "kapasite": np.nan, "kaynak": np.nan,
                   "ev_mac": np.nan, "seyirci_mac": np.nan, "not": "", "ligde": lig}
            if not lig:
                row["not"] = "Takım bu sezon Süper Lig'de değil."
                out.append(row)
                continue
            notes = [COVID_NOTE.get(s, "")]
            n_home = int(home_n.get((t, s), 0))
            r = ss[(ss.takim == t) & (ss.sezon == s)]
            n_att = int(r.seyirci_mac.iloc[0]) if not r.empty else 0
            row.update(ev_mac=n_home, seyirci_mac=n_att)
            att_order = [wikipedia.SRC]
            if n_home and n_att >= MIN_ATT_SHARE * n_home:
                att_order = [sofascore.SRC, wikipedia.SRC]
            elif n_att:
                notes.append(f"Sofascore'da yalnızca {n_att}/{n_home} iç saha maçında seyirci var; "
                             "ortalama için yetersiz sayıldı.")
            v_att, s_att, _ = pick(t, s, "ort_seyirci", att_order)
            v_cap, s_cap, _ = pick(t, s, "kapasite", [wikipedia.SRC, sofascore.SRC])
            if v_att is not None:
                row["ort_seyirci"] = round(v_att)
            if v_cap is not None:
                row["kapasite"] = round(v_cap)
            used = [x for x in (s_att, s_cap) if x]
            row["kaynak"] = ";".join(dict.fromkeys(used)) if used else np.nan
            if s_att and s_cap and s_att != s_cap:
                notes.append(f"Seyirci: {s_att}, kapasite: {s_cap}.")
            row["not"] = " ".join(n for n in notes if n)
            out.append(row)
    a = pd.DataFrame(out)
    for c in ["ort_seyirci", "kapasite", "ev_mac", "seyirci_mac"]:
        a[c] = a[c].astype("Int64")
    return a


# ---------------------------------------------------------------- eksik veri
def missing_report(m, ts, att, coverage) -> pd.DataFrame:
    rows = []
    n_teams = {s: len(v) for s, v in season_teams(m).items()}
    for _, r in ts.iterrows():
        if not r.ligde:
            rows.append({"takim": r.takim, "sezon": r.sezon, "alan": "tümü", "durum": "ligde değil",
                         "aciklama": "Takım bu sezon Süper Lig'de değil; değerler NaN bırakıldı."})
            continue
        expected = 2 * (n_teams[r.sezon] - 1)
        if r.oynanan < expected:
            rows.append({"takim": r.takim, "sezon": r.sezon, "alan": "maçlar", "durum": "eksik",
                         "aciklama": f"{r.oynanan}/{expected} maç skoru mevcut "
                                     f"({expected - r.oynanan} maç hiçbir kaynakta yok)."})
    for _, r in att[att.ligde].iterrows():
        for field, label in [("ort_seyirci", "ort_seyirci"), ("kapasite", "kapasite")]:
            if pd.isna(r[field]):
                why = coverage["attendance_reason"]
                if field == "ort_seyirci" and r["not"]:
                    why = f"{r['not']} Wikipedia sezon sayfasında da bu takım için seyirci yok."
                elif field == "kapasite":
                    why = "Ne Wikipedia sezon tablosunda ne Sofascore maç detayında kapasite var."
                rows.append({"takim": r.takim, "sezon": r.sezon, "alan": label, "durum": "eksik",
                             "aciklama": why})
    return pd.DataFrame(rows)


def run() -> dict:
    fetcher = Fetcher()
    log.info("=== Süper Lig veri hattı başladı (%s) ===", datetime.now(timezone.utc).isoformat())

    fd = footballdata.load(fetcher)
    sids = sofascore.season_ids(fetcher)
    ss = sofascore.load_matches(fetcher, sids)
    of = openfootball.load(fetcher)
    tm = sofascore.load_transfermarkt_mirror(fetcher)

    mapping, unmapped = [], []
    srcs = {}
    for g, df in [("football-data", fd), ("sofascore", ss), ("openfootball", of), ("transfermarkt", tm)]:
        parts = [standardize_frame(part, mapping, unmapped) for _, part in df.groupby("kaynak")] if not df.empty else []
        srcs[g] = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        log.info("%s: %d maç", g, len(srcs[g]))

    matches, conflicts = merge_matches(srcs)
    conflict_rows = conflicts.to_dict("records")

    ts = team_season(matches)
    in_league = season_teams(matches)

    # seyirci / kapasite
    ss_ids = srcs["sofascore"]
    ss_att = sofascore.load_attendance(fetcher, ss_ids)
    wiki = wikipedia.load(fetcher)
    if not wiki.empty:
        wiki = wiki[wiki.apply(lambda r: r.takim in in_league.get(config.season_label(r.sezon_yil), set()), axis=1)]
    att = attendance(ss_att, wiki, in_league, conflict_rows, matches)
    if not ss_att.empty:
        ss_att.to_csv(config.RAW / "sofascore_mac_seyirci.csv", index=False)

    attempts = pd.DataFrame([a.__dict__ for a in fetcher.attempts])
    # yalnızca bağlantı düzeyinde erişilemeyen hostlar (HTTP 404 gibi yanıtlar sayılmaz)
    blocked = sorted(fetcher._down)
    att_hosts = [h for h in blocked if "sofascore" in h or "wikipedia" in h]
    reason = ("Seyirci/kapasite bulunamadı: bu çalıştırmada Sofascore ve Wikipedia'ya bağlanılamadı "
              f"({', '.join(att_hosts)}); GitHub aynalarında seyirci verisi yok."
              if ss_att.empty and wiki.empty
              else "Seyirci/kapasite kaynaklarda bu takım-sezon için yer almıyor.")
    coverage = {"attendance_reason": reason}

    # kaynak kapsamı (sezon x kaynak grubu maç sayısı)
    cov = pd.DataFrame({g: (d.groupby("sezon_yil").size() if not d.empty else pd.Series(dtype=int))
                        for g, d in srcs.items()}).reindex(config.SEASON_YEARS).fillna(0).astype(int)
    cov.index = [config.season_label(y) for y in cov.index]
    cov["matches.csv"] = matches.groupby("sezon").size().reindex(cov.index).fillna(0).astype(int)
    label_used = matches.groupby("sezon")["kaynak"].agg(lambda s: "; ".join(f"{k}: {v}" for k, v in s.value_counts().items()))
    cov["kullanilan_kaynak"] = label_used.reindex(cov.index)

    miss = missing_report(matches, ts, att, coverage)
    mapping_df = team_mapping(mapping)

    # ---- yaz
    config.DATA.mkdir(exist_ok=True)
    matches.to_csv(config.DATA / "matches.csv", index=False)
    ts.to_csv(config.DATA / "team_season.csv", index=False)
    att.to_csv(config.DATA / "attendance.csv", index=False)
    mapping_df.to_csv(config.DATA / "team_mapping.csv", index=False)
    pd.DataFrame(conflict_rows).to_csv(config.DATA / "celiskiler.csv", index=False)
    miss.to_csv(config.DATA / "eksik_veri_raporu.csv", index=False)
    attempts.to_csv(config.LOGS / "kaynak_istekleri.csv", index=False)
    cov.to_csv(config.DATA / "kaynak_kapsami.csv", index_label="sezon")

    return {"matches": matches, "team_season": ts, "attendance": att, "conflicts": pd.DataFrame(conflict_rows),
            "missing": miss, "coverage": cov, "attempts": attempts, "unmapped": unmapped,
            "mapping": mapping_df, "blocked": blocked, "sids": sids}
