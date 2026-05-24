"""
Multi-keyword search for UAV multi-view detection papers
via Semantic Scholar API (IEEE/Journal coverage) + arXiv API
"""
import sys
sys.path.insert(0, 'arxiv_subscriber')
from ieee_subscriber import search_by_keyword
import json, os, time, random, urllib.parse, urllib.request, ssl
import xml.etree.ElementTree as ET

OUTPUT_DIR = 'metadata/ieee_uav_multiview_detection'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================
# Part 1: Semantic Scholar keyword search
# =============================================
json_path = f'{OUTPUT_DIR}/search_results.json'
existing = {}
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        for r in json.load(f):
            existing[r.get('dedup_id', r.get('title',''))] = r
    print(f'Loaded {len(existing)} existing S2 results')

kw_queries = [
    ('A1_multi_view', 'multi-view UAV object detection aerial imagery'),
    ('A2_cross_view', 'cross-view drone vehicle detection collaborative'),
    ('A3_cooperative', 'cooperative perception multi-UAV detection fusion'),
    ('B1_false_positive', 'false positive suppression UAV aerial detection'),
    ('B2_proposal', 'object proposal quality confidence drone detection'),
    ('B3_calibration', 'detection confidence calibration unmanned aerial'),
    ('C1_reid', 'cross-view object re-identification UAV drone'),
    ('C2_mtt', 'multi-target tracking drone cross-camera association'),
    ('C3_cross_drone', 'cross-drone object association tracking'),
    ('D_tgrs', 'UAV object detection multi-view remote sensing'),
    ('D_drone_fp', 'drone detection false positive remote sensing'),
]

new_total = 0
for tag, query in kw_queries:
    print(f'\n=== {tag}: {query} ===')
    try:
        results = search_by_keyword(query, max_results=15)
        for r in results:
            kid = r.get('dedup_id', r.get('title',''))
            if kid not in existing:
                existing[kid] = r
                new_total += 1
        print(f'  Fetched {len(results)}, new total so far: {len(existing)}')
        time.sleep(random.uniform(3, 6))
    except Exception as e:
        print(f'  Error: {str(e)[:100]}')

all_s2 = sorted(existing.values(), key=lambda x: x.get('year',''), reverse=True)
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_s2, f, indent=2, ensure_ascii=False)
print(f'\nS2 done: {len(all_s2)} unique papers saved to {json_path}')

# =============================================
# Part 2: arXiv API search
# =============================================
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

def parse_arxiv_xml(xml_text):
    ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall('atom:entry', ns):
        title_el = entry.find('atom:title', ns)
        summary_el = entry.find('atom:summary', ns)
        id_el = entry.find('atom:id', ns)
        pub_el = entry.find('atom:published', ns)
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns) if a.find('atom:name', ns) is not None]
        papers.append({
            'title': title_el.text.strip() if title_el is not None and title_el.text else '',
            'summary': summary_el.text.strip() if summary_el is not None and summary_el.text else '',
            'arxiv_id': id_el.text.strip().split('/')[-1] if id_el is not None and id_el.text else '',
            'published': pub_el.text.strip()[:10] if pub_el is not None and pub_el.text else '',
            'authors': '; '.join(authors[:5])
        })
    return papers

arxiv_queries = [
    'cat:cs.CV AND (UAV object detection false positive confidence)',
    'cat:cs.CV AND (multi-view drone vehicle detection cross-view)',
    'cat:cs.CV AND (aerial object re-identification cross-camera drone)',
    'cat:cs.CV AND (collaborative perception drone cooperative detection)',
    'cat:cs.CV AND (cross-drone object association multi-target tracking)',
]

arxiv_papers = {}
for q in arxiv_queries:
    encoded = urllib.parse.quote(q)
    url = f'http://export.arxiv.org/api/query?search_query={encoded}&start=0&max_results=15&sortBy=relevance'
    print(f'\n=== arXiv: {q[:70]}... ===')
    try:
        xml_text = arxiv_request(url)
        papers = parse_arxiv_xml(xml_text)
        for p in papers:
            aid = p['arxiv_id']
            if aid and aid not in arxiv_papers:
                arxiv_papers[aid] = p
        print(f'  {len(papers)} results')
    except Exception as e:
        print(f'  Error: {str(e)[:100]}')
    time.sleep(random.uniform(3, 5))

arxiv_list = sorted(arxiv_papers.values(), key=lambda x: x.get('published',''), reverse=True)
arxiv_path = f'{OUTPUT_DIR}/arxiv_results.json'
with open(arxiv_path, 'w', encoding='utf-8') as f:
    json.dump(arxiv_list, f, indent=2, ensure_ascii=False)
print(f'\narXiv done: {len(arxiv_list)} unique papers saved to {arxiv_path}')

# =============================================
# Summary
# =============================================
print(f'\n=== SUMMARY ===')
print(f'S2/Journal papers: {len(all_s2)} -> {json_path}')
print(f'arXiv papers: {len(arxiv_list)} -> {arxiv_path}')
print(f'Combined unique: {len(all_s2) + len(arxiv_list)}')

# Print top papers from each source
print('\n--- Top S2/Journal Papers ---')
for i, r in enumerate(all_s2[:20]):
    title = r.get('title','')[:100]
    journal = r.get('journal_ref','')[:50]
    year = r.get('year','')
    print(f'{i+1}. [{year}] {title}')
    if journal: print(f'   Journal: {journal}')

print('\n--- Top arXiv Papers ---')
for i, p in enumerate(arxiv_list[:15]):
    title = p.get('title','')[:100]
    year = p.get('published','')[:4]
    print(f'{i+1}. [{year}] {title}')
    print(f'   Authors: {p.get("authors","")[:80]}')
