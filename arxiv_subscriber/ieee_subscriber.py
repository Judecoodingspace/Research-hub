# -*- coding: utf-8 -*-
"""
IEEE / 闭源期刊论文订阅器
===========================
数据源：Semantic Scholar API (免费、无需 API Key)
备选：CrossRef API (DOI 补充检索)

原理：
1. IEEE RSS feed 已封闭 (HTTP 404/418)，CrossRef 不提供摘要
2. Semantic Scholar API 支持：关键词搜索 + 期刊过滤 + 摘要返回
3. 拉取后复用 fetcher.py 的 compute_relevance() 做关键词分级
4. 输出标准化元数据 CSV，与 arXiv 订阅共用 papercard 生成管道

依赖：pip install requests (标准库也可，requests 更友好)
"""

import json
import os
import sys
import time
import random
import urllib.request
import urllib.parse
import urllib.error
import ssl
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Set

# 设置 stdout 为 UTF-8 编码
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# =============================================
# 路径与配置
# =============================================

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_config() -> Dict:
    import yaml
    config_path = get_project_root() / "arxiv_subscriber" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# =============================================
# 去重管理（与 arXiv 共用 processed_ids.json）
# =============================================

def load_processed_ids() -> Set[str]:
    config = load_config()
    id_path = get_project_root() / config["dedup"]["id_store"]
    if not id_path.exists():
        return set()
    try:
        with open(id_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return set(data.get("processed_ids", []))
    except (json.JSONDecodeError, Exception):
        return set()


def save_processed_ids(ids: Set[str]):
    config = load_config()
    id_path = get_project_root() / config["dedup"]["id_store"]
    id_path.parent.mkdir(parents=True, exist_ok=True)
    with open(id_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "last_updated": datetime.now().isoformat(),
                "total_processed": len(ids),
                "processed_ids": sorted(list(ids)),
            },
            f,
            indent=2,
        )


# =============================================
# Semantic Scholar API 客户端
# =============================================

S2_API_BASE = "https://api.semanticscholar.org/graph/v1"

# 创建 SSL 上下文（忽略证书验证，仅限内网/测试环境）
def _create_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _s2_request(url: str, max_retries: int = 5, delay: float = 3.0) -> dict:
    """
    发送 Semantic Scholar API 请求，处理限流和重试。
    S2 API 免费但有限流（HTTP 429）。策略：
    - 首次请求等待 delay+5 秒（强制冷却）
    - HTTP 429: 等待 Retry-After（默认 60-120s），指数退避
    """
    last_error = None
    
    # 强制冷却：请求前至少等待 delay+5 秒
    cooldown = max(delay + 5, 10) + random.uniform(1, 5)
    time.sleep(cooldown)
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ResearchHub/1.0 (mailto:research@example.com)"},
            )
            with urllib.request.urlopen(req, timeout=30, context=_create_ssl_context()) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = e.headers.get("Retry-After", "60")
                try:
                    wait = int(retry_after)
                except ValueError:
                    wait = 60
                # 指数退避 + 随机抖动
                wait = max(wait, 30 * (2 ** attempt)) + random.uniform(5, 15)
                wait = min(wait, 300)  # 最多 5 分钟
                print(f"      ⚠️ S2 429 (attempt {attempt+1}/{max_retries}), wait {wait:.0f}s...")
                time.sleep(wait)
                last_error = e
            elif e.code == 403:
                print(f"      ❌ S2 403 Forbidden — 可能需要更换 IP")
                raise
            else:
                raise
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 30 * (2 ** attempt) + random.uniform(1, 10)
                print(f"      ⚠️ S2 请求失败: {e}, {wait:.0f}s 后重试...")
                time.sleep(wait)

    raise last_error or RuntimeError(f"S2 request failed after {max_retries} retries: {url}")


# =============================================
# 方案A：关键词搜索
# =============================================

