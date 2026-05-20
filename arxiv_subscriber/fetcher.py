# -*- coding: utf-8 -*-
"""
arXiv 订阅器 — 核心模块
功能：从 arXiv API 拉取新论文，按 config.yaml 中的领域分类进行初筛和去重

依赖：pip install arxiv requests pyyaml
"""

import yaml
import json
import os
import sys
import time
import random
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

# 设置 stdout 为 UTF-8 编码（避免 Windows GBK 编码报错）
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# =============================================
# 路径工具
# =============================================

def get_project_root() -> Path:
    """获取项目根目录 (arxiv_subscriber 的父目录)"""
    return Path(__file__).resolve().parent.parent

def load_config() -> Dict:
    """加载 config.yaml"""
    config_path = get_project_root() / "arxiv_subscriber" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# =============================================
# 去重管理
# =============================================

def load_processed_ids() -> set:
    """加载已处理的论文 arXiv ID 集合"""
    config = load_config()
    id_path = get_project_root() / config["dedup"]["id_store"]
    if not id_path.exists():
        return set()
    try:
        with open(id_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return set(data.get("processed_ids", []))
    except (json.JSONDecodeError, Exception):
        # 文件损坏或格式错误，重置
        return set()

def save_processed_ids(ids: set):
    """保存已处理的论文 arXiv ID 集合"""
    config = load_config()
    id_path = get_project_root() / config["dedup"]["id_store"]
    id_path.parent.mkdir(parents=True, exist_ok=True)
    with open(id_path, "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": datetime.now().isoformat(),
            "total_processed": len(ids),
            "processed_ids": sorted(list(ids))
        }, f, indent=2)

def extract_arxiv_id(paper: arxiv.Result) -> str:
    """从 arXiv Result 中提取唯一 ID (如 '2208.12345v1')"""
    # entry_id 格式: 'http://arxiv.org/abs/2208.12345v1'
    entry_id = paper.entry_id
    return entry_id.split("/")[-1]  # 取最后一段: '2208.12345v1'

def get_base_id(arxiv_id: str) -> str:
    """去掉版本号, 如 '2208.12345v1' -> '2208.12345'"""
    return arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

# =============================================
# 论文元数据提取
# =============================================

def extract_paper_metadata(paper: arxiv.Result) -> Dict:
    """从 arXiv Result 中提取标准化元数据（兼容 Zotero CSV 格式）"""
    arxiv_id = extract_arxiv_id(paper)
    base_id = get_base_id(arxiv_id)
    
    # 作者列表
    authors = "; ".join([a.name for a in paper.authors])
    first_author = paper.authors[0].name if paper.authors else "Unknown"
    
    # 日期处理
    published = paper.published.replace(tzinfo=timezone.utc) if paper.published else None
    
    # 分类标签
    categories = "; ".join(paper.categories) if paper.categories else ""
    
    # 构建标准化元数据
    metadata = {
        "arxiv_id": arxiv_id,
        "base_id": base_id,
        "arxiv_url": f"https://arxiv.org/abs/{base_id}",
        "pdf_url": paper.pdf_url,
        "title": paper.title.strip().replace("\n", " "),
        "authors": authors,
        "first_author": first_author,
        "first_author_lastname": paper.authors[0].name.split()[-1] if paper.authors else "Unknown",
        "published": published.isoformat() if published else "",
        "published_date": published.strftime("%Y-%m-%d") if published else "",
        "year": str(published.year) if published else "",
        "summary": paper.summary.strip().replace("\n", " "),
        "comment": paper.comment or "",
        "journal_ref": paper.journal_ref or "",
        "primary_category": paper.primary_category,
        "categories": categories,
        "doi": paper.doi or "",
    }
    
    return metadata

# =============================================
# 相关性分级与分类
# =============================================

