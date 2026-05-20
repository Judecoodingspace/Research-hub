# -*- coding: utf-8 -*-
"""
Papercard 自动生成器
根据从 arXiv 拉取的论文元数据，按 Agents.md 规则生成结构化简报

功能：
1. 读取 metadata CSV 或 fetcher 输出的论文列表
2. 对高相关/中相关论文，生成结构化 papercard（11 条规则的精简版）
3. 更新主题索引 (papercard/<topic>/index.md)
4. 更新总索引 (paper_index.md)
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# =============================================
# 路径工具
# =============================================

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent

# =============================================
# Papercard 模板 — 基于 Agents.md 的 11 条规则
# =============================================

PAPERCARD_TEMPLATE = """# {first_author_lastname} {year} — {short_title}

> **来源**：{journal_ref} | arXiv: {arxiv_id}
> **作者**：{authors}
> **采集日期**：{fetch_date} | 相关性：{relevance} | 归类：{category_label}
> **arXiv URL**：{arxiv_url}

---

## 相关性 / 标签
- **相关性等级**：{relevance_cn}
- **子方向标签**：{sub_tags_str}
- **判断理由**：{relevance_reason}

---

## 1. Problem

{problem_section}

---

## 2. Setting / Assumptions

| 维度 | 设定 |
|------|------|
| 节点数量 | {setting_nodes} |
| 基础设施 | {setting_infrastructure} |
| 算力条件 | {setting_compute} |
| 通信条件 | {setting_communication} |
| 感知条件 | {setting_perception} |
| 移动性 | {setting_mobility} |
| 任务模型 | {setting_task} |
| 模型部署 | {setting_model_deploy} |
| 视角关系 | {setting_view} |
| 模态范围 | {setting_modality} |

---

## 3. Core Idea

{core_idea}

---

## 4. Key Mechanism

{key_mechanism}

---

## 5. Experiments

{experiments}

---

## 6. Strength

{strength}

---

## 7. Weakness & Limitation

{weakness}

---

## 8. Reusable Part

{reusable_part}

---

## 9. Attack Point / Improvement Direction

{attack_point}

---

## 10. Relation to My Topic

{relation_to_my_topic}

---

## 11. Scenario-Experiment Justification

### 11.1 Scenario → Algorithm Mapping

{scenario_algo_mapping}

### 11.2 Ablation & Necessity Evidence

{ablation_evidence}

### 11.3 "Why Not Simpler" Logic

{why_not_simpler}

### 11.4 Defensibility Summary

{defensibility_summary}

---

> ⚠️ **自动生成标记**：此 papercard 由 arXiv 订阅系统自动生成（基于摘要元数据）。深度分析（完整 11 条 + 对照主线）需人工补充 PDF 精读。标记为 `[AUTO]` 的条目为机器推断，需人工验证。
"""

# =============================================
# 智能内容生成（基于摘要 + 关键词的启发式推断）
# =============================================

def generate_papercard_content(paper: Dict) -> Dict:
    """
    根据论文元数据（标题+摘要+分类）自动推断 papercard 各条目内容。
    
    此函数是启发式的——基于摘要中的关键词和句式推断 11 条规则的内容。
    生成的 papercard 标记为 [AUTO]，需人工审核后补充精读内容。
    """
    
    title = paper.get("title", "")
    summary = paper.get("summary", "")
    authors = paper.get("authors", "")
    categories = paper.get("categories", "")
    sub_tags = paper.get("sub_tags", [])
    relevance = paper.get("relevance", "low")
    category = paper.get("category", "Uncategorized")
    
    full_text = (title + " " + summary).lower()
    
    # --- 1. Problem ---
    problem_bias = infer_problem_bias(full_text)
    problem_section = f"""**摘要推断**：{summary[:300]}...

**问题偏向**（自动推断）：{problem_bias}

