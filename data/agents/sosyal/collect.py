import re,sys,subprocess,time,html,json,csv,urllib.parse,datetime
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
TODAY='2026-10-06'
def curl(u,extra=()):
    p=subprocess.run(['curl','-sL','-m','35','-A',UA,*extra,u],capture_output=True)
    time.sleep(1.3)
    return p.stdout.decode('utf8','ignore')
MON={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
def ig(h):
    t=curl(f'https://instastatistics.com/{h}')
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
    m=re.search(r'is (?:a |an )?([a-z ]*)Instagram account with ([0-9,]+) followers as of ([A-Z][a-z]+) (\d+), (\d{4})',t)
    if not m: return None
    d=f'{m.group(5)}-{MON[m.group(3)]:02d}-{int(m.group(4)):02d}'
    return int(m.group(2).replace(',','')),d,m.group(1).strip()
def fx(h):
    for i in range(5):
        t=curl(f'https://api.fxtwitter.com/{h}')
        try:
            u=json.loads(t)['user']; return u['followers'],u['screen_name'],u['name'],(u.get('verification') or {}).get('type')
        except Exception: time.sleep(4)
    return None
def conv(s):
    s=s.replace(',','')
    mult={'K':1e3,'M':1e6,'B':1e9}
    if s[-1] in mult: return int(round(float(s[:-1])*mult[s[-1]]))
    return int(float(s))
def fb(h):
    u='https://www.facebook.com/plugins/page.php?href='+urllib.parse.quote('https://www.facebook.com/'+h,safe='')+'&tabs&width=340&height=130&small_header=true&adapt_container_width=true&hide_cover=true&show_facepile=false'
    t=curl(u)
    f=re.search(r'([0-9.,]+[KMB]?) followers',t)
    names=re.findall(r'<a [^>]*href="https://www.facebook.com/[^"]*"[^>]*>([^<]{2,60})</a>',t)
    if not f: return None
    return conv(f.group(1)),f.group(1),(names[0] if names else ''),u
def tt(h):
    t=curl(f'https://www.tiktok.com/@{h}')
    m=re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',t,re.S)
    if not m: return None
    try:
        ui=json.loads(m.group(1))['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
        return ui['stats']['followerCount'],ui['user']['uniqueId'],ui['user']['nickname'],ui['user']['verified']
    except Exception: return None
def yt(path):
    t=curl(f'https://www.youtube.com/{path}',['-H','Accept-Language: en-US,en;q=0.9','-b','CONSENT=YES+1; SOCS=CAI'])
    s=re.findall(r'"content":"([0-9.,]+[KMB]?) subscribers"',t)
    if not s: s=re.findall(r'"subscriberCountText":\{"[^}]*?"content":"([0-9.,]+[KMB]?) subscribers',t)
    title=re.search(r'<meta property="og:title" content="([^"]*)"',t)
    can=re.search(r'"canonicalBaseUrl":"([^"]*)"',t)
    if not s: return None
    return conv(s[0]),s[0],html.unescape(title.group(1)) if title else '',can.group(1) if can else ''
def retry(f):
    def g(*a):
        for i in range(4):
            r=f(*a)
            if r: return r
            time.sleep(4)
        return None
    return g
ig,fb,tt,yt=retry(ig),retry(fb),retry(tt),retry(yt)
plan=json.load(open('plan.json'))
rows=[];log=[]
for club,spec in plan.items():
    for plat,cfg in spec.items():
        if cfg is None: continue
        if plat=='IG':
            r=ig(cfg['h'])
            if r: rows.append([club,'Instagram','@'+cfg['h'],r[0],r[2] and r[1],f'https://instastatistics.com/{cfg["h"]}',f'Instastatistics (3. taraf izleyici) sayfasındaki tam sayı; tarih = sitenin verdiği güncelleme tarihi. {r[2]} hesap. '+cfg.get('n','')]); 
            else: log.append((club,plat,'FAIL',cfg))
            if r: rows[-1][4]=r[1]
        elif plat in('X','X_EN'):
            r=fx(cfg['h'])
            if r: rows.append([club,'X' if plat=='X' else 'X_EN','@'+r[1],r[0],TODAY,f'https://api.fxtwitter.com/{cfg["h"]}',f'FxTwitter genel API (x.com profil verisi), tam sayı; profil adı "{r[2]}", doğrulama={r[3]}. '+cfg.get('n','')])
            else: log.append((club,plat,'FAIL',cfg))
        elif plat=='FB':
            r=fb(cfg['h'])
            if r: rows.append([club,'Facebook',cfg['h'],r[0],TODAY,r[3],f'Facebook sayfa eklentisi; YUVARLAK ("{r[1]} followers"), sayfa adı "{r[2]}". '+cfg.get('n','')])
            else: log.append((club,plat,'FAIL',cfg))
        elif plat=='TT':
            r=tt(cfg['h'])
            if r: rows.append([club,'TikTok','@'+r[1],r[0],TODAY,f'https://www.tiktok.com/@{cfg["h"]}',f'TikTok profil sayfası (followerCount; büyük hesaplarda 100 bin/1000 düzeyinde yuvarlak geliyor); ad "{r[2]}", doğrulanmış={r[3]}. '+cfg.get('n','')])
            else: log.append((club,plat,'FAIL',cfg))
        elif plat=='YT':
            r=yt(cfg['p'])
            if r: rows.append([club,'YouTube',r[3] or cfg['p'],r[0],TODAY,f'https://www.youtube.com/{cfg["p"]}',f'YouTube kanal sayfası; YUVARLAK ("{r[1]} subscribers"), kanal adı "{r[2]}". '+cfg.get('n','')])
            else: log.append((club,plat,'FAIL',cfg))
json.dump(rows,open('rows.json','w'),ensure_ascii=False,indent=0)
print(len(rows),'rows');print(log)
