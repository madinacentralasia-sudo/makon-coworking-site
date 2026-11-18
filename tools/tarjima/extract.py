import json, re, sys
from html.parser import HTMLParser
PAGES=['index.html','makon.html','galereya.html','azolik.html','rezidentlar.html','hayot.html','aloqa.html','rahmat.html']
ATTRS={'placeholder','alt','title','aria-label'}
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.out=[]; s.skip=0
    def handle_starttag(s,tag,attrs):
        if tag in('script','style'): s.skip+=1
        d=dict(attrs)
        for a,v in attrs:
            if a in ATTRS and v and v.strip(): s.out.append(v.strip())
        if tag=='meta' and d.get('name') in('description',) or d.get('property') in('og:title','og:description'):
            if d.get('content'): s.out.append(d['content'].strip())
    def handle_endtag(s,tag):
        if tag in('script','style'): s.skip-=1
    def handle_data(s,data):
        if s.skip: return
        t=re.sub(r'\s+',' ',data).strip()
        if t: s.out.append(t)
seen={}
for fn in PAGES:
    p=P(); p.feed(open(fn,encoding='utf-8').read())
    for t in p.out:
        seen.setdefault(t,[]).append(fn)
json.dump(list(seen.keys()),open('/home/claude/work/strings.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(seen))