def search_by_keyword(query: str, max_results: int = 50, year: str = "2025-") -> List[Dict]:
    """
    通过 Semantic Scholar 关键词搜索论文。
    
    参数:
        query: 自然语言查询词
        max_results: 最大返回数 (S2 limit=100)
        year: 年份范围，如 "2025-" 或 "2025-2026"
    
    返回: 标准化元数据列表
    """
    encoded_query = urllib.parse.quote(query)
    url = (
        f"{S2_API_BASE}/paper/search"
        f"?query={encoded_query}"
        f"&limit={max_results}"
        f"&year={year}"
        f"&fields=title,authors,abstract,publicationDate,externalIds,venue,journal,publicationTypes"
    )
    
    data = _s2_request(url)
    papers = data.get("data", [])
    total = data.get("total", 0)
    
    results = []
    for p in papers:
        paper = _normalize_s2_paper(p, query)
        if paper:
            results.append(paper)
    
    print(f"   S2 关键词搜索: '{query[:50]}...' -> {len(results)}/{total} 篇")
    return results


def _normalize_s2_paper(p: dict, source_query: str = "") -> Optional[Dict]:
    """将 Semantic Scholar 论文数据标准化为项目元数据格式"""
    title = p.get("title", "")
    if not title:
        return None
    
    # 论文唯一标识
    paper_id = p.get("paperId", "")
    external_ids = p.get("externalIds", {}) or {}
    doi = external_ids.get("DOI", "")
    arxiv_id = external_ids.get("ArXiv", "")
    
    # 构建唯一 ID（用于去重）：优先用 DOI，其次 paperId
    dedup_id = f"doi:{doi}" if doi else f"s2:{paper_id}"
    
    # 作者
    authors_list = p.get("authors", [])
    authors_str = "; ".join([a.get("name", "") for a in authors_list if a.get("name")])
    first_author = authors_list[0].get("name", "Unknown") if authors_list else "Unknown"
    first_author_lastname = first_author.split()[-1] if first_author else "Unknown"
    
    # 日期
    pub_date = p.get("publicationDate", "")
    year = pub_date[:4] if pub_date else ""
    
    # 期刊/会议
    journal_info = p.get("journal", {}) or {}
    venue_info = p.get("venue", {}) or {}
    journal_name = journal_info.get("name", "") or venue_info.get("name", "") or venue_info.get("text", "") or "Unknown"
    
    # 摘要
    abstract = p.get("abstract", "") or ""
    
    # 出版类型
    pub_types = p.get("publicationTypes", []) or []
    is_journal = "JournalArticle" in pub_types
    
    # arXiv URL（如果有 preprint）
    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
    
    # 论文 URL：优先 arXiv，否则用 DOI
    if arxiv_url:
        paper_url = arxiv_url
    elif doi:
        paper_url = f"https://doi.org/{doi}"
    else:
        paper_url = f"https://www.semanticscholar.org/paper/{paper_id}"
    
    return {
        # 唯一标识
        "dedup_id": dedup_id,
        "paper_id": paper_id,
        "doi": doi,
        "arxiv_id": arxiv_id,
        
        # 基础元数据
        "title": title.strip().replace("\n", " "),
        "authors": authors_str[:300],
        "first_author": first_author,
        "first_author_lastname": first_author_lastname,
        "summary": abstract.strip().replace("\n", " ")[:1000],
        "published_date": pub_date,
        "year": year,
        
        # 来源
        "source": "Semantic Scholar",
        "journal_ref": journal_name,
        "is_journal": is_journal,
        "publication_types": "; ".join(pub_types),
        
        # URL
        "url": paper_url,
        "arxiv_url": arxiv_url,
        
        # 原始来源查询（用于 traceback）
        "source_query": source_query,
    }


# =============================================
# 方案B：按期刊 ISSN + 关键词搜索
# =============================================

