# -*- coding: utf-8 -*-
"""
多普勒效应对 CVN 信道影响 — 关键词批量检索脚本
==================================================
基于 ieee_subscriber.py 的 Semantic Scholar API 客户端，
使用 15 组多普勒 + CVN / 车载信道相关关键词组合进行检索。

输出：metadata/doppler_search/ 文件夹下的 CSV 文件
"""
import sys
import os
import csv
import time
import random
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

# 导入 ieee_subscriber 中的核心函数
from ieee_subscriber import (
    search_by_keyword,
    compute_relevance,
    load_config,
    load_processed_ids,
    save_processed_ids,
)

# 设置 stdout 编码
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================
# 15 组多普勒 + CVN 关键词组合
# =============================================
DOPPLER_QUERIES = [
    # === 高精度组合 ===
    {
        "query": '"Doppler spread" "vehicular channel" "5.9 GHz"',
        "label": "Q1_DopplerSpread_VehicularChannel_5.9GHz",
        "description": "多普勒扩展 + 车载信道 + 5.9GHz",
    },
    {
        "query": '"Doppler effect" "cognitive vehicular network" "channel estimation"',
        "label": "Q2_DopplerEffect_CVN_ChannelEstimation",
        "description": "多普勒效应 + 认知车联网 + 信道估计",
    },
    {
        "query": '"high mobility" "Doppler shift" V2X "channel coherence time"',
        "label": "Q3_HighMobility_DopplerShift_V2X_CoherenceTime",
        "description": "高移动性 + 多普勒频移 + V2X + 信道相干时间",
    },
    {
        "query": '"time-varying channel" vehicular Doppler OFDM',
        "label": "Q4_TimeVaryingChannel_Vehicular_Doppler_OFDM",
        "description": "时变信道 + 车载 + 多普勒 + OFDM",
    },
    {
        "query": '"Doppler power spectrum" V2V "channel modeling"',
        "label": "Q5_DopplerPowerSpectrum_V2V_ChannelModeling",
        "description": "多普勒功率谱 + V2V + 信道建模",
    },
    # === 中等精度 ===
    {
        "query": '"vehicular communication" Doppler "channel aging"',
        "label": "Q6_VehicularComm_Doppler_ChannelAging",
        "description": "车载通信 + 多普勒 + 信道老化",
    },
    {
        "query": '"spectrum sensing" Doppler "cognitive radio" mobility',
        "label": "Q7_SpectrumSensing_Doppler_CR_Mobility",
        "description": "频谱感知 + 多普勒 + 认知无线电 + 移动性",
    },
    {
        "query": 'DSRC "Doppler spread" "channel estimation"',
        "label": "Q8_DSRC_DopplerSpread_ChannelEstimation",
        "description": "DSRC + 多普勒扩展 + 信道估计",
    },
    {
        "query": 'C-V2X "Doppler spread" "channel estimation"',
        "label": "Q8b_CV2X_DopplerSpread_ChannelEstimation",
        "description": "C-V2X + 多普勒扩展 + 信道估计",
    },
    {
        "query": '"Rician fading" vehicular Doppler "5.9 GHz"',
        "label": "Q9_RicianFading_Vehicular_Doppler_5.9GHz",
        "description": "Rician衰落 + 车载 + 多普勒 + 5.9GHz",
    },
    {
        "query": '"non-stationary" "vehicular channel" Doppler',
        "label": "Q10_NonStationary_VehicularChannel_Doppler",
        "description": "非平稳 + 车载信道 + 多普勒",
    },
    # === 宽泛搜索（综述/奠基） ===
    {
        "query": '"vehicular channel" survey Doppler',
        "label": "Q11_VehicularChannel_Survey_Doppler",
        "description": "车载信道综述 + 多普勒",
    },
    {
        "query": '"cognitive vehicular" "physical layer" Doppler',
        "label": "Q12_CVN_PhysicalLayer_Doppler",
        "description": "CVN 物理层 + 多普勒",
    },
    # === 针对论文具体论证点 ===
    {
        "query": '"coherence time" vehicular "120 km/h"',
        "label": "Q13_CoherenceTime_Vehicular_120kmh",
        "description": "相干时间 + 车载 + 120km/h",
    },
    {
        "query": '"Doppler compensation" vehicular "deep learning"',
        "label": "Q14_DopplerCompensation_Vehicular_DL",
        "description": "多普勒补偿 + 车载 + 深度学习",
    },
    {
        "query": '"small scale fading" vehicular "Doppler spread" "coherence bandwidth"',
        "label": "Q15_SmallScaleFading_Vehicular_Doppler_CoherenceBW",
        "description": "小尺度衰落 + 车载 + 多普勒扩展 + 相干带宽",
    },
    {
        "query": '"fading margin" V2X "link budget"',
        "label": "Q16_FadingMargin_V2X_LinkBudget",
        "description": "衰落裕量 + V2X + 链路预算",
    },
    {
        "query": '"path loss" "spatial correlation" vehicular "coherence distance"',
        "label": "Q17_PathLoss_SpatialCorrelation_Vehicular_CoherenceDistance",
        "description": "路径损耗 + 空间相关 + 车载 + 相干距离",
    },
    {
        "query": '"PU activity model" Markov "cognitive radio" "sojourn time"',
        "label": "Q18_PUActivityModel_Markov_CR_SojournTime",
        "description": "PU活动模型 + Markov + 认知无线电 + 驻留时间",
    },
]


