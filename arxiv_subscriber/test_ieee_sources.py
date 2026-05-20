# -*- coding: utf-8 -*-
"""测试 IEEE 论文元数据获取方案：CrossRef API + Semantic Scholar API"""
import urllib.request
import json
import ssl
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
ua = "ResearchHub/1.0 (mailto:research@example.com)"

# ===== CrossRef API: 按 ISSN 获取最近论文 =====
print("=" * 60)
print("CrossRef API: IEEE 期刊最近论文（含摘要检查）")
print("=" * 60)

journals = [
    ("TCOM", "0090-6778"),
    ("TWC", "1536-1276"),
    ("TVT", "0018-9545"),
    ("IoT-J", "2327-4662"),
    ("JSAC", "0733-8716"),
    ("TCCN", "2332-7731"),
    ("TMC", "1536-1233"),
    ("TSP", "1053-587X"),
    ("COMML", "1089-7798"),
    ("TITS", "1524-9050"),
]

for name, issn in journals:
    url = f"https://api.crossref.org/works?filter=issn:{issn},from-pub-date:2026-04-01&rows=1&sort=published&order=desc"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("message", {}).get("items", [])
            total = data.get("message", {}).get("total-results", 0)
            print(f"\n[{name}] ISSN={issn} | 2026年4月后: {total}篇")
            for item in items[:1]:
                title = item.get("title", [""])[0][:100] if item.get("title") else "No title"
                doi = item.get("DOI", "")
                date_parts = item.get("published-print", {}).get("date-parts", [[0]])[0]
                abstract = item.get("abstract", "")
                has_abs = "YES" if abstract else "NO "
                snippet = abstract[:150] if abstract else "(无摘要)"
                print(f"  标题: {title}")
                print(f"  DOI: {doi} | 日期: {date_parts}")
                print(f"  有摘要: {has_abs} | {snippet}")
    except Exception as e:
        print(f"\n[{name}] FAIL: {str(e)[:80]}")

# ===== Semantic Scholar API =====
print("\n" + "=" * 60)
print("Semantic Scholar API: UAV关键词搜索")
print("=" * 60)

ss_url = (
    "https://api.semanticscholar.org/graph/v1/paper/search"
    "?query=UAV+semantic+communication+cooperative"
    "&limit=3&fieldsOfStudy=Computer Science,Engineering"
    "&year=2025-"
    "&fields=title,authors,abstract,publicationDate,externalIds,venue"
)
try:
    req = urllib.request.Request(ss_url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        papers = data.get("data", [])
        total = data.get("total", 0)
        print(f"搜索结果: {total} 篇")
        for p in papers[:3]:
            title = p.get("title", "")[:100]
            doi = p.get("externalIds", {}).get("DOI", "N/A")
            venue = p.get("venue", {}) if p.get("venue") else ""
            venue_name = venue.get("name", "") if venue else ""
            abstract = (p.get("abstract", "") or "")[:150]
            arxiv = p.get("externalIds", {}).get("ArXiv", "")
            print(f"\n  [{venue_name}] {title}")
            print(f"  DOI: {doi} | arXiv: {arxiv}")
            print(f"  摘要: {abstract}")
except Exception as e:
    print(f"FAIL: {str(e)[:100]}")

# ===== CrossRef 搜索 (直接按关键词) =====
print("\n" + "=" * 60)
print("CrossRef API: 直接按关键词搜索 (UAV semantic)")
print("=" * 60)

cr_search_url = (
    "https://api.crossref.org/works"
    "?query=UAV+semantic+communication+cooperative"
    "&filter=from-pub-date:2025-01-01"
    "&rows=3&sort=published&order=desc"
)
try:
    req = urllib.request.Request(cr_search_url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        items = data.get("message", {}).get("items", [])
        total = data.get("message", {}).get("total-results", 0)
        print(f"搜索结果: {total} 篇")
        for item in items[:3]:
            title = item.get("title", [""])[0][:100] if item.get("title") else "No title"
            doi = item.get("DOI", "")
            publisher = item.get("publisher", "")
            date_parts = item.get("published-print", {}).get("date-parts", [[0]])[0]
            abstract = (item.get("abstract", "") or "")[:150]
            print(f"\n  [{publisher}] {title}")
            print(f"  DOI: {doi} | 日期: {date_parts}")
            print(f"  摘要: {abstract}")
except Exception as e:
    print(f"FAIL: {str(e)[:80]}")

print("\nDone.")