> [AUTO] 此推断基于摘要关键词。完整分析需 PDF 精读。"""

    # --- 2. Setting / Assumptions ---
    settings = infer_settings(full_text, title)
    
    # --- 3. Core Idea ---
    core_idea = infer_core_idea(title, summary)
    
    # --- 4. Key Mechanism ---
    key_mechanism = infer_key_mechanism(full_text, title)
    
    # --- 5. Experiments ---
    experiments = infer_experiments(full_text)
    
    # --- 6. Strength ---
    strength = infer_strength(full_text, title)
    
    # --- 7. Weakness ---
    weakness = infer_weakness(full_text, title)
    
    # --- 8. Reusable Part ---
    reusable_part = infer_reusable_part(full_text, title)
    
    # --- 9. Attack Point ---
    attack_point = infer_attack_point(full_text, title)
    
    # --- 10. Relation to My Topic ---
    relation = infer_relation(full_text, title, category, sub_tags)
    
    # --- 11. Scenario-Experiment Justification ---
    scen_algo = infer_scenario_algo_mapping(full_text, title)
    ablation = "> [AUTO] 需 PDF 精读后补充消融实验分析。"
    why_not = "> [AUTO] 需 PDF 精读后补充替代方案排除逻辑分析。"
    defense = "> [AUTO] 需 PDF 精读后补充可防御性总结。"
    
    # 组装
    content = {
        "first_author_lastname": paper.get("first_author_lastname", "Unknown"),
        "year": paper.get("year", "????"),
        "short_title": shorten_title(title),
        "journal_ref": paper.get("journal_ref", "arXiv preprint"),
        "arxiv_id": paper.get("arxiv_id", ""),
        "authors": authors[:200] + ("..." if len(authors) > 200 else ""),
        "fetch_date": datetime.now().strftime("%Y-%m-%d"),
        "relevance": relevance.upper(),
        "relevance_cn": {"high": "🔴 高相关", "medium": "🟡 中相关", "low": "⚪ 低相关"}.get(relevance, "⚪ 低相关"),
        "category_label": paper.get("category", "Uncategorized"),
        "arxiv_url": paper.get("arxiv_url", ""),
        "sub_tags_str": "; ".join(sub_tags[:5]) if sub_tags else "待标注",
        "relevance_reason": infer_relevance_reason(full_text, category),
        "problem_section": problem_section,
        "setting_nodes": settings["nodes"],
        "setting_infrastructure": settings["infrastructure"],
        "setting_compute": settings["compute"],
        "setting_communication": settings["communication"],
        "setting_perception": settings["perception"],
        "setting_mobility": settings["mobility"],
        "setting_task": settings["task"],
        "setting_model_deploy": settings["model_deploy"],
        "setting_view": settings["view"],
        "setting_modality": settings["modality"],
        "core_idea": core_idea,
        "key_mechanism": key_mechanism,
        "experiments": experiments,
        "strength": strength,
        "weakness": weakness,
        "reusable_part": reusable_part,
        "attack_point": attack_point,
        "relation_to_my_topic": relation,
        "scenario_algo_mapping": scen_algo,
        "ablation_evidence": ablation,
        "why_not_simpler": why_not,
        "defensibility_summary": defense,
    }
    
    return content


# =============================================
# 启发式推断函数
# =============================================

def shorten_title(title: str) -> str:
    """缩短标题用于文件名"""
    # 取前 80 字符，在单词边界截断
    if len(title) <= 80:
        return title
    short = title[:80]
    # 回退到最后一个空格
    last_space = short.rfind(" ")
    return short[:last_space] if last_space > 0 else short

def infer_problem_bias(text: str) -> str:
    """推断问题偏向"""
    biases = []
    if any(kw in text for kw in ["detection", "recognition", "classification", "segmentation", "accuracy"]):
        biases.append("感知质量不足")
    if any(kw in text for kw in ["bandwidth", "latency", "transmission", "communication overhead", "redundant"]):
        biases.append("传输效率不足")
    if any(kw in text for kw in ["real-time", "inference", "computation", "resource-constrained", "edge"]):
        biases.append("推理/计算实时性不足")
    if any(kw in text for kw in ["cooperative", "collaboration", "coordination", "multi-agent", "swarm"]):
        biases.append("协同机制不足")
    if any(kw in text for kw in ["resource allocation", "scheduling", "energy", "power", "offloading"]):
        biases.append("资源分配不合理")
    if any(kw in text for kw in ["trajectory", "path planning", "coverage", "navigation"]):
        biases.append("路径/轨迹规划与任务目标脱节")
    if any(kw in text for kw in ["multi-modal", "multimodal", "fusion", "heterogeneous data"]):
        biases.append("多模态/多源信息未统一建模")
    if any(kw in text for kw in ["when to", "trigger", "select", "decision", "conditional"]):
        biases.append("决策触发条件不明确")
    
    return " + ".join(biases) if biases else "待确认（需 PDF 精读）"

def infer_settings(text: str, title: str) -> Dict:
    """推断场景设定"""
    # 节点数量
    if any(kw in text for kw in ["multi-uav", "multi uav", "multiple uavs", "swarm", "multiple drones"]):
        nodes = "多 UAV / 无人机集群"
    elif any(kw in text for kw in ["vehicular", "vehicle", "connected vehicle", "car"]):
        nodes = "车联网多车"
    elif any(kw in text for kw in ["multi-user", "multi user", "multiple users"]):
        nodes = "多用户"
    elif any(kw in text for kw in ["single uav", "single drone", "a uav", "one uav"]):
        nodes = "单 UAV"
    else:
        nodes = "待确认"
    
    # 基础设施
    if any(kw in text for kw in ["edge server", "mec", "edge computing", "fog", "cloud"]):
        infra = "有边缘服务器/云端"
    else:
        infra = "未明确提及（待确认）"
    
    # 算力
    if any(kw in text for kw in ["heterogeneous", "resource-constrained", "limited computational"]):
        compute = "异构算力 / 端侧受限"
    else:
        compute = "待确认"
    
    # 通信
    if any(kw in text for kw in ["awgn", "rayleigh", "fading", "snr", "bandwidth constrained"]):
        comm = "受限信道（衰落/噪声建模）"
    elif any(kw in text for kw in ["perfect channel", "ideal communication"]):
        comm = "完美信道"
    else:
        comm = "待确认"
    
    # 感知
    if any(kw in text for kw in ["noise", "occlusion", "degraded", "low-quality", "low resolution"]):
        perc = "含噪声/退化/遮挡"
    else:
        perc = "待确认（摘要未提及感知退化）"
    
    # 移动性
    if any(kw in text for kw in ["trajectory", "path", "mobility", "moving", "dynamic"]):
        mob = "动态轨迹"
    elif any(kw in text for kw in ["fixed", "stationary"]):
        mob = "固定位置"
    else:
        mob = "待确认"
    
    # 任务模型
    if any(kw in text for kw in ["dynamic task", "task flow", "task scheduling", "task allocation"]):
        task = "动态任务 / 任务流"
    else:
        task = "固定任务（待确认）"
    
    # 模型部署
    if any(kw in text for kw in ["split", "partition", "offload", "model splitting"]):
        deploy = "讨论分割推理/卸载"
    else:
        deploy = "未明确讨论（待确认）"
    
    # 视角
    if any(kw in text for kw in ["multi-view", "multi view", "multiple views", "complementary"]):
        view = "多视角协同"
    elif any(kw in text for kw in ["single view", "single camera"]):
        view = "单视角"
    else:
        view = "待确认"
    
    # 模态
    if any(kw in text for kw in ["multi-modal", "multimodal", "rgb+depth", "text+image", "text and image"]):
        mod = "多模态"
    else:
        mod = "单模态（主要 RGB 图像，待确认）"
    
    return {
        "nodes": nodes,
        "infrastructure": infra,
        "compute": compute,
        "communication": comm,
        "perception": perc,
        "mobility": mob,
        "task": task,
        "model_deploy": deploy,
        "view": view,
        "modality": mod,
    }

def infer_core_idea(title: str, summary: str) -> str:
    """推断核心思想"""
    text = (title + " " + summary).lower()
    
    ideas = []
    if any(kw in text for kw in ["task-oriented", "task oriented"]):
        ideas.append(f"围绕下游任务目标（而非数据重建质量）优化{'通信' if 'communication' in text else '系统'}决策")
    if any(kw in text for kw in ["semantic", "semantics"]):
        ideas.append(f"利用语义信息指导{'传输' if 'transmission' in text else '处理'}，去除冗余、保留任务相关特征")
    if any(kw in text for kw in ["cooperative", "collaboration", "multi-uav"]):
        ideas.append("通过多节点协同弥补单节点视角/算力不足")
    if any(kw in text for kw in ["reinforcement learning", "deep reinforcement", "drl"]):
        ideas.append("用学习型策略替代固定规则，适应动态环境")
    if any(kw in text for kw in ["selection", "select", "choose", "which"]):
        ideas.append("引入选择/触发机制——不是所有节点/数据都需要参与")
    if any(kw in text for kw in ["split", "partition", "offload"]):
        ideas.append("将模型在端-边之间动态切分以平衡计算负载与通信开销")
    
    if ideas:
        return "**" + "；".join(ideas[:3]) + "**。\n\n> [AUTO] 基于摘要推断，核心思想需 PDF 精读后深化。"
    else:
        return f"**摘要推断**：{summary[:200]}...\n\n> [AUTO] 需 PDF 精读后提炼核心思想。"

def infer_key_mechanism(text: str, title: str) -> str:
    """推断关键机制"""
    mechanisms = []
    
    if any(kw in text for kw in ["reinforcement learning", "drl", "q-learning", "policy gradient", "ddqn"]):
        mechanisms.append("- **学习范式**：深度强化学习（DRL），通过与环境交互学习最优策略")
    if any(kw in text for kw in ["optimization", "convex", "lagrange", "lyapunov"]):
        mechanisms.append("- **优化方法**：数学优化（凸优化/Lyapunov/Lagrange），求解析或迭代解")
    if any(kw in text for kw in ["semantic", "feature extraction", "encoder", "autoencoder"]):
        mechanisms.append("- **语义表征**：语义编码器提取任务相关特征，压缩传输数据量")
    if any(kw in text for kw in ["split", "partition", "offload", "edge inference"]):
        mechanisms.append("- **计算卸载**：模型切分/任务卸载到边缘节点，平衡端边负载")
    if any(kw in text for kw in ["selection", "select", "threshold", "gate"]):
        mechanisms.append("- **选择/门控机制**：根据条件（相似度/阈值/效用）选择性激活节点或特征")
    if any(kw in text for kw in ["query", "key", "matching", "similarity"]):
        mechanisms.append("- **匹配机制**：Query-Key 相似度匹配，实现语义级别的源选择")
    if any(kw in text for kw in ["federated", "distributed training"]):
        mechanisms.append("- **训练范式**：联邦学习/分布式训练，保护数据隐私的同时协同训练")
    if any(kw in text for kw in ["fusion", "merge", "aggregate"]):
        mechanisms.append("- **融合策略**：多源特征加权融合，整合互补信息")
    if any(kw in text for kw in ["transformer", "attention", "vit", "swin"]):
        mechanisms.append("- **模型架构**：Transformer/Attention 机制，捕获长程依赖和任务相关区域")
    
    if not mechanisms:
        mechanisms.append(f"> [AUTO] 摘要信息不足以推断关键机制。需 PDF 精读。\n> 摘要提示：{text[:300]}...")
    
    return "\n".join(mechanisms)

def infer_experiments(text: str) -> str:
    """推断实验设置"""
    parts = []
    
    # 数据集
    datasets = []
    for ds in ["cifar", "imagenet", "coco", "visdrone", "uavdt", "aid", "ucf", "kitti", 
               "cityscapes", "pascal voc", "mnist", "sentinel", "landsat"]:
        if ds in text:
            datasets.append(ds.upper())
    if datasets:
        parts.append(f"- **可能数据集**：{', '.join(datasets)}（摘要提及）")
    
    # 对比方法
    if "baseline" in text or "compared" in text or "benchmark" in text:
        parts.append("- **对比评估**：摘要提及与 baseline/benchmark 对比")
    
    # 指标
    metrics = []
    for m in ["accuracy", "precision", "recall", "f1", "iou", "latency", "throughput", 
              "energy", "bandwidth", "mse", "psnr", "ssim"]:
        if m in text:
            metrics.append(m)
    if metrics:
        parts.append(f"- **可能指标**：{', '.join(metrics)}")
    
    if not parts:
        parts.append("> [AUTO] 摘要未提供足够实验细节，需 PDF 精读补充。")
    
    parts.append("\n> [AUTO] 完整实验分析（baseline 合理性、消融实验、鲁棒性测试）需 PDF 精读。")
    return "\n".join(parts)

def infer_strength(text: str, title: str) -> str:
    """推断优点"""
    strengths = []
    if any(kw in text for kw in ["novel", "new framework", "first", "pioneer"]):
        strengths.append("- 提出了新的系统框架/架构")
    if any(kw in text for kw in ["joint", "jointly", "co-optimize", "simultaneously"]):
        strengths.append("- 联合优化多个相互耦合的维度")
    if "real-world" in text or "real world" in text or "deploy" in text:
        strengths.append("- 考虑了实际部署约束")
    if any(kw in text for kw in ["outperform", "superior", "state-of-the-art", "better"]):
        strengths.append("- 实验结果显示优于现有方法")
    
    if not strengths:
        strengths.append("> [AUTO] 需 PDF 精读后评估。")
    else:
        strengths.append("\n> [AUTO] 以上基于摘要表述推断，具体贡献强度需 PDF 精读验证。")
    return "\n".join(strengths)

def infer_weakness(text: str, title: str) -> str:
    """推断局限"""
    weaknesses = []
    
    text_lower = text.lower()
    
    # 通过"缺失"推断
    if "single" in text_lower and "multi" not in text_lower:
        weaknesses.append("- ⚠️ 可能未涉及多节点协同（仅单机场景）")
    if "simulation" in text_lower or "simulated" in text_lower:
        weaknesses.append("- ⚠️ 可能仅在仿真环境验证，缺少真实平台部署实验")
    if "perfect" in text_lower:
        weaknesses.append("- ⚠️ 可能假设完美信道/完美感知，实际部署鲁棒性存疑")
    if "fixed" in text_lower:
        weaknesses.append("- ⚠️ 可能假设固定拓扑/固定任务，动态适应性不足")
    if "centralized" in text_lower or "central" in text_lower:
        weaknesses.append("- ⚠️ 可能采用集中式架构，单点故障风险和通信瓶颈")
    if "known" in text_lower and "csi" in text_lower:
        weaknesses.append("- ⚠️ 可能假设完全已知 CSI，实际信道估计误差未考虑")
    
    weaknesses.append("\n> [AUTO] 以上为基于摘要关键词的初步推断，完整的局限性分析需 PDF 精读。")
    return "\n".join(weaknesses) if len(weaknesses) > 1 else "> [AUTO] 需 PDF 精读后分析。"

def infer_reusable_part(text: str, title: str) -> str:
    """推断可复用内容"""
    parts = []
    if "system model" in text or "framework" in text:
        parts.append("- **系统建模方式**：可参考其系统架构和问题定义框架")
    if "metric" in text or "evaluation" in text:
        parts.append("- **指标体系**：可借鉴其评估维度和指标设计")
    if "reinforcement learning" in text:
        parts.append("- **RL 设计**：可参考其状态/动作/奖励函数设计")
    if "semantic" in text:
        parts.append("- **语义表征思路**：可借鉴其语义编码和压缩方案")
    
    if not parts:
        parts.append("> [AUTO] 需 PDF 精读后评估可复用内容。")
    else:
        parts.append("\n> [AUTO] 具体复用方式需 PDF 精读确认。")
    return "\n".join(parts)

def infer_attack_point(text: str, title: str) -> str:
    """推断可改进点"""
    points = []
    text_lower = text.lower()
    
    if "semantic" not in text_lower and "task-oriented" not in text_lower:
        points.append("- **缺少任务导向优化**：可能仍以数据重建为目标而非任务完成质量")
    if "multi-uav" not in text_lower and "swarm" not in text_lower:
        points.append("- **缺少多 UAV 协同**：可能仅在单机场景验证，多机扩展未讨论")
    if "heterogeneous" not in text_lower:
        points.append("- **缺少异构算力建模**：可能假设所有节点算力同构")
    if "modality" not in text_lower and "multimodal" not in text_lower:
        points.append("- **缺少多模态融合**：可能仅处理单一模态（RGB）")
    if "trajectory" not in text_lower and "path" not in text_lower:
        points.append("- **缺少路径-通信-推理联动**：路径规划与下游任务未耦合")
    
    if not points:
        points.append("> [AUTO] 需 PDF 精读后识别可攻击的薄弱环节。")
    return "\n".join(points)

def infer_relation(text: str, title: str, category: str, sub_tags: List[str]) -> str:
    """推断与当前研究主线的关系"""
    relations = []
    
    # 基于归类的方向给出关系判断
    if "Semantic" in category or "semantic" in text.lower():
        relations.append("- 与当前 **多无人机协同语义通信** 主线直接相关")
        relations.append("- 可支撑任务导向传输、语义源选择等子方向的文献综述")
    if "Resource" in category:
        relations.append("- 为当前研究中的 **资源分配与调度** 模块提供参考 baseline")
    if "Split" in category:
        relations.append("- 与当前 **端边协同推理** 方向相关，可参考其切分策略")
    if "LLM" in category:
        relations.append("- 为当前工作中的 **多模态推理/语义判断** 提供前沿参考")
    if "Fire" in category:
        relations.append("- 为 **无人机火险感知** 应用场景提供方法参考")
    if "CVN" in category or "DSA" in category:
        relations.append("- 为 **认知车联网频谱接入** 研究提供对比参考文献")
    
    relations.append("\n> [AUTO] 精确关系定位需对照主线文档 + PDF 精读后确定。")
    return "\n".join(relations) if relations else "> [AUTO] 需对照主线文档评估关系。"

def infer_scenario_algo_mapping(text: str, title: str) -> str:
    """推断场景-算法映射"""
    mappings = []
    text_lower = text.lower()
    
    if "bandwidth" in text_lower or "limited" in text_lower:
        mappings.append("| 带宽受限 | 需要压缩/选择传输 | 语义编码/源选择 | 中（待验证） |")
    if "real-time" in text_lower or "latency" in text_lower:
        mappings.append("| 实时性要求 | 需要低延迟推理 | 边缘计算/模型轻量化 | 中（待验证） |")
    if "dynamic" in text_lower or "varying" in text_lower:
        mappings.append("| 环境动态变化 | 需要自适应策略 | 学习型决策（DRL） | 中（待验证） |")
    
    if not mappings:
        return "> [AUTO] 需 PDF 精读后建立场景特征→算法选择的因果链。"
    
    header = "| 场景特征 | 引发的技术需求 | 选择的算法/模型 | 必要性强度 |\n|---|---|---|---|\n"
    return header + "\n".join(mappings) + "\n\n> [AUTO] 必要性强度需 PDF 精读后评估。"

def infer_relevance_reason(text: str, category: str) -> str:
    """推断相关性理由"""
    reasons = []
    
    if "uav" in text.lower() or "drone" in text.lower():
        reasons.append("涉及 UAV/无人机场景")
    if "semantic" in text.lower():
        reasons.append("涉及语义通信/语义表征")
    if "task-oriented" in text.lower() or "task oriented" in text.lower():
        reasons.append("明确任务导向优化")
    if "multi" in text.lower() and ("uav" in text.lower() or "agent" in text.lower()):
        reasons.append("涉及多节点/多智能体协同")
    if "communication" in text.lower():
        reasons.append("以通信效率为核心关注点")
    if "edge" in text.lower() or "onboard" in text.lower():
        reasons.append("涉及边缘/端侧计算")
    
    return "；".join(reasons) if reasons else f"自动归类至 {category}，需人工审核相关性"

# =============================================
# Papercard 写入与索引更新
# =============================================

def generate_filename(paper: Dict) -> str:
    """生成 papercard 文件名"""
    year = paper.get("year", "????")
    lastname = paper.get("first_author_lastname", "Unknown")
    short_title = shorten_title(paper.get("title", "Untitled"))
    # 清理文件名中的特殊字符
    safe_title = re.sub(r'[<>:"/\\|?*]', '', short_title)
    safe_title = safe_title.replace(" ", "_")[:60]
    return f"{year}_{lastname}_{safe_title}.md"

def write_papercard(paper: Dict, content: Dict, category_folder: str) -> Path:
    """将 papercard 写入文件"""
    # 创建目标目录
    card_dir = get_project_root() / "papercard" / category_folder
    card_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成内容
    papercard_text = PAPERCARD_TEMPLATE.format(**content)
    
    # 写入
    filename = generate_filename(paper)
    filepath = card_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(papercard_text)
    
    print(f"  ✅ Papercard 已生成: papercard/{category_folder}/{filename}")
    return filepath

def update_topic_index(category_folder: str, paper: Dict, filepath: Path):
    """更新主题索引 papercard/<topic>/index.md"""
    index_dir = get_project_root() / "papercard" / category_folder
    index_path = index_dir / "index.md"
    
    title = paper.get("title", "Untitled")
    year = paper.get("year", "????")
    authors = paper.get("authors", "")
    relevance = paper.get("relevance", "low")
    filename = filepath.name
    
    # 索引条目
    entry = f"| {year} | {authors[:50]}... | [{title[:60]}...]({filename}) | {relevance.upper()} | {datetime.now().strftime('%Y-%m-%d')} |"
    
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            existing = f.read()
        
        if filename not in existing:
            # 在第一个空行前插入
            with open(index_path, "a", encoding="utf-8") as f:
                f.write(f"\n{entry}")
    else:
        # 创建新索引
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(f"""# {category_folder} 文献索引

