# -*- coding: utf-8 -*-
"""测试 Semantic Scholar API 关键词搜索和期刊过滤能力"""
import urllib.request
import urllib.parse
import json
import ssl
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
ua = "ResearchHub/1.0 (mailto:research@example.com)"

# ===== S2: 关键词搜索 =====
print("=" * 60)
print("Semantic Scholar API: UAV 关键词搜索")
print("=" * 60)

query = urllib.parse.quote("UAV semantic communication cooperative")
url = (
    "https://api.semanticscholar.org/graph/v1/paper/search"
    f"?query={query}"
    "&limit=5"
    "&year=2025-2026"
    "&fields=title,authors,abstract,publicationDate,externalIds,venue,journal"
)
try:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        papers = data.get("data", [])
        total = data.get("total", 0)
        print(f"Total: {total}, Returned: {len(papers)}\n")
        for i, p in enumerate(papers):
            title = p.get("title", "")[:120]
            doi = p.get("externalIds", {}).get("DOI", "")
            arxiv_id = p.get("externalIds", {}).get("ArXiv", "")
            venue_info = p.get("venue", {}) or {}
            journal_info = p.get("journal", {}) or {}
            journal_name = journal_info.get("name", "") or venue_info.get("name", "Unknown")
            year = (p.get("publicationDate") or "")[:4]
            abstract = (p.get("abstract", "") or "")[:200]
            has_abs = "YES" if abstract else "NO "
            print(f"  [{i+1}] [{year}] {title}")
            print(f"      Venue: {journal_name}")
            print(f"      DOI: {doi} | arXiv: {arxiv_id}")
            print(f"      Abstract[{has_abs}]: {abstract}\n")
except Exception as e:
    print(f"[FAIL]: {e}")

# ===== S2: 按期刊名搜索 =====
print("=" * 60)
print("Semantic Scholar: 期刊名 + 关键词搜索")
print("=" * 60)

journal_searches = [
    "IEEE Transactions on Communications UAV drone",
    "IEEE Transactions on Wireless Communications drone",
    "IEEE Transactions on Vehicular Technology UAV",
    "IEEE Internet of Things Journal UAV communication",
]

for search_term in journal_searches:
    q = urllib.parse.quote(search_term)
    url2 = (
        "https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={q}"
        "&limit=2"
        "&year=2024-"
        "&fields=title,abstract,publicationDate,venue,externalIds"
    )
    try:
        req = urllib.request.Request(url2, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            papers = data.get("data", [])
            total = data.get("total", 0)
            print(f"\n  [{search_term[:50]}...]: total={total}")
            for p in papers[:1]:
                title = p.get("title", "")[:100]
                venue = ((p.get("journal") or {}).get("name", "") or (p.get("venue") or {}).get("name", ""))
                doi = p.get("externalIds", {}).get("DOI", "")
                abstract = (p.get("abstract", "") or "")[:120]
                print(f"    [{venue}] {title}")
                print(f"    DOI: {doi}")
                print(f"    Abstract: {abstract}")
    except Exception as e:
        print(f"  [FAIL]: {str(e)[:80]}")

print("\nDone.")
