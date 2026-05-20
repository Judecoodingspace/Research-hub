# Zhang 2026 — Learning Enhanced Scheduling and Resource Allocation for Heterogeneous UAV Swarms in Edge Assisted Remote Sensing

> **来源**：Scientific Reports, 2026 | DOI: 10.1038/s41598-025-34497-z
> **作者**：Jingjing Zhang, Yunyi Hu, Mengmeng Shao, You Tang, Leilei Wang, Xinyu Li
> **精读日期**：2026-05-14
> **服务于**：Paper 3 (Conditional Semantic Collaboration / Multi-Action Selector)
> **子方向标签**：资源分配与调度；路径规划 / 轨迹优化；协同推理 / 边缘智能
> **相关性**：中相关（路径规划+资源调度，与 Paper 3 互补但非同一问题域）

---

## 1. Problem

论文试图解决**异构 UAV 集群在边缘辅助遥感场景下的联合任务调度与资源分配问题**。

核心矛盾：大规模遥感任务（图像采集、LiDAR 扫描、点云融合、语义分割、目标检测等）在空间分布、数据量、计算复杂度和时延约束上高度异构，而 UAV 平台在传感器配置、机载算力、能量储备上也存在显著差异。静态或单阶段的任务分配/路径规划策略无法应对动态环境（任务新增、位置更新、UAV 故障、优先级变化）。

**问题类别**（通用脚手架）：
- **资源分配不合理**（主）：算力/能量/悬停时间三维能力向量未联合优化
- **路径/轨迹规划与任务目标脱节**（主）：路径规划未与边缘计算负载联动
- **协同机制不足**（次）：多 UAV 任务分工缺乏动态重分配机制
- **推理/计算实时性不足**（次）：边缘计算任务需在 deadline 内完成

> **Paper 3 聚焦判断**：该论文不直接触及 Paper 3 的核心问题（决策触发条件不明确 / 传输效率不足 / 协同机制不足中的 pair 选择），但在「异构能力建模」和「动态触发机制」两个维度上可提供方法论参考。

---

## 2. Setting / Assumptions

| 维度 | 设定 |
|------|------|
| 节点数量 | 多 UAV（3 架，可扩展） |
| 基础设施 | 边缘服务器 / Command Center 可用 |
| 算力条件 | **异构**：energy (J), hovering time (s), FLOPs 三维能力向量；UAV 分为 sensing-only、processing-only、integrated 三类 |
| 通信条件 | **未显式建模**：仅考虑 compatibility 约束，无带宽/速率/信道模型 |
| 感知条件 | 完美感知（理想化网格模型），无退化/遮挡/噪声 |
| 移动性 | 动态轨迹（通过任务分配间接决定） |
| 任务模型 | 动态任务（新任务插入、位置更新、取消），含 deadline 和 priority |
| 模型部署 | 不涉及 DNN 模型切分/分割推理 |
| 视角关系 | 不涉及多视角协同感知 |
| 模态范围 | 单模态（遥感数据，不涉及文本/语音） |

> **与 Paper 3 的设定差异**：Zhang 2026 是卫星遥感式的区域扫描 + 边缘计算任务调度，Paper 3 是实时目标检测 + 前后端语义融合的触发决策。Zhang 2026 无通信约束、无感知退化、无触发/拒绝机制——这些恰是 Paper 3 的核心设定。差异非威胁，而是互补：Paper 3 的 pair 级触发决策可嵌入 Zhang 2026 这类调度框架中，作为"感知协作动作"的可选步骤。

---

## 3. Core Idea

**DMMP-PR-TSA：三阶段动态多阶段任务规划框架**。

核心思想：将异构 UAV 集群的遥感任务调度解耦为三个阶段，层层递进——

1. **D (Partitioning)**：基于容量约束的 power diagram 将任务区域划分为负载均衡、空间紧凑的子区域，每个 UAV 获得初始任务集；
2. **PR (Preallocation & Reallocation)**：在初始预分配基础上，当动态事件（新任务、位置变更、UAV 故障）触发时，执行可行性感知的任务重分配；
3. **TSA (Task Sequence Adjustment)**：用 RL（POMDP 建模）优化每个 UAV 内部的执行顺序，优先高优先级任务、平衡计算负载。

**为什么这样设计**：场景的三大特征——(1) 异构 UAV 能力（2）异构任务需求（3）动态环境变化——分别逼出了 D（解决静态异构匹配）、PR（解决动态适应）、TSA（解决序列最优）。三个阶段输入输出耦合，形成闭环。