def compute_relevance(metadata: Dict, config: Dict) -> tuple:
    """
    计算论文的相关性等级和归类
    
    改进的匹配逻辑（修复假阳性问题）：
    1. 每个领域查询词必须**整体匹配**（所有单词同时出现）
    2. 至少命中 1 个完整的领域查询词才算有效匹配
    3. 高相关 = 命中 ≥ 2 个完整查询词 或 命中 ≥ 3 个高级关键词
    4. 中相关 = 命中 ≥ 1 个完整查询词 或 命中 ≥ 1 个高级关键词
    
    返回: (relevance_level, matched_category_name, matched_sub_tags)
    """
    title_lower = metadata["title"].lower()
    summary_lower = metadata["summary"].lower()
    full_text = title_lower + " " + summary_lower
    
    # 1. 按领域分类的查询匹配（确定归属目录）
    best_category = None
    best_match_count = 0
    matched_sub_tags = []
    
    for cat in config.get("categories", []):
        match_count = 0
        for query in cat.get("queries", []):
            query_lower = query.lower()
            # 查询词可以包含多个单词，**全部同时出现**才算一次完整匹配
            terms = query_lower.split()
            if len(terms) >= 2:
                # 多词查询：必须全部出现
                if all(term in full_text for term in terms):
                    match_count += 1
                    if query_lower not in matched_sub_tags:
                        matched_sub_tags.append(query_lower)
            else:
                # 单词查询：直接匹配
                if query_lower in full_text:
                    match_count += 1
                    if query_lower not in matched_sub_tags:
                        matched_sub_tags.append(query_lower)
        
        if match_count > best_match_count:
            best_match_count = match_count
            best_category = cat["name"]
    
    # 2. 计算相关性等级（更严格）
    screening = config.get("screening", {})
    high_kw = [kw.lower() for kw in screening.get("high_keywords", [])]
    medium_kw = [kw.lower() for kw in screening.get("medium_keywords", [])]
    
    high_hits = sum(1 for kw in high_kw if kw in full_text)
    # 至少命中 high_kw 中 ≥ 3 个才算（避免单关键词误匹配）
    
    if best_match_count >= 2 or high_hits >= 3:
        relevance = "high"
    elif best_match_count >= 1 or high_hits >= 1 or sum(1 for kw in medium_kw if kw in full_text) >= 3:
        relevance = "medium"
    elif sum(1 for kw in medium_kw if kw in full_text) >= 2:
        relevance = "low"
    else:
        relevance = "low"
    
    # 如果没有匹配到任何分类，归入 "Uncategorized"
    if best_category is None:
        best_category = "Uncategorized"
    
    return relevance, best_category, matched_sub_tags

# =============================================
# arXiv 查询与拉取
# =============================================

# =============================================
# arXiv API 直接 HTTP 访问（替代 arxiv 库，更好控制限流）
# =============================================

ARXIV_API_BASE = "https://export.arxiv.org/api/query"
ARXIV_RSS_BASE = "https://rss.arxiv.org/rss"

# arXiv 主要分类 → RSS feed 映射
# 覆盖项目关注的方向：CV、通信、网络、AI、机器人
RSS_CATEGORIES = [
    "cs.CV",        # Computer Vision
    "cs.NI",        # Networking and Internet Architecture
    "cs.AI",        # Artificial Intelligence
    "cs.LG",        # Machine Learning
    "cs.RO",        # Robotics
    "eess.IV",      # Image and Video Processing
    "eess.SP",      # Signal Processing
    "cs.MA",        # Multiagent Systems
    "cs.SY",        # Systems and Control
]

# arXiv 标准命名空间
NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
    'arxiv': 'http://arxiv.org/schemas/atom',
}

def _arxiv_request(url: str, max_retries: int = 5) -> str:
    """发送 arXiv API 请求，处理限流和重试"""
    last_error = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'ResearchHub/1.0 (mailto:research@example.com)'}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                # 检查限流头
                remaining = resp.headers.get('X-RateLimit-Remaining', 'unknown')
                retry_after = resp.headers.get('Retry-After', '0')
                
                body = resp.read().decode('utf-8')
                
                # 如果限流即将耗尽，主动等待
                try:
                    rem = int(remaining)
                    if rem < 3:
                        wait = max(int(retry_after), 30)
                        print(f"      ⏳ 限流预警 (剩余={rem}), 等待 {wait}s...")
                        time.sleep(wait)
                except ValueError:
                    pass
                
                return body
                
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # 读取 Retry-After 头
                retry_after = e.headers.get('Retry-After', '30')
                try:
                    wait = int(retry_after)
                except ValueError:
                    wait = 30
                wait = min(wait, 120)  # 最多等 120 秒
                print(f"      ⚠️ HTTP 429, 等待 {wait}s 后重试 ({attempt+1}/{max_retries})...")
                time.sleep(wait + random.uniform(1, 5))
                last_error = e
            else:
                raise
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = (attempt + 1) * 10
                print(f"      ⚠️ 请求失败: {e}, {wait}s 后重试 ({attempt+1}/{max_retries})...")
                time.sleep(wait)
    
    raise last_error or RuntimeError(f"Request failed after {max_retries} retries: {url}")

