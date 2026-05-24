# Zhang 2025 — Resource Allocation and Trajectory Optimization in Multi-UAV Collaborative

> **来源**：IEEE Internet of Things Journal | arXiv: 
> **作者**：Wenqian Zhang; Lu Tan; Tao Huang; Xiaowen Huang; Mengting Huang; Guanglin Zhang
> **采集日期**：2026-05-24 | 相关性：MEDIUM | 归类：UAV-Resource-Allocation
> **arXiv URL**：

---

## 相关性 / 标签
- **相关性等级**：🟡 中相关
- **子方向标签**：uav resource allocation trajectory optimization
- **判断理由**：涉及 UAV/无人机场景；涉及多节点/多智能体协同；涉及边缘/端侧计算

---

## 1. Problem

**摘要推断**：In vehicular networks enhanced by uncrewed aerial vehicles (UAVs), vehicle state information is efficiently collected, and traffic safety is assured. UAVs, serving as aerial base stations, enable vehicle network access and provide edge computing services in the absence of roadside units (RSUs). This...

**问题偏向**（自动推断）：推理/计算实时性不足 + 协同机制不足 + 资源分配不合理 + 路径/轨迹规划与任务目标脱节

> [AUTO] 此推断基于摘要关键词。完整分析需 PDF 精读。

---

## 2. Setting / Assumptions

| 维度 | 设定 |
|------|------|
| 节点数量 | 多 UAV / 无人机集群 |
| 基础设施 | 有边缘服务器/云端 |
| 算力条件 | 待确认 |
| 通信条件 | 待确认 |
| 感知条件 | 待确认（摘要未提及感知退化） |
| 移动性 | 动态轨迹 |
| 任务模型 | 固定任务（待确认） |
| 模型部署 | 讨论分割推理/卸载 |
| 视角关系 | 待确认 |
| 模态范围 | 单模态（主要 RGB 图像，待确认） |

---

## 3. Core Idea

**通过多节点协同弥补单节点视角/算力不足；用学习型策略替代固定规则，适应动态环境；将模型在端-边之间动态切分以平衡计算负载与通信开销**。

> [AUTO] 基于摘要推断，核心思想需 PDF 精读后深化。

---

## 4. Key Mechanism

- **学习范式**：深度强化学习（DRL），通过与环境交互学习最优策略
- **优化方法**：数学优化（凸优化/Lyapunov/Lagrange），求解析或迭代解
- **计算卸载**：模型切分/任务卸载到边缘节点，平衡端边负载

---

## 5. Experiments

> [AUTO] 摘要未提供足够实验细节，需 PDF 精读补充。

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
- **缺少异构算力建模**：可能假设所有节点算力同构
- **缺少多模态融合**：可能仅处理单一模态（RGB）

---

## 10. Relation to My Topic

- 为当前研究中的 **资源分配与调度** 模块提供参考 baseline

> [AUTO] 精确关系定位需对照主线文档 + PDF 精读后确定。

---

## 11. Scenario-Experiment Justification

### 11.1 Scenario → Algorithm Mapping

| 场景特征 | 引发的技术需求 | 选择的算法/模型 | 必要性强度 |
|---|---|---|---|
| 环境动态变化 | 需要自适应策略 | 学习型决策（DRL） | 中（待验证） |

> [AUTO] 必要性强度需 PDF 精读后评估。

### 11.2 Ablation & Necessity Evidence

> [AUTO] 需 PDF 精读后补充消融实验分析。

### 11.3 "Why Not Simpler" Logic

> [AUTO] 需 PDF 精读后补充替代方案排除逻辑分析。

### 11.4 Defensibility Summary

> [AUTO] 需 PDF 精读后补充可防御性总结。

---

> ⚠️ **自动生成标记**：此 papercard 由 arXiv 订阅系统自动生成（基于摘要元数据）。深度分析（完整 11 条 + 对照主线）需人工补充 PDF 精读。标记为 `[AUTO]` 的条目为机器推断，需人工验证。
