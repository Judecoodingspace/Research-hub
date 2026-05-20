"""Quick check of high relevance papers from today's arXiv fetch"""
import csv

path = r'D:\Research-hub\metadata\2026-05-18_arxiv_daily.csv'
with open(path, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

high = [r for r in rows if 'high' in r.get('Extra', '').lower()]
med = [r for r in rows if 'medium' in r.get('Extra', '').lower()]

print(f"Total: {len(rows)}, High: {len(high)}, Medium: {len(med)}")
print()

if high:
    print("=== HIGH RELEVANCE ===")
    for r in high:
        title = r.get('Title', '')[:120]
        arxiv_id = r.get('ArXiv ID', '')
        tags = r.get('Manual Tags', '')[:60]
        print(f"  [{tags}]")
        print(f"  {title}")
        print(f"  arXiv: {arxiv_id}")
        print()

print("=== MEDIUM (first 20) ===")
for r in med[:20]:
    title = r.get('Title', '')[:100]
    arxiv_id = r.get('ArXiv ID', '')
    tags = r.get('Manual Tags', '')[:40]
    print(f"  [{tags}] {arxiv_id}")
    print(f"    {title}...")
    print()