def _parse_arxiv_api_response(xml_text: str) -> List[Dict]:
    """解析 arXiv API XML 响应 (Atom feed, 使用 <entry> 元素)"""
    root = ET.fromstring(xml_text)
    papers = []
    
    for entry in root.findall('atom:entry', NS):
        paper = _parse_entry_common(entry)
        if paper:
            papers.append(paper)
    
    return papers


def _parse_arxiv_rss_response(xml_text: str) -> List[Dict]:
    """解析 arXiv RSS feed 响应 (RSS 2.0, 使用 <item> 元素)"""
    root = ET.fromstring(xml_text)
    papers = []
    
    # RSS 的结构: <rss><channel>...<item>...</item>...</channel></rss>
    channel = root.find('channel')
    if channel is None:
        return papers
    
    for item in channel.findall('item'):
        paper = {}
        
        # arXiv ID — 从 <link> 提取
        link_elem = item.find('link')
        if link_elem is not None and link_elem.text:
            href = link_elem.text.strip()
            # https://arxiv.org/abs/2605.15256v1 -> 2605.15256v1
            paper['arxiv_id'] = href.split('/')[-1]
            paper['base_id'] = paper['arxiv_id'].split('v')[0] if 'v' in paper['arxiv_id'] else paper['arxiv_id']
        
        if not paper.get('arxiv_id'):
            continue
        
        # 标题
        title_elem = item.find('title')
        if title_elem is not None and title_elem.text:
            paper['title'] = title_elem.text.strip().replace('\n', ' ').replace('  ', ' ')
        
        # 摘要 (RSS 用 <description>)
        desc_elem = item.find('description')
        if desc_elem is not None and desc_elem.text:
            raw = desc_elem.text.strip()
            # 移除 arXiv ID 前缀和 Announce Type
            # 格式: "arXiv:2605.15256v1 Announce Type: new  Abstract: ..."
            if 'Abstract:' in raw:
                raw = raw.split('Abstract:', 1)[-1]
            paper['summary'] = raw.strip().replace('\n', ' ').replace('  ', ' ')
        
        # 作者 (RSS 用 <dc:creator>)
        dc_ns = 'http://purl.org/dc/elements/1.1/'
        creator_elem = item.find('{http://purl.org/dc/elements/1.1/}creator')
        if creator_elem is not None and creator_elem.text:
            authors_raw = creator_elem.text.strip()
            authors = [a.strip() for a in authors_raw.split(',')]
            paper['authors'] = '; '.join(authors)
            paper['first_author'] = authors[0] if authors else 'Unknown'
            paper['first_author_lastname'] = authors[0].split()[-1] if authors else 'Unknown'
        
        # 发布日期
        pub_elem = item.find('pubDate')
        if pub_elem is not None and pub_elem.text:
            from email.utils import parsedate_to_datetime
            try:
                dt = parsedate_to_datetime(pub_elem.text.strip())
                paper['published'] = dt.isoformat()
                paper['published_date'] = dt.strftime('%Y-%m-%d')
                paper['year'] = str(dt.year)
            except:
                paper['published_date'] = pub_elem.text.strip()[:10]
                paper['year'] = paper['published_date'][:4]
        
        # 分类 (RSS 用 <category>)
        categories = []
        for cat in item.findall('category'):
            if cat.text:
                categories.append(cat.text.strip())
        paper['categories'] = '; '.join(categories)
        paper['primary_category'] = categories[0] if categories else ''
        
        # 其他字段
        paper['doi'] = ''
        paper['arxiv_url'] = f"https://arxiv.org/abs/{paper.get('base_id', '')}"
        paper['pdf_url'] = f"https://arxiv.org/pdf/{paper.get('base_id', '')}"
        paper['journal_ref'] = 'arXiv preprint'
        paper['comment'] = ''
        
        papers.append(paper)
    
    return papers


