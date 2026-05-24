# Ji 2025 — A Hybrid Scheduling Approach for Optimizing UAV-Assisted Edge Computing toward

> **来源**：2025 IEEE International Conference on Unmanned Systems (ICUS) | arXiv: 
> **作者**：Y. Ji; Xinyue Du; Chu-ge Wu
> **采集日期**：2026-05-24 | 相关性：MEDIUM | 归类：UAV-LLM
> **arXiv URL**：

---

## 相关性 / 标签
- **相关性等级**：🟡 中相关
- **子方向标签**：uav llm inference edge
- **判断理由**：涉及 UAV/无人机场景；涉及多节点/多智能体协同；涉及边缘/端侧计算

---

## 1. Problem

**摘要推断**：Large Language Models (LLMs) play an important role in robotics and embodied intelligence system at the edge, enabling capabilities such as multi-modal data processing, real-time natural language interaction, complex task planning and autonomous decision making. However, numerous resource constraine...

**问题偏向**（自动推断）：传输效率不足 + 推理/计算实时性不足 + 资源分配不合理 + 多模态/多源信息未统一建模 + 决策触发条件不明确

> [AUTO] 此推断基于摘要关键词。完整分析需 PDF 精读。

---

## 2. Setting / Assumptions

| 维度 | 设定 |
|------|------|
| 节点数量 | 车联网多车 |
| 基础设施 | 有边缘服务器/云端 |
| 算力条件 | 待确认 |
| 通信条件 | 待确认 |
| 感知条件 | 待确认（摘要未提及感知退化） |
| 移动性 | 待确认 |
| 任务模型 | 固定任务（待确认） |
| 模型部署 | 未明确讨论（待确认） |
| 视角关系 | 待确认 |
| 模态范围 | 多模态 |

---

## 3. Core Idea

**引入选择/触发机制——不是所有节点/数据都需要参与**。

> [AUTO] 基于摘要推断，核心思想需 PDF 精读后深化。

---

## 4. Key Mechanism

> [AUTO] 摘要信息不足以推断关键机制。需 PDF 精读。
> 摘要提示：a hybrid scheduling approach for optimizing uav-assisted edge computing toward efficient llm inference large language models (llms) play an important role in robotics and embodied intelligence system at the edge, enabling capabilities such as multi-modal data processing, real-time natural language i...

---

## 5. Experiments

- **可能指标**：latency, energy, bandwidth

> [AUTO] 完整实验分析（baseline 合理性、消融实验、鲁棒性测试）需 PDF 精读。

---

## 6. Strength

> [AUTO] 需 PDF 精读后评估。

---

## 7. Weakness & Limitation

- ⚠️ 可能仅在仿真环境验证，缺少真实平台部署实验

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

- 为当前工作中的 **多模态推理/语义判断** 提供前沿参考

> [AUTO] 精确关系定位需对照主线文档 + PDF 精读后确定。

---

## 11. Scenario-Experiment Justification

### 11.1 Scenario → Algorithm Mapping

| 场景特征 | 引发的技术需求 | 选择的算法/模型 | 必要性强度 |
|---|---|---|---|
| 带宽受限 | 需要压缩/选择传输 | 语义编码/源选择 | 中（待验证） |
| 实时性要求 | 需要低延迟推理 | 边缘计算/模型轻量化 | 中（待验证） |

> [AUTO] 必要性强度需 PDF 精读后评估。

### 11.2 Ablation & Necessity Evidence

> [AUTO] 需 PDF 精读后补充消融实验分析。

### 11.3 "Why Not Simpler" Logic

> [AUTO] 需 PDF 精读后补充替代方案排除逻辑分析。

### 11.4 Defensibility Summary

> [AUTO] 需 PDF 精读后补充可防御性总结。

---

> ⚠️ **自动生成标记**：此 papercard 由 arXiv 订阅系统自动生成（基于摘要元数据）。深度分析（完整 11 条 + 对照主线）需人工补充 PDF 精读。标记为 `[AUTO]` 的条目为机器推断，需人工验证。
