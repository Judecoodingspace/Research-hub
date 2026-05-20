# -*- coding: utf-8 -*-
"""简易端到端测试：IEEE 订阅拉取 + 分级（单查询，长冷却）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ieee_subscriber import search_by_keyword, compute_relevance, load_config

config = load_config()

# 仅测试 1 个查询，用高延迟
query = "UAV semantic communication cooperative"
print(f"查询: {query}")
print("等待 15 秒 S2 冷却...")
import time
time.sleep(15)

papers = search_by_keyword(query, max_results=3, year="2026-")
print(f"\n拉取: {len(papers)} 篇")

for p in papers:
    relevance, cat, tags = compute_relevance(p, config)
    p["relevance"] = relevance
    p["category"] = cat
    title = p.get("title", "")[:100]
    doi = p.get("doi", "N/A")
    journal = p.get("journal_ref", "?")[:80]
    abstract = (p.get("summary", "") or "")[:120]
    print(f"\n  [{relevance}] {title}")
    print(f"    分类: {cat} | DOI: {doi}")
    print(f"    期刊: {journal}")
    print(f"    摘要: {abstract}")

print("\nDone.")