def _parse_entry_common(entry) -> Dict:
    """从 Atom entry 中提取通用字段 (API 和 RSS 共用)"""
    paper = {}
    
    # arXiv ID
    id_url = entry.find('atom:id', NS)
    if id_url is not None and id_url.text:
        paper['arxiv_id'] = id_url.text.strip().split('/')[-1]
        paper['base_id'] = paper['arxiv_id'].split('v')[0] if 'v' in paper['arxiv_id'] else paper['arxiv_id']
    
    if not paper.get('arxiv_id'):
        return None
    
    # 标题
    title_elem = entry.find('atom:title', NS)
    if title_elem is not None and title_elem.text:
        paper['title'] = title_elem.text.strip().replace('\n', ' ').replace('  ', ' ')
    
    # 摘要
    summary_elem = entry.find('atom:summary', NS)
    if summary_elem is not None and summary_elem.text:
        paper['summary'] = summary_elem.text.strip().replace('\n', ' ').replace('  ', ' ')
    
    # 作者
    authors = []
    for author in entry.findall('atom:author', NS):
        name_elem = author.find('atom:name', NS)
        if name_elem is not None and name_elem.text:
            authors.append(name_elem.text.strip())
    paper['authors'] = '; '.join(authors)
    paper['first_author'] = authors[0] if authors else 'Unknown'
    paper['first_author_lastname'] = authors[0].split()[-1] if authors else 'Unknown'
    
    # 发布日期
    published_elem = entry.find('atom:published', NS)
    if published_elem is not None and published_elem.text:
        paper['published'] = published_elem.text.strip()
        try:
            dt = datetime.fromisoformat(paper['published'].replace('Z', '+00:00'))
            paper['published_date'] = dt.strftime('%Y-%m-%d')
            paper['year'] = str(dt.year)
        except:
            paper['published_date'] = paper['published'][:10]
            paper['year'] = paper['published'][:4]
    
    # 分类
    categories = []
    for cat in entry.findall('atom:category', NS):
        term = cat.get('term', '')
        if term:
            categories.append(term)
    paper['categories'] = '; '.join(categories)
    paper['primary_category'] = categories[0] if categories else ''
    
    # DOI
    for link in entry.findall('atom:link', NS):
        if link.get('title') == 'doi':
            paper['doi'] = link.get('href', '')
            break
    if 'doi' not in paper:
        paper['doi'] = ''
    
    # arXiv URL
    paper['arxiv_url'] = f"https://arxiv.org/abs/{paper.get('base_id', '')}"
    paper['pdf_url'] = f"https://arxiv.org/pdf/{paper.get('base_id', '')}"
    
    # 其他
    paper['journal_ref'] = 'arXiv preprint'
    comment_elem = entry.find('arxiv:comment', NS)
    if comment_elem is not None and comment_elem.text:
        paper['comment'] = comment_elem.text.strip()
    else:
        paper['comment'] = ''
    
    return paper


def _parse_arxiv_response(xml_text: str, is_rss: bool = False) -> List[Dict]:
    """
    统一的 arXiv 响应解析入口
    
    参数:
        xml_text: XML 文本
        is_rss: True=RSS feed 格式, False=API Atom feed 格式
    """
    if is_rss:
        return _parse_arxiv_rss_response(xml_text)
    else:
        return _parse_arxiv_api_response(xml_text)