def main():
    config = load_config()
    delay = max(config.get("ieee_subscriber", {}).get("delay_seconds", 3), 3)

    # 输出目录
    out_dir = Path(__file__).resolve().parent.parent / "metadata" / "doppler_search"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_papers = {}  # dedup_id -> paper
    query_results = {}  # label -> count

    print("=" * 60)
    print("📡 多普勒效应 + CVN 信道关键词批量检索")
    print(f"   共 {len(DOPPLER_QUERIES)} 组关键词")
    print(f"   请求延迟: {delay}s")
    print(f"   输出目录: {out_dir}")
    print("=" * 60)

    for i, q in enumerate(DOPPLER_QUERIES):
        label = q["label"]
        query = q["query"]
        desc = q["description"]

        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(DOPPLER_QUERIES)}] {label}")
        print(f"  查询: {query[:80]}...")
        print(f"  描述: {desc}")

        try:
            papers = search_by_keyword(query, max_results=30)

            new_count = 0
            for p in papers:
                dedup_id = p.get("dedup_id", "")
                if dedup_id and dedup_id not in all_papers:
                    p["query_label"] = label
                    p["query_description"] = desc
                    all_papers[dedup_id] = p
                    new_count += 1
                elif dedup_id and dedup_id in all_papers:
                    # 追加查询标签
                    existing_labels = all_papers[dedup_id].get("query_label", "")
                    if label not in existing_labels:
                        all_papers[dedup_id]["query_label"] = existing_labels + "; " + label

            query_results[label] = {
                "total_returned": len(papers),
                "new_added": new_count,
                "description": desc,
            }
            print(f"  → 返回 {len(papers)} 篇, 新增 {new_count} 篇, 累计 {len(all_papers)} 篇")

        except Exception as e:
            print(f"  ❌ 查询失败: {e}")
            query_results[label] = {
                "total_returned": 0,
                "new_added": 0,
                "description": desc,
                "error": str(e),
            }

        # 请求间延迟
        if i < len(DOPPLER_QUERIES) - 1:
            wait = delay + random.uniform(1, 3)
            print(f"  ⏳ 等待 {wait:.1f}s...")
            time.sleep(wait)

    # =============================================
    # 输出 CSV
    # =============================================
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    csv_path = out_dir / f"doppler_search_{timestamp}.csv"

    fieldnames = [
        "dedup_id",
        "title",
        "authors",
        "first_author",
        "first_author_lastname",
        "year",
        "published_date",
        "summary",
        "doi",
        "arxiv_id",
        "journal_ref",
        "source",
        "url",
        "arxiv_url",
        "query_label",
        "query_description",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for paper in all_papers.values():
            writer.writerow(paper)

    print(f"\n{'='*60}")
    print(f"✅ 检索完成！")
    print(f"   总论文数（去重后）: {len(all_papers)}")
    print(f"   输出文件: {csv_path}")
    print(f"\n{'='*60}")
    print("各组查询统计:")
    print(f"{'Label':<45} {'返回':>6} {'新增':>6} 描述")
    print("-" * 80)
    for label, info in query_results.items():
        desc = info.get("description", "")[:30]
        err = info.get("error", "")
        status = f"❌ {err[:20]}" if err else ""
        print(f"{label:<45} {info['total_returned']:>6} {info['new_added']:>6}  {desc}{'  ' + status if status else ''}")


if __name__ == "__main__":
    main()