---

## 4. Key Mechanism

### 4.1 任务建模
- 网格离散化：遥感区域 A 离散为 grid cells G = {g1,...,gN}
- 每个 cell 有 workload 向量：能量成本 ω_E,i、悬停时间 ω_H,i、计算量 ω_F,i，以及优先级权重 w_pri_i
- 每个 UAV u 有三维能力向量：C_u(t) = [C_u,E(t), C_u,H(t), C_u,F(t)]

### 4.2 D：容量约束区域划分
- 优化目标：最小化旅行距离 × 优先级权重 + TV 正则化（空间紧凑性）
- 约束：每个 cell 分配给恰好 1 架 UAV；每架 UAV 的 E/H/F 维度不超容量
- 解法：容量约束 power diagram + Lagrange 乘子法迭代 + 局部 1-swap 精化
- 周期重评估：每 Δt 秒，用 CV-KF 预测 UAV 位置，用 hysteresis 阈值避免不必要重划分

### 4.3 PR：动态任务重分配
触发条件：新任务插入、任务位置更新、UAV 故障、任务取消
- 改进的 SOM 进行智能预分配（考虑空间邻近性和能力兼容性）
- 优先级感知的重分配：高优先级任务优先匹配能力强的 UAV
- 6 类约束：(1) 能量 (2) 计算 (3) 优先级 (4) Deadline (5) UAV-任务兼容性 (6) 前置约束

### 4.4 TSA：RL 驱动任务序列调整
- POMDP 建模：状态 = (剩余能力, 已完成任务, 当前任务队列)；动作 = 选择下一个执行的任务
- 奖励函数：完成任务数 − 违反 deadline 惩罚
- 在 D 和 PR 产出的任务集 {T_u^PR} 基础上优化执行顺序

### 4.5 联合优化关系
D → PR → TSA 是级联的：D 提供初始任务集，PR 动态调整，TSA 精细化排序。但三个阶段**非端到端联合优化**，而是分阶段独立求解。

---

## 5. Experiments

### 实验设置
- **任务规模**：9 个预分配任务 + 9 个动态新插入任务
- **任务类型比**：数据采集任务 : 边缘处理任务 = 1:2
- **高优先级任务占比**：50%
- **UAV 配置**：3 种 fleet 配置（balanced 1:1:1 / acquisition-oriented 1:2:3 / processing-oriented 3:2:1）
- **Baseline**：PSO（粒子群优化）、DPSO（动态 PSO）、Random（随机分配）、Uniform（均匀分配）

### 测试场景
1. 初始任务序列配置（TSA vs PSO/DPSO）
2. 新任务插入（9 个新任务，不同 priority/deadline）
3. 任务位置更新
4. UAV 故障（UAV1 失效后的重分配）
5. 任务取消

### 关键结果
| 场景 | DMMP-PR-TSA | PSO/DPSO |
|------|------------|----------|
| 初始配置 | 100% | 77.78% |
| 新任务插入 | 88.89% | 72.22% / 77.78% |
| 位置更新 | 100% | 77.78% |
| UAV 故障 | 88.89% | 66.67% |
| 任务取消 | 100% | 71.43% |

### 实验评估
- ✅ 覆盖了多种动态场景
- ✅ 有合理的 heuristic baseline（PSO, DPSO, Random, Uniform）
- ✅ 任务规模可扩展（1-9 任务，3-5 UAV）
- ❌ **缺少消融实验**：未逐步移除 D/PR/TSA 模块以证明各自贡献
- ❌ **仅在仿真中验证**：无真实 UAV 部署或硬件在环测试
- ❌ **无感知质量指标**：只关注 completion rate，无检测精度/召回率等任务质量维度
- ❌ **无通信约束建模**：带宽/延迟/信道条件未体现
- ❌ **任务模型过于抽象**：网格 cells 替代了真实遥感数据

> **Paper 3 实验补强线索**：Zhang 2026 的 ablation 缺失对 Paper 3 是**警示**——Paper 3 必须保留并强化现有的诚实消融（V/D/H/HC 四组特征对比）。Zhang 2026 的动态触发机制（新任务插入、UAV 故障）的评估方式可供 Paper 3 Layer 2 的 pair 重匹配实验参考。

---

## 6. Strength