def search_arxiv(config: Dict) -> List[Dict]:
    """
    按 config 中的 categories 查询 arXiv，合并去重后返回论文元数据列表。
    
    策略：
    1. 主通道：RSS feed（无严格限流，获取今日新论文）
    2. 备通道：arXiv API（按查询词搜索，用于精确匹配领域关键词）
    3. 两步合并：RSS 全量初筛 → API 精确补漏 → 按关键词分类过滤
    
    RSS feed 没有查询参数限制，可一次性获取 cs.CV 今天所有新论文（约 50-200 篇），
    然后用本地关键词过滤。这避免了 arXiv API 的严格限流（HTTP 429）。
    """
    all_papers = {}  # base_id -> metadata
    processed_ids = load_processed_ids() if config["dedup"]["enabled"] else set()
    
    base_delay = max(config["arxiv"]["delay_seconds"], 5)
    
    print(f"\U0001f4e1 开始查询 arXiv...")
    print(f"   策略: RSS feed (优先) + API (备选)")
    print(f"   RSS 分类: {', '.join(RSS_CATEGORIES)}")
    print(f"   查询间隔: {base_delay}s")
    print("-" * 60)
    
    # ====== 阶段 1: RSS Feed 拉取 ======
    print(f"\n\U0001f4e1 阶段 1: RSS Feed 拉取 ({len(RSS_CATEGORIES)} 个分类)")
    rss_papers = {}  # 临时存储，用于关键词过滤
    
    for idx, cat in enumerate(RSS_CATEGORIES):
        try:
            rss_url = f"{ARXIV_RSS_BASE}/{cat}"
            xml_text = _arxiv_request(rss_url)
            papers = _parse_arxiv_response(xml_text, is_rss=True)
            
            new_count = 0
            for p in papers:
                base_id = p.get('base_id', '')
                if base_id and base_id not in rss_papers:
                    rss_papers[base_id] = p
                    new_count += 1
            
            print(f"  [{idx+1}/{len(RSS_CATEGORIES)}] {cat}: {len(papers)} 篇 (新增 {new_count})")
            
        except Exception as e:
            print(f"  [{idx+1}/{len(RSS_CATEGORIES)}] {cat}: \u274c {str(e)[:80]}")
        
        # RSS feed 之间的小延迟
        if idx < len(RSS_CATEGORIES) - 1:
            time.sleep(base_delay / 2)
    
    print(f"\n\U0001f4ca RSS 阶段完成: 去重后共 {len(rss_papers)} 篇候选论文")
    
    # ====== 阶段 2: 本地关键词过滤 ======
    print(f"\n\U0001f50d 阶段 2: 关键词过滤 + 相关性分级")
    
    # 收集所有查询关键词（用于标题/摘要过滤）
    all_keywords = set()
    for cat in config.get("categories", []):
        for query in cat.get("queries", []):
            for term in query.lower().split():
                if len(term) > 2:  # 忽略太短的词
                    all_keywords.add(term)
    
    matched_count = 0
    for base_id, paper in rss_papers.items():
        # 去重检查
        if config["dedup"]["enabled"] and base_id in processed_ids:
            continue
        
        title = paper.get('title', '').lower()
        summary = paper.get('summary', '').lower()
        full_text = title + ' ' + summary
        
        # 检查是否匹配任何关键词
        matched = False
        for kw in all_keywords:
            if kw in full_text:
                matched = True
                break
        
        if not matched and len(all_keywords) > 0:
            continue  # 不匹配任何关键词，跳过
        
        matched_count += 1
        
        # 相关性分级
        relevance, category, sub_tags = compute_relevance(paper, config)
        paper['relevance'] = relevance
        paper['category'] = category
        paper['sub_tags'] = sub_tags
        
        if base_id not in all_papers:
            all_papers[base_id] = paper
    
    print(f"   关键词过滤后: {matched_count} 篇 (从 {len(rss_papers)} 篇中)")
    
    # ====== 阶段 3: arXiv API 精确补漏（可选，控制频次） ======
    # 仅在关键词过滤后少于 5 篇时启用 API 补漏
    if len(all_papers) < 5:
        print(f"\n\U0001f50d 阶段 3: arXiv API 精确补漏 (结果较少，启用)")
        api_max_results = 10
        
        for cat_config in config.get("categories", []):
            for query in cat_config.get("queries", []):
                if len(all_papers) >= 50:
                    break
                    
                try:
                    params = {
                        'search_query': query,
                        'sortBy': 'submittedDate',
                        'sortOrder': 'descending',
                        'start': 0,
                        'max_results': api_max_results,
                    }
                    url = ARXIV_API_BASE + '?' + urllib.parse.urlencode(params)
                    xml_text = _arxiv_request(url)
                    papers = _parse_arxiv_response(xml_text, is_rss=False)
                    
                    new_count = 0
                    for p in papers:
                        base_id = p.get('base_id', '')
                        if config["dedup"]["enabled"] and base_id in processed_ids:
                            continue
                        if base_id and base_id not in all_papers:
                            relevance, category, sub_tags = compute_relevance(p, config)
                            p['relevance'] = relevance
                            p['category'] = category
                            p['sub_tags'] = sub_tags
                            all_papers[base_id] = p
                            new_count += 1
                    
                    if new_count > 0:
                        print(f"  {query[:50]}...: +{new_count} 篇")
                    
                    time.sleep(base_delay * 2)  # API 需要更长的间隔
                    
                except Exception as e:
                    print(f"  {query[:50]}...: \u26a0\ufe0f {str(e)[:60]}")
    
    # 按发布日期排序
    papers_list = sorted(all_papers.values(), 
                         key=lambda x: x.get("published", ""), 
                         reverse=True)
    
    print(f"\n\U0001f4ca 查询完成: 最终 {len(papers_list)} 篇新论文")
    return papers_list
    
    # 按发布日期排序
    papers_list = sorted(all_papers.values(), 
                         key=lambda x: x.get("published", ""), 
                         reverse=True)
    
    print(f"\n📊 去重后共 {len(papers_list)} 篇新论文 (已过滤 {len(processed_ids)} 篇已处理)")
    return papers_list

