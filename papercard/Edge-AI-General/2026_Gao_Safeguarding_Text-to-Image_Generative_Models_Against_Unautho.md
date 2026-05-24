# Gao 2026 — Safeguarding Text-to-Image Generative Models Against Unauthorized Knowledge

> **来源**：arXiv preprint | arXiv: 2605.22060
> **作者**：Yilan Gao; Sida Huang; Hongyuan Zhang; Xuelong Li
> **采集日期**：2026-05-24 | 相关性：MEDIUM | 归类：Edge-AI-General
> **arXiv URL**：https://arxiv.org/abs/2605.22060

---

## 相关性 / 标签
- **相关性等级**：🟡 中相关
- **子方向标签**：knowledge distillation edge deployment
- **判断理由**：涉及边缘/端侧计算

---

## 1. Problem

**摘要推断**：Closed-weight generative services are increasingly deployed through query-based APIs, where users can obtain generated outputs while model parameters remain inaccessible. However, such deployment does not prevent model stealing: an attacker can repeatedly query the service, collect large volumes of ...

**问题偏向**（自动推断）：推理/计算实时性不足

> [AUTO] 此推断基于摘要关键词。完整分析需 PDF 精读。

---

## 2. Setting / Assumptions

| 维度 | 设定 |
|------|------|
| 节点数量 | 待确认 |
| 基础设施 | 未明确提及（待确认） |
| 算力条件 | 待确认 |
| 通信条件 | 待确认 |
| 感知条件 | 待确认（摘要未提及感知退化） |
| 移动性 | 待确认 |
| 任务模型 | 固定任务（待确认） |
| 模型部署 | 未明确讨论（待确认） |
| 视角关系 | 待确认 |
| 模态范围 | 单模态（主要 RGB 图像，待确认） |

---

## 3. Core Idea

**摘要推断**：Closed-weight generative services are increasingly deployed through query-based APIs, where users can obtain generated outputs while model parameters remain inaccessible. However, such deployment does...

> [AUTO] 需 PDF 精读后提炼核心思想。

---

## 4. Key Mechanism

- **选择/门控机制**：根据条件（相似度/阈值/效用）选择性激活节点或特征
- **匹配机制**：Query-Key 相似度匹配，实现语义级别的源选择

---

## 5. Experiments

> [AUTO] 摘要未提供足够实验细节，需 PDF 精读补充。

> [AUTO] 完整实验分析（baseline 合理性、消融实验、鲁棒性测试）需 PDF 精读。

---

## 6. Strength

- 考虑了实际部署约束

> [AUTO] 以上基于摘要表述推断，具体贡献强度需 PDF 精读验证。

---

## 7. Weakness & Limitation

- ⚠️ 可能未涉及多节点协同（仅单机场景）

> [AUTO] 以上为基于摘要关键词的初步推断，完整的局限性分析需 PDF 精读。

---

## 8. Reusable Part

- **系统建模方式**：可参考其系统架构和问题定义框架

> [AUTO] 具体复用方式需 PDF 精读确认。

---

## 9. Attack Point / Improvement Direction

- **缺少任务导向优化**：可能仍以数据重建为目标而非任务完成质量
- **缺少多 UAV 协同**：可能仅在单机场景验证，多机扩展未讨论
- **缺少异构算力建模**：可能假设所有节点算力同构
- **缺少多模态融合**：可能仅处理单一模态（RGB）
- **缺少路径-通信-推理联动**：路径规划与下游任务未耦合

---

## 10. Relation to My Topic


> [AUTO] 精确关系定位需对照主线文档 + PDF 精读后确定。

---

## 11. Scenario-Experiment Justification

### 11.1 Scenario → Algorithm Mapping

> [AUTO] 需 PDF 精读后建立场景特征→算法选择的因果链。

### 11.2 Ablation & Necessity Evidence

> [AUTO] 需 PDF 精读后补充消融实验分析。

### 11.3 "Why Not Simpler" Logic

> [AUTO] 需 PDF 精读后补充替代方案排除逻辑分析。

### 11.4 Defensibility Summary

> [AUTO] 需 PDF 精读后补充可防御性总结。

---

> ⚠️ **自动生成标记**：此 papercard 由 arXiv 订阅系统自动生成（基于摘要元数据）。深度分析（完整 11 条 + 对照主线）需人工补充 PDF 精读。标记为 `[AUTO]` 的条目为机器推断，需人工验证。