1. **异构建模系统性强**：三维能力向量（E/H/F）+ 三类 UAV（sensing/processing/integrated）的异构刻画值得借鉴
2. **动态触发机制清晰**：明确列出 4 种触发重分配的场景（新任务、位置更新、故障、取消），每种有独立的处理逻辑
3. **约束形式化完整**：6 类约束（能量、计算、优先级、deadline、兼容性、前置）完整覆盖 UAV 任务调度核心限制
4. **多阶段解耦设计**：D → PR → TSA 的分阶段架构使问题可解，且输入输出耦合关系明确

---

## 7. Weakness

1. **无通信建模**：完全未考虑 UAV 间通信的带宽、延迟、信道质量——这是多 UAV 协同的核心约束，尤其在边缘计算场景下数据传输是关键瓶颈
2. **无感知质量反馈**：仅以 completion rate 为指标，不关心数据采集/处理的质量（图像清晰度、检测精度等）
3. **缺少消融实验**：未逐步移除 D/PR/TSA 证明各模块独立贡献，无法判断三阶段均必要
4. **RL 使用缺乏场景必要性论证**：TSA 使用 POMDP+RL，但为什么不直接用优先级排序（rule-based）就能取得接近效果？未设简单 baseline（如 EDF / priority-first）
5. **仿真过于理想**：网格化区域 + 静态 workload 估计，与实际遥感场景（天气变化、遮挡、传感器噪声）差距大
6. **无 real-device 验证**：全在仿真中，无 Jetson/真实 UAV 部署

> **Paper 3 压力测试**：Zhang 2026 的 RL 使用方式（仅用于序列调整而非全局策略）提示一个对 Paper 3 的潜在审稿质疑——如果 Paper 3 的 Ridge 回归预测器已经够用，为什么某些工作（如 Zhang 2026）要用 RL？Paper 3 需在 spec 中明确回答：Ridge 回归服务于 <1ms 的实时预测，而 RL 的序列决策服务于更长时域的任务排序——两者场景约束不同，方法选择由场景驱动。

---

## 8. Reusable Part

| 可复用内容 | 具体方面 | 用于 Paper 3 的位置 |
|------------|---------|-------------------|
| 异构能力建模 | 三维能力向量 (E, H, F) 的思路可迁移为 Paper 3 中 UAV pair 的能力刻画 | Layer 2 pair 选择器 |
| 动态触发条件分类 | 明确列出触发事件类型（新任务→新图像、故障→后侧 UAV 离线、位置变更→链路变化） | Layer 2 的 trigger condition 设计 |
| 约束形式化风格 | 6 类约束的数学表达方式可借鉴用于 Paper 3 的通信预算约束、延迟预算约束 | 问题形式化 (Problem Formulation) |
| 多 baseline 对比策略 | PSO/DPSO/Random/Uniform 四 baseline 的设置逻辑 | Paper 3 的 baseline 选择可参照（always-B2, always-none, random trigger 已对应） |
| 动态场景实验设计 | 新任务插入/UAV 故障/任务取消的实验范式 | Layer 2 的鲁棒性验证实验 |

---

## 9. Attack Point

- **缺少任务导向优化**：不关心采集数据的感知质量，仅优化 completion rate——可将 Paper 3 的语义效用驱动决策嵌入其调度框架
- **缺少通信建模**：引入带宽/延迟约束后，任务重分配的通信代价不可忽略——Paper 3 的 A2A 链路感知决策恰可填补
- **缺少触发/拒绝机制**：所有任务都试图完成，无"该任务不值得执行"的判断——Paper 3 的预算约束触发可补充
- **RL 使用缺乏论证**：TSA 的 RL 选择没有与简单 rule-based 方案对比——这是 Paper 3 可发力的写作防御点

---

## 10. Relation to My Topic (Paper 3)

| 对照维度 | 分析 |
|----------|------|
| **补哪一环** | Zhang 2026 补的是**宏观调度层**：异构 UAV 集群的任务分配与路径规划。Paper 3 补的是**微观决策层**：给定一对前后端 UAV，当前图像是否值得触发语义融合。两者是不同粒度的决策，可形成层级关系。 |
| **忽略哪一环** | Zhang 2026 忽略通信约束、感知质量反馈、图像级触发决策——恰是 Paper 3 的核心。 |
| **前置工作 vs 对比基线** | 可作为 **Related Work 中的定位锚点**：Paper 3 的 pair 级触发决策可被描述为"在现有宏观任务调度框架（如 Zhang 2026 DMMP-PR-TSA）之下的微观协作决策层，填补'已分配任务中哪些图像值得后端协作'的空白"。 |
| **能否支撑论证** | 可以。Zhang 2026 证明了异构 UAV 能力+动态环境的调度可行性，但未解决"协作是否总是有益的"——Paper 3 的预算约束触发恰可引用此 gap。 |

