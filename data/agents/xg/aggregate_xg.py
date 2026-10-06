#!/usr/bin/env python3
"""Aggregate cached Sofascore match xG + FotMob team-season xG into CSVs. Run after fetch_xg.py."""
import json, os, glob
import pandas as pd
ROOT = '/home/user/Superlig_team_analysis'; OUT = f'{ROOT}/data/agents/xg'
FMMAP = {'Başakşehir': 'İstanbul Başakşehir', 'Rizespor': 'Çaykur Rizespor', 'Istanbulspor': 'İstanbulspor',
         'Erzurumspor FK': 'Erzurumspor', 'Ankaragücü': 'Ankaragücü'}
SEASONS = [f'{y}-{str(y+1)[2:]}' for y in range(2016, 2026)]

m = pd.read_csv(f'{ROOT}/data/matches.csv')
ts = pd.read_csv(f'{ROOT}/data/team_season.csv'); ts = ts[ts.ligde.astype(str) == 'True']
s = pd.read_csv(f'{ROOT}/data/raw/sofascore_mac_seyirci.csv').dropna(subset=['sofascore_id'])
s['sezon'] = s.sezon_yil.map(lambda y: f'{y}-{str(y+1)[2:]}'); s['sofascore_id'] = s.sofascore_id.astype(int)

def sofa_xg(eid):
    p = f'{OUT}/cache/sofa/{eid}.json'
    if not os.path.exists(p): return None
    for per in json.load(open(p)).get('statistics', []):
        if per.get('period') == 'ALL':
            for g in per['groups']:
                for it in g['statisticsItems']:
                    if it.get('key') == 'expectedGoals': return float(it['homeValue']), float(it['awayValue'])
    return None

# ---- match level (Sofascore)
k = m.merge(s[['sezon', 'ev', 'deplasman', 'sofascore_id']], on=['sezon', 'ev', 'deplasman'], how='left')
rows = []
for r in k.itertuples():
    if pd.isna(r.sofascore_id): continue
    x = sofa_xg(int(r.sofascore_id))
    if x: rows.append((r.sezon, r.tarih, r.ev, r.deplasman, x[0], x[1], 'sofascore'))
xm = pd.DataFrame(rows, columns=['sezon', 'tarih', 'ev', 'deplasman', 'ev_xg', 'dep_xg', 'kaynak']).sort_values(['tarih', 'ev'])
xm.to_csv(f'{OUT}/xg_mac.csv', index=False, encoding='utf-8')

# ---- sofascore season sums
h = xm.rename(columns={'ev': 'takim', 'ev_xg': 'f', 'dep_xg': 'a'})[['sezon', 'takim', 'f', 'a']]
a = xm.rename(columns={'deplasman': 'takim', 'dep_xg': 'f', 'ev_xg': 'a'})[['sezon', 'takim', 'f', 'a']]
sf = pd.concat([h, a]).groupby(['sezon', 'takim']).agg(xg=('f', 'sum'), xga=('a', 'sum'), n=('f', 'size')).reset_index()
sf = sf.set_index(['sezon', 'takim'])

# ---- fotmob season totals
fm = {}
for sez in SEASONS:
    pf, pa = f'{OUT}/cache/fotmob/{sez}_expected_goals_team.json', f'{OUT}/cache/fotmob/{sez}_expected_goals_conceded_team.json'
    if not (os.path.exists(pf) and os.path.exists(pa)): continue
    F = {x['ParticipantName']: x for x in json.load(open(pf))['TopLists'][0]['StatList']}
    A = {x['ParticipantName']: x for x in json.load(open(pa))['TopLists'][0]['StatList']}
    for n, x in F.items():
        t = FMMAP.get(n, n)
        if n in A: fm[(sez, t)] = dict(xg=x['StatValue'], xga=A[n]['StatValue'], n=min(x['StatValueCount'], A[n]['StatValueCount']), mp=x['MatchesPlayed'])
pd.DataFrame([dict(sezon=s_, takim=t, **v) for (s_, t), v in fm.items()]).to_csv(f'{OUT}/fotmob_sezon_ham.csv', index=False, encoding='utf-8')