def search_by_journal(journal_name: str, issn: str, keyword: str, max_results: int = 30) -> List[Dict]:
    """
    通过 Semantic Scholar 在特定期刊内按关键词搜索。
    
    S2 API 不直接支持 ISSN 过滤，策略：
    1. 用期刊名 + 关键词拼成查询
    2. 在结果中二次过滤 journal name
    """
    # 拼合查询：期刊名 + 关键词
    full_query = f'"{journal_name}" {keyword}'
    encoded_query = urllib.parse.quote(full_query)
    
    url = (
        f"{S2_API_BASE}/paper/search"
        f"?query={encoded_query}"
        f"&limit={max_results}"
        f"&year=2024-"
        f"&fields=title,authors,abstract,publicationDate,externalIds,venue,journal,publicationTypes"
    )
    
    data = _s2_request(url)
    papers = data.get("data", [])
    total = data.get("total", 0)
    
    results = []
    for p in papers:
        paper = _normalize_s2_paper(p, source_query=f"journal:{journal_name}")
        if not paper:
            continue
        
        # 二次过滤：确认期刊名匹配
        jref = paper.get("journal_ref", "").lower()
        jname_lower = journal_name.lower()
        # 模糊匹配：期刊名包含在 journal_ref 中
        if jname_lower in jref or any(
            word in jref for word in jname_lower.split() if len(word) > 3
        ):
            results.append(paper)
    
    print(f"   S2 期刊搜索: '{journal_name[:40]}' + '{keyword[:30]}...' -> {len(results)}/{total} 篇")
    return results


# =============================================
# 方案C：CrossRef DOI 补充检索（获取摘要）
# =============================================

CROSSREF_API_BASE = "https://api.crossref.org/works"


def _crossref_request(url: str, max_retries: int = 3) -> dict:
    """发送 CrossRef API 请求"""
    last_error = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ResearchHub/1.0 (mailto:research@example.com)"},
            )
            with urllib.request.urlopen(req, timeout=20, context=_create_ssl_context()) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 10 * (attempt + 1)
                print(f"      ⚠️ CrossRef HTTP 429, 等待 {wait}s...")
                time.sleep(wait)
                last_error = e
            else:
                raise
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(5)
    
    raise last_error or RuntimeError(f"CrossRef request failed: {url}")


def enrich_with_crossref(papers: List[Dict]) -> List[Dict]:
    """
    对缺少摘要的论文，通过 CrossRef API 按 DOI 补充摘要。
    注意：CrossRef 大多不提供摘要（IEEE 政策），此方案仅作为最后补漏。
    """
    enriched = []
    for paper in papers:
        if paper.get("summary") and len(paper["summary"]) > 50:
            enriched.append(paper)
            continue
        
        doi = paper.get("doi", "")
        if not doi:
            enriched.append(paper)
            continue
        
        # 通过 DOI 查询 CrossRef
        url = f"{CROSSREF_API_BASE}/{urllib.parse.quote(doi)}"
        try:
            data = _crossref_request(url)
            message = data.get("message", {})
            crossref_abstract = message.get("abstract", "")
            if crossref_abstract:
                paper["summary"] = crossref_abstract.strip().replace("\n", " ")[:1000]
                paper["summary_source"] = "CrossRef"
        except Exception:
            pass
        
        enriched.append(paper)
    
    return enriched


# =============================================
# 相关性分级（复用 fetcher.py 的逻辑）
# =============================================

# 尝试导入 fetcher 中的 compute_relevance 函数
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from fetcher import compute_relevance as _compute_relevance_fetcher

    def compute_relevance(paper: Dict, config: Dict) -> tuple:
        """复用 fetcher.py 的相关性分级逻辑"""
        return _compute_relevance_fetcher(paper, config)