## 使用说明
- 本索引追踪该主题下所有已生成的 paper card
- [AUTO] 标记 = arXiv 自动生成，[REVIEWED] = 已人工精读

## 论文列表

| 年份 | 作者 | 标题 | 相关性 | 生成日期 |
|------|------|------|--------|----------|
{entry}
""")
    
    print(f"  📋 主题索引已更新: papercard/{category_folder}/index.md")

def update_main_index(category_folder: str):
    """更新总索引 paper_index.md"""
    index_path = get_project_root() / "paper_index.md"
    
    if not index_path.exists():
        print("  ⚠️ paper_index.md 不存在，跳过更新")
        return
    
    with open(index_path, "r", encoding="utf-8") as f:
        existing = f.read()
    
    # 检查是否已有该主题的记录
    topic_index_ref = f"`papercard/{category_folder}/index.md`"
    if topic_index_ref in existing:
        # 已存在，更新状态
        card_dir = get_project_root() / "papercard" / category_folder
        md_files = list(card_dir.glob("*.md"))
        auto_count = sum(1 for f in md_files if f.name != "index.md")
        
        # 简单替换状态
        old_pattern = f"| {category_folder} |"
        # 不做复杂替换，仅标记有更新
        import re
        pattern = re.compile(rf'(\| {re.escape(category_folder)} \|.*\|.*\| )(.+?)( \|)', re.DOTALL)
        match = pattern.search(existing)
        if match:
            new_status = f"已有 {auto_count} 篇 paper card (含自动生成)"
            updated = existing[:match.start(2)] + new_status + existing[match.end(2):]
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"  📊 总索引已更新: paper_index.md")
    else:
        print(f"  ℹ️ paper_index.md 中无 {category_folder} 记录，需手动添加或运行专用更新脚本")

# =============================================
# 批量生成入口
# =============================================

def run_papercard_generation(papers: List[Dict], min_relevance: str = "medium") -> Dict:
    """
    对论文列表批量生成 papercard
    
    参数:
        papers: fetcher 返回的论文列表（已包含 relevance/category 字段）
        min_relevance: 最低生成等级 ("high" | "medium" | "low")
    
    返回:
        统计信息 dict
    """
    stats = {
        "total": len(papers),
        "generated": 0,
        "skipped_low": 0,
        "errors": 0,
        "generated_list": [],
    }
    
    relevance_order = {"high": 3, "medium": 2, "low": 1}
    min_level = relevance_order.get(min_relevance, 2)
    
    print(f"\n{'='*60}")
    print(f"📝 开始生成 Papercard (最低等级: {min_relevance})")
    print(f"{'='*60}")
    
    for paper in papers:
        relevance = paper.get("relevance", "low")
        
        if relevance_order.get(relevance, 0) < min_level:
            stats["skipped_low"] += 1
            continue
        
        category = paper.get("category", "Uncategorized")
        title = paper.get("title", "Untitled")[:80]
        
        print(f"\n📄 [{relevance.upper()}] {title}...")
        
        try:
            # 生成内容
            content = generate_papercard_content(paper)
            
            # 写入文件
            filepath = write_papercard(paper, content, category)
            
            # 更新索引
            update_topic_index(category, paper, filepath)
            update_main_index(category)
            
            stats["generated"] += 1
            stats["generated_list"].append({
                "title": paper.get("title"),
                "category": category,
                "relevance": relevance,
                "filepath": str(filepath.relative_to(get_project_root())),
            })
            
        except Exception as e:
            print(f"  ❌ 生成失败: {e}")
            stats["errors"] += 1
    
    return stats


if __name__ == "__main__":
    # 独立运行时：从 fetcher 获取论文并生成 papercard
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from fetcher import run_arxiv_fetch
    
    # 1. 拉取论文
    papers, csv_path = run_arxiv_fetch()
    
    if not papers:
        print("没有新论文，退出。")
        sys.exit(0)
    
    # 2. 生成 papercard
    stats = run_papercard_generation(papers, min_relevance="medium")
    
    print(f"\n{'='*60}")
    print(f"✨ Papercard 生成完成!")
    print(f"   总论文数: {stats['total']}")
    print(f"   已生成: {stats['generated']} 篇")
    print(f"   跳过(低相关): {stats['skipped_low']} 篇")
    print(f"   错误: {stats['errors']} 篇")
    
    if stats["generated_list"]:
        print(f"\n📋 生成列表:")
        for g in stats["generated_list"]:
            print(f"   [{g['relevance'].upper()}] {g['filepath']}")
