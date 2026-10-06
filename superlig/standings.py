"""matches.csv'den puan durumu hesaplama.

Sıralama: puan → aralarındaki maçlarda puan → aralarındaki averaj →
aralarındaki atılan gol → genel averaj → atılan gol (Süper Lig talimatı).
Puan silme cezaları maç verisinde olmadığı için uygulanmaz.
"""
from __future__ import annotations

import pandas as pd


def _long(m: pd.DataFrame) -> pd.DataFrame:
    h = pd.DataFrame({"takim": m["ev"], "rakip": m["deplasman"], "ag": m["ev_gol"], "yg": m["dep_gol"], "ic": 1})
    a = pd.DataFrame({"takim": m["deplasman"], "rakip": m["ev"], "ag": m["dep_gol"], "yg": m["ev_gol"], "ic": 0})
    d = pd.concat([h, a], ignore_index=True)
    d["g"] = (d.ag > d.yg).astype(int)
    d["b"] = (d.ag == d.yg).astype(int)
    d["m"] = (d.ag < d.yg).astype(int)
    d["p"] = 3 * d.g + d.b
    return d


def _table(d: pd.DataFrame) -> pd.DataFrame:
    t = d.groupby("takim").agg(
        oynanan=("p", "size"), galibiyet=("g", "sum"), beraberlik=("b", "sum"),
        maglubiyet=("m", "sum"), atilan_gol=("ag", "sum"), yenilen_gol=("yg", "sum"),
        puan=("p", "sum"),
        ic_saha_puan=("p", lambda s: s[d.loc[s.index, "ic"] == 1].sum()),
        dis_saha_puan=("p", lambda s: s[d.loc[s.index, "ic"] == 0].sum()),
    )
    t["averaj"] = t.atilan_gol - t.yenilen_gol
    return t


def season_table(m: pd.DataFrame, deductions: dict | None = None) -> pd.DataFrame:
    """deductions verilirse puan = maç puanı − silinen puan (resmi tablo)."""
    m = m.dropna(subset=["ev_gol", "dep_gol"])
    d = _long(m)
    t = _table(d)
    if deductions:
        t["puan"] = t["puan"] - t.index.map(lambda n: deductions.get(n, 0))

    def h2h_key(group: list[str]) -> dict[str, tuple]:
        sub = d[d.takim.isin(group) & d.rakip.isin(group)]
        s = sub.groupby("takim").agg(p=("p", "sum"), ag=("ag", "sum"), yg=("yg", "sum"))
        s = s.reindex(group, fill_value=0)
        return {k: (r.p, r.ag - r.yg, r.ag) for k, r in s.iterrows()}

    keys = {}
    for _, grp in t.groupby("puan"):
        names = list(grp.index)
        hk = h2h_key(names) if len(names) > 1 else {names[0]: (0, 0, 0)}
        for n in names:
            keys[n] = (t.at[n, "puan"], *hk[n], t.at[n, "averaj"], t.at[n, "atilan_gol"])
    order = sorted(keys, key=lambda n: (tuple(-x for x in keys[n]), n))
    t = t.loc[order]
    t["sira"] = range(1, len(t) + 1)
    return t.reset_index()