except ImportError:
    def compute_relevance(paper: Dict, config: Dict) -> tuple:
        """
        独立版相关性分级（与 fetcher.py 逻辑一致）。
        返回: (relevance_level, matched_category_name, matched_sub_tags)
        """
        title_lower = paper.get("title", "").lower()
        summary_lower = paper.get("summary", "").lower()
        full_text = title_lower + " " + summary_lower

        # 1. 按领域分类的查询匹配
        best_category = None
        best_match_count = 0
        matched_sub_tags = []

        for cat in config.get("categories", []):
            match_count = 0
            for query in cat.get("queries", []):
                query_lower = query.lower()
                terms = query_lower.split()
                if len(terms) >= 2:
                    if all(term in full_text for term in terms):
                        match_count += 1
                        if query_lower not in matched_sub_tags:
                            matched_sub_tags.append(query_lower)
                else:
                    if query_lower in full_text:
                        match_count += 1
                        if query_lower not in matched_sub_tags:
                            matched_sub_tags.append(query_lower)

            if match_count > best_match_count:
                best_match_count = match_count
                best_category = cat["name"]

        # 2. 相关性等级
        screening = config.get("screening", {})
        high_kw = [kw.lower() for kw in screening.get("high_keywords", [])]
        medium_kw = [kw.lower() for kw in screening.get("medium_keywords", [])]

        high_hits = sum(1 for kw in high_kw if kw in full_text)

        if best_match_count >= 2 or high_hits >= 3:
            relevance = "high"
        elif best_match_count >= 1 or high_hits >= 1 or sum(1 for kw in medium_kw if kw in full_text) >= 3:
            relevance = "medium"
        elif sum(1 for kw in medium_kw if kw in full_text) >= 2:
            relevance = "low"
        else:
            relevance = "low"

        if best_category is None:
            best_category = "Uncategorized"

        return relevance, best_category, matched_sub_tags


# =============================================
# 主流程：执行所有方案
# =============================================

def run_ieee_fetch(config: Optional[Dict] = None) -> List[Dict]:
    """
    执行 IEEE 论文订阅拉取流程：
    方案A: 关键词搜索 (覆盖面广)
    方案B: 期刊名 + 关键词搜索 (目标精确)
    方案C: CrossRef DOI 补摘要 (备选)
    
    返回: 去重 + 分级后的论文元数据列表
    """
    if config is None:
        config = load_config()
    
    ieee_config = config.get("ieee_subscriber", {})
    if not ieee_config.get("enabled", True):
        print("⚠️ IEEE 订阅已禁用 (ieee_subscriber.enabled=false)")
        return []
    
    max_results = ieee_config.get("max_results", 50)
    delay = max(ieee_config.get("delay_seconds", 3), 1)
    processed_ids = load_processed_ids() if config["dedup"]["enabled"] else set()
    
    all_papers: Dict[str, Dict] = {}  # dedup_id -> paper
    
    print("📡 开始 IEEE 期刊订阅拉取 (Semantic Scholar API)...")
    print(f"   策略: 关键词搜索 + 期刊过滤 + CrossRef 补摘要")
    print(f"   请求延迟: {delay}s")
    print("-" * 60)
    
    # ====== 方案A: 关键词搜索 ======
    print("\n📡 方案A: 关键词搜索")
    keyword_queries = ieee_config.get("keyword_queries", [])
    for i, query in enumerate(keyword_queries):
        try:
            papers = search_by_keyword(query, max_results=max_results // len(keyword_queries) + 10)
            for p in papers:
                dedup_id = p.get("dedup_id", "")
                if dedup_id and dedup_id not in all_papers:
                    # 检查是否已处理过
                    if config["dedup"]["enabled"] and dedup_id in processed_ids:
                        continue
                    all_papers[dedup_id] = p
            
            if i < len(keyword_queries) - 1:
                time.sleep(delay + random.uniform(0, 1))
        except Exception as e:
            print(f"   ⚠️ 查询失败: '{query[:50]}...' - {e}")
    
    # ====== 方案B: 按期刊搜索 ======
    print(f"\n📡 方案B: 期刊过滤搜索 (当前累计 {len(all_papers)} 篇)")
    target_journals = ieee_config.get("target_journals", [])
    for i, journal in enumerate(target_journals):
        try:
            papers = search_by_journal(
                journal["name"],
                journal.get("issn", ""),
                journal.get("keyword", "UAV OR drone"),
                max_results=10,
            )
            for p in papers:
                dedup_id = p.get("dedup_id", "")
                if dedup_id and dedup_id not in all_papers:
                    if config["dedup"]["enabled"] and dedup_id in processed_ids:
                        continue
                    all_papers[dedup_id] = p
            
            if i < len(target_journals) - 1:
                time.sleep(delay + random.uniform(0, 1))
        except Exception as e:
            print(f"   ⚠️ 期刊查询失败: '{journal['name'][:40]}...' - {e}")
    
    print(f"\n📊 去重后合计: {len(all_papers)} 篇新论文")
    
    # ====== 方案C: CrossRef 补充摘要 ======
    if ieee_config.get("crossref_fallback", {}).get("enabled", False):
        print("\n📡 方案C: CrossRef 补充摘要...")
        papers_list = list(all_papers.values())
        papers_list = enrich_with_crossref(papers_list)
        all_papers = {p["dedup_id"]: p for p in papers_list}
    
    # ====== 相关性分级 ======
    print("\n🏷️ 相关性分级...")
    results = []
    for paper in all_papers.values():
        relevance, category, sub_tags = compute_relevance(paper, config)
        paper["relevance"] = relevance
        paper["category"] = category
        paper["sub_tags"] = sub_tags
        results.append(paper)
    
    # 按相关性排序
    results.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("relevance", "low"), 3))
    
    # 统计
    high = sum(1 for p in results if p.get("relevance") == "high")
    medium = sum(1 for p in results if p.get("relevance") == "medium")
    low = sum(1 for p in results if p.get("relevance") == "low")
    print(f"   高相关: {high} | 中相关: {medium} | 低相关: {low}")
    
    return results


