"""arXiv API search for UAV multi-view detection papers"""
import json, os, time, random, urllib.parse, urllib.request, ssl
import xml.etree.ElementTree as ET

def arxiv_request(url, max_retries=3):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'ResearchHub/1.0'})
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                return resp.read().decode('utf-8')
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise

def parse_arxiv(xml_text):
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall('atom:entry', ns):
        t = entry.find('atom:title', ns)
        s = entry.find('atom:summary', ns)
        aid = entry.find('atom:id', ns)
        pub = entry.find('atom:published', ns)
        authors = [
            a.find('atom:name', ns).text
            for a in entry.findall('atom:author', ns)
            if a.find('atom:name', ns) is not None
        ]
        papers.append({
            'title': t.text.strip() if t is not None and t.text else '',
            'summary': s.text.strip()[:500] if s is not None and s.text else '',
            'arxiv_id': aid.text.strip().split('/')[-1] if aid is not None and aid.text else '',
            'published': pub.text.strip()[:10] if pub is not None and pub.text else '',
            'authors': '; '.join(authors[:5])
        })
    return papers

queries = [
    ('multi-view UAV object detection cross-view drone', 15),
    ('UAV object detection false positive confidence calibration', 15),
    ('cross-view object re-identification aerial drone', 15),
    ('cooperative perception multi-drone collaborative detection', 10),
    ('cross-drone object association multi-target tracking', 10),
    ('aerial object proposal quality verification detection', 10),
]

out_dir = 'metadata/ieee_uav_multiview_detection'
os.makedirs(out_dir, exist_ok=True)
all_papers = {}

for query, max_r in queries:
    encoded = urllib.parse.quote(query)
    url = (
        f'http://export.arxiv.org/api/query'
        f'?search_query=all:{encoded}'
        f'&start=0&max_results={max_r}&sortBy=relevance'
    )
    print(f'=== {query[:60]}... ===')
    try:
        xml_text = arxiv_request(url)
        papers = parse_arxiv(xml_text)
        for p in papers:
            if p['arxiv_id'] and p['arxiv_id'] not in all_papers:
                all_papers[p['arxiv_id']] = p
        print(f'  {len(papers)} results, total unique: {len(all_papers)}')
    except Exception as e:
        print(f'  Error: {str(e)[:80]}')
    time.sleep(random.uniform(4, 6))

arxiv_list = sorted(
    all_papers.values(),
    key=lambda x: x.get('published', ''),
    reverse=True
)
path = os.path.join(out_dir, 'arxiv_results.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(arxiv_list, f, indent=2, ensure_ascii=False)
print(f'\nSaved {len(arxiv_list)} arXiv papers to {path}')
for i, p in enumerate(arxiv_list[:25]):
    year = p.get('published', '')[:4]
    title = p.get('title', '')[:120]
    authors = p.get('authors', '')[:80]
    print(f'{i+1}. [{year}] {title}')
    print(f'   Authors: {authors}')
    print()