# =============================================
# 元数据导出 (CSV 格式，兼容 Zotero 导入)
# =============================================

def export_metadata_csv(papers: List[Dict], output_dir: Path, date_str: str):
    """
    将论文元数据导出为 CSV (兼容项目现有 Zotero metadata 格式)
    """
    import csv
    
    csv_path = output_dir / f"{date_str}_arxiv_daily.csv"
    
    fieldnames = [
        "Key", "Item Type", "Publication Year", "Author", "Title",
        "Publication Title", "ISSN", "DOI", "Url", "Abstract Note",
        "Date", "Date Added", "Extra", "Manual Tags", "Automatic Tags",
        "ArXiv ID", "Primary Category", "Categories"
    ]
    
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        
        for p in papers:
            writer.writerow({
                "Key": p.get("base_id", ""),
                "Item Type": "journalArticle",
                "Publication Year": p.get("year", ""),
                "Author": p.get("authors", ""),
                "Title": p.get("title", ""),
                "Publication Title": p.get("journal_ref", "arXiv preprint"),
                "DOI": p.get("doi", ""),
                "Url": p.get("arxiv_url", ""),
                "Abstract Note": p.get("summary", ""),
                "Date": p.get("published_date", ""),
                "Date Added": datetime.now().isoformat(),
                "Extra": f"Relevance: {p.get('relevance', '')} | Category: {p.get('category', '')}",
                "Manual Tags": "; ".join(p.get("sub_tags", [])),
                "Automatic Tags": p.get("categories", ""),
                "ArXiv ID": p.get("arxiv_id", ""),
                "Primary Category": p.get("primary_category", ""),
                "Categories": p.get("categories", ""),
            })
    
    print(f"📄 元数据已导出: {csv_path}")
    return csv_path

# =============================================
# 主入口
# =============================================

def run_arxiv_fetch(output_dir: Optional[Path] = None) -> tuple:
    """
    执行 arXiv 订阅拉取
    
    参数:
        output_dir: 输出目录，默认为 metadata/
    
    返回:
        (papers_list, metadata_csv_path)
    """
    config = load_config()
    
    if output_dir is None:
        output_dir = get_project_root() / "metadata"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 日期标记
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 拉取论文
    papers = search_arxiv(config)
    
    if not papers:
        print("✅ 没有发现新论文")
        return [], None
    
    # 2. 相关性分级
    print(f"\n📋 相关性分级...")
    high_count = medium_count = low_count = 0
    for p in papers:
        relevance, category, sub_tags = compute_relevance(p, config)
        p["relevance"] = relevance
        p["category"] = category
        p["sub_tags"] = sub_tags
        
        if relevance == "high":
            high_count += 1
        elif relevance == "medium":
            medium_count += 1
        else:
            low_count += 1
    
    print(f"   🔴 高相关: {high_count} 篇")
    print(f"   🟡 中相关: {medium_count} 篇")
    print(f"   ⚪ 低相关: {low_count} 篇")
    
    # 3. 导出 CSV
    csv_path = export_metadata_csv(papers, output_dir, date_str)
    
    # 4. 更新已处理 ID
    if config["dedup"]["enabled"]:
        processed_ids = load_processed_ids()
        for p in papers:
            processed_ids.add(p["base_id"])
        save_processed_ids(processed_ids)
        print(f"💾 已更新去重数据库: {len(processed_ids)} 篇已处理")
    
    return papers, csv_path


if __name__ == "__main__":
    # 独立运行时执行拉取
    papers, csv_path = run_arxiv_fetch()
    
    if papers:
        print(f"\n✨ 完成! 共拉取 {len(papers)} 篇新论文")
        # 打印高相关论文标题
        high_papers = [p for p in papers if p["relevance"] == "high"]
        if high_papers:
            print(f"\n🔴 高相关论文 ({len(high_papers)} 篇):")
            for p in high_papers:
                print(f"   [{p['category']}] {p['title'][:100]}...")
                print(f"     {p['arxiv_url']}")