# =============================================
# 输出：CSV / JSON
# =============================================

def save_results_csv(papers: List[Dict], output_path: Optional[str] = None):
    """将拉取结果保存为 CSV（兼容 Zotero 导入格式）"""
    import csv
    
    if not papers:
        print("   无新论文，跳过 CSV 输出")
        return
    
    if output_path is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = str(get_project_root() / "metadata" / f"{date_str}_ieee_daily.csv")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fieldnames = [
        "dedup_id", "title", "authors", "first_author", "first_author_lastname",
        "year", "published_date", "summary", "doi", "arxiv_id",
        "journal_ref", "source", "relevance", "category", "sub_tags",
        "url", "arxiv_url", "source_query",
    ]
    
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for p in papers:
            # 将 sub_tags list 转为 string
            row = dict(p)
            row["sub_tags"] = "; ".join(row.get("sub_tags", []))
            writer.writerow(row)
    
    print(f"   CSV 已保存: {output_path} ({len(papers)} 篇)")
    return output_path


# =============================================
# 命令行入口
# =============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="IEEE 期刊论文订阅器")
    parser.add_argument("--fetch-only", action="store_true", help="仅拉取，不输出 CSV")
    parser.add_argument("--test", action="store_true", help="测试模式：仅拉取前 3 个查询")
    args = parser.parse_args()
    
    config = load_config()
    
    if args.test:
        # 测试模式：限制查询数量
        config["ieee_subscriber"]["keyword_queries"] = config["ieee_subscriber"]["keyword_queries"][:3]
        config["ieee_subscriber"]["max_results"] = 5
        print("🧪 测试模式：仅拉取前 3 个查询，每查询 5 篇\n")
    
    papers = run_ieee_fetch(config)
    
    if not args.fetch_only and papers:
        csv_path = save_results_csv(papers)
        
        # 打印高相关结果
        high_papers = [p for p in papers if p.get("relevance") == "high"]
        if high_papers:
            print(f"\n{'='*60}")
            print(f"🔴 高相关论文 ({len(high_papers)} 篇)")
            print(f"{'='*60}")
            for i, p in enumerate(high_papers):
                title = p.get("title", "Untitled")[:120]
                journal = p.get("journal_ref", "Unknown")
                doi = p.get("doi", "N/A")
                print(f"\n  [{i+1}] [{journal}]")
                print(f"       {title}")
                print(f"       DOI: {doi}")
                print(f"       URL: {p.get('url', '')}")
    
    print(f"\n✅ IEEE 订阅拉取完成。")
