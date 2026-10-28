import datetime as dt, email.utils, json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from difflib import SequenceMatcher

ROOT=Path(__file__).parent
NOW=dt.datetime.now(dt.timezone.utc)
SOURCES={
 'lebensmittelzeitung.net':('Lebensmittel Zeitung',10), 'stores-shops.de':('stores+shops',10),
 'ehi.org':('EHI',9),'einzelhandel.de':('HDE',9),'lebensmittelpraxis.de':('Lebensmittel Praxis',8),
 'etailment.de':('etailment',8),'internetworld.de':('INTERNET WORLD',8),
 'horizont.net':('HORIZONT',7),'t3n.de':('t3n',7),'handelsblatt.com':('Handelsblatt',7),
 'tagesschau.de':('Tagesschau',6),'wiwo.de':('WirtschaftsWoche',6),'retail-news.de':('Retail News',7)
}
TOPICS={
 'KI & Technologie':['künstliche intelligenz','ki ','ki-','ai ','agentic','automatisierung','robotik','self-checkout','computer vision','digitalisierung','technologie','smart store','autonom'],
 'Handelsstrategie':['einzelhandel','handelskonzern','filial','expansion','insolvenz','übernahme','fusion','strategie','restrukturierung','umsatz','geschäftsjahr','marktanteil'],
 'Logistik':['logistik','supply chain','lager','distribution','lieferkette','retouren','fulfillment','transport'],
 'Konsumenten':['konsum','verbraucher','kunden','kaufverhalten','nachfrage','preisbewusst','loyalität','markentreue'],
 'E-Commerce':['onlinehandel','e-commerce','marktplatz','omnichannel','plattform','quick commerce']
}
QUERIES=['Einzelhandel Deutschland when:7d','Lebensmittelhandel Deutschland when:7d','Handel KI Automatisierung Deutschland when:7d','Handelslogistik Deutschland when:7d','E-Commerce Handel Deutschland when:7d','Handelsunternehmen Filialen Deutschland when:7d']
for domain in SOURCES:
 QUERIES.append(f'site:{domain} (Handel OR Einzelhandel OR Retail) when:7d')

def fetch(q):
 url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q,'hl':'de','gl':'DE','ceid':'DE:de'})
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 RetailRadar/1.0'})
 with urllib.request.urlopen(req,timeout=20) as response: return response.read()

def norm(t):
 t=re.sub(r'[^\wäöüß]+',' ',t.casefold())
 return re.sub(r'\s+',' ',t).strip()

def parse(raw):
 root=ET.fromstring(raw)
 for it in root.findall('.//item'):
  title=it.findtext('title','').strip(); link=it.findtext('link','').strip()
  source_node=it.find('source'); source=(source_node.text or '').strip() if source_node is not None else ''
  source_url=source_node.attrib.get('url','') if source_node is not None else ''
  try: published=email.utils.parsedate_to_datetime(it.findtext('pubDate')).astimezone(dt.timezone.utc)
  except Exception: continue
  if not title or not link or not (NOW-dt.timedelta(days=7)<=published<=NOW+dt.timedelta(hours=2)): continue
  if source and title.endswith(' - '+source): title=title[:-(len(source)+3)]
  yield dict(title=title,url=link,source=source or 'Google News',source_url=source_url,published=published)

def rank(a):
  txt=' '+norm(a['title'])+' '; cats=[]; hits=0
  for cat,keys in TOPICS.items():
   n=sum(1 for k in keys if k in txt)
   if n: cats.append((cat,n)); hits+=min(n,3)
  if not cats:return None
  domain=urllib.parse.urlparse(a['source_url']).netloc.lower().removeprefix('www.')
  source_weight=next((v[1] for k,v in SOURCES.items() if domain==k or domain.endswith('.'+k)),4)
  age=(NOW-a['published']).total_seconds()/86400
  topical=min(45,18+hits*6)
  source_score=source_weight*2
  freshness=round(15*(1-age/7))
  impact=min(20,5+5*sum(k in txt for k in ['insolvenz','übernahme','milliard','bundesweit','gesetz','regulierung','marktanteil','restrukturierung','investition','filialschließung']))
  a.update(score=min(100,topical+source_score+freshness+impact),category=max(cats,key=lambda x:x[1])[0],score_detail={'Thema':topical,'Quelle':source_score,'Aktualität':freshness,'Tragweite (Schlüsselwörter)':impact})
  return a

def main():
  found=[]; errors=[]
  for q in QUERIES:
   try:
    for item in parse(fetch(q)):
     item=rank(item)
     if item:found.append(item)
   except Exception as exc:errors.append(f'{q}: {type(exc).__name__}: {exc}')
  if not found:raise RuntimeError('Keine Meldungen abrufbar. Vorhandene Ausgabe bleibt erhalten. '+str(errors[:3]))
  found.sort(key=lambda x:(-x['score'],-x['published'].timestamp()))
  unique=[]; seen=set()
  for item in found:
   key=norm(item['title'])
   if key in seen or any(SequenceMatcher(None,key,norm(old['title'])).ratio()>.84 for old in unique):continue
   seen.add(key);unique.append(item)
   if len(unique)>=10:break
  out={'generated_at':NOW.isoformat(),'window_days':7,'candidate_count':len(found),'errors_count':len(errors),'articles':[]}
  for a in unique:
   a['published']=a['published'].isoformat()
   out['articles'].append(a)
  target=ROOT/'site'/'news.json';target.parent.mkdir(exist_ok=True)
  target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
  print(f'{len(unique)} Nachrichten aus {len(found)} Kandidaten, {len(errors)} Feed-Fehler')
if __name__=='__main__':main()
