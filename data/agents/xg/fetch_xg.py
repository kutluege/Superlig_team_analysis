#!/usr/bin/env python3
"""Resumable Sofascore xG fetcher. Usage: python3 fetch_xg.py [probe|fetch]
Caches raw JSON in cache/sofa/{id}.json; errors in fetch_errors.log.
Default: probe 25 random events for seasons <2022 (stop if no xG found), fetch all for seasons with xG."""
import json, os, sys, time, random
import pandas as pd, requests
ROOT = '/home/user/Superlig_team_analysis'
OUT = f'{ROOT}/data/agents/xg'; CACHE = f'{OUT}/cache/sofa'
os.makedirs(CACHE, exist_ok=True)
H = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
S = requests.Session(); S.headers.update(H)

def log(m):
    with open(f'{OUT}/fetch_errors.log', 'a') as f: f.write(f'{time.strftime("%F %T")} {m}\n')

def get(eid):
    p = f'{CACHE}/{eid}.json'
    if os.path.exists(p):
        return json.load(open(p))
    for a in range(3):
        try:
            r = S.get(f'https://api.sofascore.com/api/v1/event/{eid}/statistics', timeout=30)
            time.sleep(1.2)
            if r.status_code == 200:
                d = r.json(); json.dump(d, open(p, 'w')); return d
            if r.status_code == 404:
                d = {'statistics': [], 'http404': True}; json.dump(d, open(p, 'w')); return d
            log(f'{eid} HTTP {r.status_code}'); time.sleep(5 * (a + 1))
        except Exception as e:
            log(f'{eid} EXC {e}'); time.sleep(5)
    return None

def xg(d):
    if not d: return None
    for p in d.get('statistics', []):
        if p.get('period') == 'ALL':
            for g in p['groups']:
                for it in g['statisticsItems']:
                    if it.get('key') == 'expectedGoals':
                        return float(it['homeValue']), float(it['awayValue'])
    return None

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    s = pd.read_csv(f'{ROOT}/data/raw/sofascore_mac_seyirci.csv').dropna(subset=['sofascore_id'])
    s['sofascore_id'] = s.sofascore_id.astype(int)
    cov = {}
    for y, g in s.groupby('sezon_yil'):
        ids = list(g.sofascore_id)
        random.Random(7).shuffle(ids)
        n = sum(xg(get(i)) is not None for i in ids[:25])
        cov[y] = n; print('probe', y, n, '/25', flush=True)
    json.dump(cov, open(f'{OUT}/probe.json', 'w'))
    if mode == 'probe': return
    for y, g in s.groupby('sezon_yil'):
        if cov[y] == 0: continue
        for k, i in enumerate(g.sofascore_id):
            get(i)
            if k % 50 == 0: print('fetch', y, k, len(g), flush=True)
    print('done')

if __name__ == '__main__': main()