**一句话定位**：Zhang 2026 管的是"哪个 UAV 去哪做什么任务"，Paper 3 管的是"任务中哪些图像值得前后端协作"——Zhang 2026 为 Paper 3 提供了上层调度框架的存在性证明，Paper 3 补充了调度框架中缺失的感知质量驱动触发决策。

---

## 11. Scenario-Experiment Justification（场景-实验双重合理化）

### 11.1 Scenario → Algorithm Mapping

| 场景特征 | 引发的技术需求 | 选择的算法/模型 | 必要性强度 |
|----------|--------------|----------------|-----------|
| 异构 UAV（sensing-only / processing-only / integrated） | 需在分配时考虑能力匹配 | Capacity-constrained power diagram + 兼容性约束 | **强** |
| 任务异构（采集 vs 处理，不同数据量/计算量） | 需三维 workload 建模 | (E, H, F) workload 向量 | **强** |
| 动态环境（新任务、UAV 故障） | 需在线重分配 + 触发条件 | Improved SOM + priority-aware reallocation | **中** |
| 执行顺序影响效率 | 需序列优化 | RL-based TSA (POMDP) | **弱**：未说明为何不用 EDF/priority-first 等简单规则 |
| 空间区域覆盖 | 需任务区域划分 | Power diagram + TV regularization | **中** |

### 11.2 Ablation & Necessity Evidence

- ❌ **未提供消融实验**：论文未逐步移除 D/PR/TSA 各模块以证明各自独立贡献
- ❌ 无法判断 D+PR+TSA 的组合收益是否大于各部分之和
- ⚠️ 论文通过多场景对比（PSO/DPSO）间接论证整体框架优势，但无法区分各模块贡献
- **对 Paper 3 的启示**：必须保留现有的 V/D/H/HC 对比消融，并在论文中显式说明每个模块的必要性

### 11.3 "Why Not Simpler" Logic

- ❌ 未讨论为何 RL（TSA）优于简单的优先级排序（EDF / priority-first）
- ❌ 未设置 rule-based 简单 baseline（如固定优先级排序 + 最近邻路径）
- ⚠️ PSO/DPSO/Random/Uniform 均为 meta-heuristic 或随机策略，但缺少"为什么非学习不可"的论证
- **过度设计嫌疑**：TSA 使用 POMDP+RL 处理序列调整，但该子问题的状态空间小（单 UAV 内 3-7 个任务），rule-based 方案可能足够且更可解释——存在"杀鸡用牛刀"嫌疑

### 11.4 Defensibility Summary

这篇论文的 D 和 PR 模块的场景→算法映射链较强（异构能力×异构任务 → 容量约束划分 → 动态重分配），但 **TSA 的 RL 选择缺乏场景必要性论证**。主要漏洞：(a) 无消融实验证明三模块各自必要；(b) TSA 无 simple baseline 排除 rule-based 替代方案；(c) 无通信建模使边缘计算场景的完整性存疑。整体上，论文能部分经受"技术堆砌"质疑（前两个模块有场景依据），但 TSA 的 RL 选择是明显的防御缺口。

---

## 附录：与 Paper 3 的跨文献对照汇总

| Paper 3 对照维度 | 评估 |
|-----------------|------|
| **设定差异** | 异构调度 vs 触发决策，互补非竞争 |
| **方法验证/挑战** | 支持 Paper 3 的异构建模方向；RL 使用方式警示 Paper 3 需辩护 Ridge 回归的简单性 |
| **实验补强** | Zhang 2026 的 ablation 缺失警示 Paper 3 必须保留消融；动态触发场景实验可借鉴 |
| **写作借鉴** | 约束形式化风格、"三层递进"的架构描述方式可复用 |
| **防御素材** | TSA 无 simple baseline 的漏洞 → Paper 3 的 Ridge vs random/always-B2 对比恰是优势 |
| **baseline 候选** | 可作为 Related Work 中"宏观调度层"的锚点论文 |