# ---- season table
tm = pd.concat([m.rename(columns={'ev': 'takim'})[['sezon', 'takim']], m.rename(columns={'deplasman': 'takim'})[['sezon', 'takim']]]).groupby(['sezon', 'takim']).size()
out, cross = [], []
for r in ts.itertuples():
    key = (r.sezon, r.takim); tot = int(tm.get(key, 0)); note = []
    S = sf.loc[key] if key in sf.index else None; F = fm.get(key)
    FULL = F is not None and F['n'] >= 0.8 * F['mp']   # FotMob usable only when it covers most matches
    if S is not None:
        xg, xga, n, src = S.xg, S.xga, int(S.n), 'sofascore'
        if n < tot: note.append(f'{tot-n} mac icin xG yok (Sofascore)')
        if F is not None and FULL:
            cross.append((r.sezon, r.takim, n, xg, xga, F['n'], F['xg'], F['xga']))
            src = 'sofascore (fotmob capraz kontrol)'
    elif F is not None and FULL:
        xg, xga, n, src = F['xg'], F['xga'], int(F['n']), 'fotmob'
        note.append('yalniz FotMob sezon toplami (mac bazli yok)')
        if n < tot: note.append(f'FotMob {n}/{tot} mac')
    else:
        xg = xga = None; n = 0; src = ''
        note.append('xG kaynagi yok' + (f'; FotMob yalniz {F["n"]}/{F["mp"]} mac (kullanilmadi)' if F else ''))
    out.append(dict(takim=r.takim, sezon=r.sezon, mac_kapsami=n, toplam_mac=tot,
                    xg=None if xg is None else round(xg, 2), xga=None if xga is None else round(xga, 2),
                    xg_mac_basi=None if not n else round(xg / n, 3), xga_mac_basi=None if not n else round(xga / n, 3),
                    kaynak=src, **{'not': '; '.join(note)}))
sez = pd.DataFrame(out).sort_values(['sezon', 'takim'])
sez.to_csv(f'{OUT}/xg_sezonluk.csv', index=False, encoding='utf-8')
cdf = pd.DataFrame(cross, columns=['sezon', 'takim', 'sofa_mac', 'sofa_xg', 'sofa_xga', 'fotmob_mac', 'fotmob_xg', 'fotmob_xga'])
cdf['fark_xg'] = (cdf.sofa_xg - cdf.fotmob_xg).round(2); cdf['fark_xga'] = (cdf.sofa_xga - cdf.fotmob_xga).round(2)
cdf.to_csv(f'{OUT}/capraz_kontrol.csv', index=False, encoding='utf-8')

# ---- 10-year per team
d = sez[sez.mac_kapsami > 0]; rows = []
for t, g in sez.groupby('takim'):
    gd = g[g.mac_kapsami > 0]
    if gd.empty:
        rows.append(dict(takim=t, sezon_sayisi=0, mac=0, kapsanan_sezonlar='', **{'not': 'xG verisi yok'})); continue
    mac = int(gd.mac_kapsami.sum()); xg = gd.xg.sum(); xga = gd.xga.sum()
    miss = g[g.mac_kapsami == 0].sezon.tolist(); nt = []
    if miss: nt.append('xG yok: ' + ','.join(miss))
    if (gd.mac_kapsami < gd.toplam_mac).any(): nt.append('bazi sezonlarda eksik mac')
    rows.append(dict(takim=t, sezon_sayisi=len(gd), mac=mac, xg_toplam=round(xg, 2), xga_toplam=round(xga, 2),
                     xg_mac_basi=round(xg / mac, 3), xga_mac_basi=round(xga / mac, 3), xg_fark_mac_basi=round((xg - xga) / mac, 3),
                     kapsanan_sezonlar=','.join(gd.sezon), **{'not': '; '.join(nt)}))
cols = ['takim', 'sezon_sayisi', 'mac', 'xg_toplam', 'xga_toplam', 'xg_mac_basi', 'xga_mac_basi', 'xg_fark_mac_basi', 'kapsanan_sezonlar', 'not']
pd.DataFrame(rows)[cols].sort_values('xg_mac_basi', ascending=False).to_csv(f'{OUT}/xg_10yil.csv', index=False, encoding='utf-8')
print('ok', len(xm), len(sez), len(cdf))
