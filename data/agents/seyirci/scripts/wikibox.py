import re,sys
from bs4 import BeautifulSoup
from dateutil import parser as dp
def boxes(path):
    s=BeautifulSoup(open(path).read(),'lxml')
    out=[]
    for b in s.select('table.vevent, div.footballbox'):
        t=b.get_text(' ',strip=True)
        orgs=[x.get_text(' ',strip=True) for x in b.select('.fn.org')]
        if len(orgs)<2: 
            orgs=[x.get_text(' ',strip=True) for x in b.select('.fhome, .faway')]
        m=re.search(r'Attendance:?\s*([\d,\.]+)',t)
        d=re.search(r'(\d{1,2} [A-Z][a-z]+ \d{4})',t)
        sec=b.find_previous(['h2','h3','h4'])
        out.append(dict(date=dp.parse(d.group(1)).date().isoformat() if d else None,home=orgs[0] if orgs else None,away=orgs[1] if len(orgs)>1 else None,
                        att=int(m.group(1).replace(',','').replace('.','')) if m else None,section=sec.get_text(' ',strip=True) if sec else None))
    return out
if __name__=='__main__':
    for r in boxes(sys.argv[1]): print(r)
