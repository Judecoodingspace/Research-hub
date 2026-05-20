# -*- coding: utf-8 -*-
"""
每日工作流主脚本
一键执行：arXiv / IEEE 拉取 → 相关性分级 → Papercard 生成 → 索引更新 → 邮件/通知

使用方式：
    python daily_workflow.py                      # 完整流程 (arXiv + IEEE)
    python daily_workflow.py --fetch-only         # 仅拉取，不生成 papercard
    python daily_workflow.py --source arxiv       # 仅拉取 arXiv
    python daily_workflow.py --source ieee        # 仅拉取 IEEE
    python daily_workflow.py --min-relevance high # 仅生成高相关 papercard
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# 将当前目录加入路径
sys.path.insert(0, str(Path(__file__).parent))

from fetcher import run_arxiv_fetch, load_config
from generator import run_papercard_generation

# =============================================
# 日报生成
# =============================================

def generate_daily_report(papers, stats, csv_path, source="arXiv"):
    """
    生成每日简报 Markdown 文件
    存放位置: arxiv_subscriber/daily_reports/YYYY-MM-DD.md
    """
    config = load_config()
    report_dir = Path(__file__).parent / "daily_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = report_dir / f"{date_str}.md"
    
    # 按相关性分组
    high_papers = [p for p in papers if p.get("relevance") == "high"]
    medium_papers = [p for p in papers if p.get("relevance") == "medium"]
    low_papers = [p for p in papers if p.get("relevance") == "low"]
    
    # 按分类分组
    by_category = {}
    for p in papers:
        cat = p.get("category", "Uncategorized")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(p)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 📡 {source} 每日简报 — {date_str}\n\n")
        f.write(f"> 自动生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> 拉取论文数：{len(papers)} 篇 | 高相关：{len(high_papers)} | 中相关：{len(medium_papers)} | 低相关：{len(low_papers)}\n\n")
        
        f.write("---\n\n")
        
        # 概览
        f.write("## 📊 概览\n\n")
        f.write("| 分类 | 高相关 | 中相关 | 低相关 | 合计 |\n")
        f.write("|------|--------|--------|--------|------|\n")
        for cat, cat_papers in sorted(by_category.items()):
            h = sum(1 for p in cat_papers if p.get("relevance") == "high")
            m = sum(1 for p in cat_papers if p.get("relevance") == "medium")
            l = sum(1 for p in cat_papers if p.get("relevance") == "low")
            f.write(f"| {cat} | {h} | {m} | {l} | {len(cat_papers)} |\n")
        
        f.write("\n---\n\n")
        
        # 🔴 高相关论文
        if high_papers:
            f.write("## 🔴 高相关论文 — 建议优先阅读\n\n")
            for p in high_papers:
                f.write(f"### {p.get('title', 'Untitled')}\n\n")
                f.write(f"- **作者**：{p.get('authors', '')[:150]}\n")
                # arXiv 或 DOI 链接
                paper_url = p.get('arxiv_url', '') or p.get('url', '')
                paper_id = p.get('arxiv_id', '') or p.get('doi', '')
                f.write(f"- **来源**：{p.get('source', 'arXiv')} | [{paper_id}]({paper_url})\n")
                f.write(f"- **发表**：{p.get('published_date', '')}\n")
                f.write(f"- **期刊**：{p.get('journal_ref', '')}\n")
                f.write(f"- **分类**：{p.get('category', '')}\n")
                f.write(f"- **摘要**：{p.get('summary', '')[:400]}...\n")
                f.write(f"- **Papercard**：`papercard/{p.get('category', 'Uncategorized')}/`\n")
                f.write("\n")
        
        # 🟡 中相关论文
        if medium_papers:
            f.write("## 🟡 中相关论文 — 可关注\n\n")
            f.write("| 标题 | 作者 | 来源 | 分类 |\n")
            f.write("|------|------|------|------|\n")
            for p in medium_papers:
                title = p.get('title', 'Untitled')[:60]
                author = p.get('first_author', 'Unknown')[:30]
                source = p.get('source', 'arXiv')
                cat = p.get('category', '')
                paper_url = p.get('arxiv_url', '') or p.get('url', '')
                paper_id = p.get('arxiv_id', '') or p.get('doi', '')
                f.write(f"| {title}... | {author} | [{paper_id}]({paper_url}) | {cat} |\n")
            f.write("\n")
        
        # ⚪ 低相关论文
        if low_papers:
            f.write(f"## ⚪ 低相关论文 ({len(low_papers)} 篇)\n\n")
            f.write("<details>\n<summary>展开查看</summary>\n\n")
            f.write("| 标题 | 分类 |\n")
            f.write("|------|------|\n")
            for p in low_papers:
                title = p.get('title', 'Untitled')[:80]
                cat = p.get('category', '')
                f.write(f"| {title}... | {cat} |\n")
            f.write("\n</details>\n\n")
        
        # 统计信息
        f.write("---\n\n")
        f.write("## 📈 累积统计\n\n")
        f.write(f"- CSV 元数据：`{csv_path}`\n")
        f.write(f"- Papercard 生成：{stats.get('generated', 0)} 篇\n")
        f.write(f"- 错误：{stats.get('errors', 0)} 篇\n")
    
    print(f"\n📰 每日简报已生成: {report_path}")
    return report_path


# =============================================
# IEEE 拉取流程
# =============================================

def run_ieee_fetch_and_save():
    """执行 IEEE 拉取并保存 CSV"""
    from ieee_subscriber import run_ieee_fetch as ieee_fetch, save_results_csv
    
    print("\n" + "=" * 60)
    print("📡 IEEE 期刊订阅拉取 (Semantic Scholar API)")
    print("=" * 60)
    
    papers = ieee_fetch()
    
    if not papers:
        print("✅ IEEE 无新论文。")
        return None, None
    
    csv_path = save_results_csv(papers)
    return papers, csv_path


# =============================================
# 主流程
# =============================================

def main():
    parser = argparse.ArgumentParser(description="arXiv/IEEE 领域订阅 + Papercard 自动生成")
    parser.add_argument("--fetch-only", action="store_true", 
                        help="仅拉取论文元数据，不生成 papercard")
    parser.add_argument("--source", type=str, default="all",
                        choices=["all", "arxiv", "ieee"],
                        help="拉取来源: all (默认), arxiv, ieee")
    parser.add_argument("--min-relevance", type=str, default="medium",
                        choices=["high", "medium", "low"],
                        help="生成 papercard 的最低相关性等级 (默认: medium)")
    parser.add_argument("--dry-run", action="store_true",
                        help="试运行：仅拉取不保存")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 领域订阅系统 — 每日工作流")
    print(f"   时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   模式：{'仅拉取' if args.fetch_only else '拉取+生成'}")
    print(f"   来源：{args.source}")
    print(f"   最低等级：{args.min_relevance}")
    print("=" * 60)
    
    all_papers = []
    csv_paths = []
    
    # 1. arXiv 拉取
    if args.source in ("all", "arxiv"):
        papers, csv_path = run_arxiv_fetch()
        if papers:
            all_papers.extend(papers)
            csv_paths.append(csv_path)
    
    # 2. IEEE 拉取
    if args.source in ("all", "ieee"):
        ieee_papers, ieee_csv = run_ieee_fetch_and_save()
        if ieee_papers:
            all_papers.extend(ieee_papers)
            if ieee_csv:
                csv_paths.append(ieee_csv)
    
    if not all_papers:
        print("\n✅ 今日无新论文，结束。")
        return
    
    # 3. 如果是 fetch-only 模式，到此为止
    if args.fetch_only:
        csv_all = "; ".join(csv_paths)
        print(f"\n✅ 拉取完成！元数据已保存: {csv_all}")
        print(f"   使用以下命令生成 papercard:")
        print(f"   python generator.py  # 或运行完整工作流")
        return
    
    # 4. 生成 papercard
    stats = run_papercard_generation(all_papers, min_relevance=args.min_relevance)
    
    # 5. 生成每日简报
    csv_all = "; ".join(csv_paths)
    report_path = generate_daily_report(all_papers, stats, csv_all, source=args.source.upper())
    
    # 6. 总结
    print(f"\n{'='*60}")
    print(f"✨ 每日工作流完成!")
    print(f"{'='*60}")
    print(f"   📡 拉取论文: {len(all_papers)} 篇")
    print(f"   📝 生成 Papercard: {stats['generated']} 篇")
    print(f"   📰 每日简报: {report_path}")
    print(f"   📄 元数据 CSV: {csv_all}")
    
    # 7. 高相关论文快速预览
    high_papers = [p for p in all_papers if p.get("relevance") == "high"]
    if high_papers:
        print(f"\n🔴 今日高相关论文 ({len(high_papers)} 篇) — 建议优先阅读:")
        for p in high_papers:
            source = p.get('source', 'arXiv')
            title = p.get('title', '')[:100]
            url = p.get('arxiv_url', '') or p.get('url', '')
            print(f"   📌 [{source}] {title}")
            print(f"      {url}")


if __name__ == "__main__":
    main()
