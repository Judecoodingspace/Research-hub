# TVT 重投修改执行计划 (Revision Execution Plan)

> **基于**: 4位审稿人 + AE 决定信 | 原稿号 `VT-2026-02444` | 120天重投窗口
> **生成日期**: 2026-05-08
> **关联文件**: `revision_matrix.md`, `revision_strategy.md`, `novelty_revision_directions_bilingual.md`

---

## 一、审稿意见全景统计

| 审稿人 | 评论数 | Critical | Major | Minor |
|--------|--------|----------|-------|-------|
| Reviewer 1 | 11 | 6 | 4 | 1 |
| Reviewer 2 | 11 | 2 | 6 | 3 |
| Reviewer 3 | 9 | 6 | 2 | 1 |
| Reviewer 4 | 4 | 4 | 0 | 0 |
| **合计** | **35** | **18** | **12** | **5** |

---

## 二、六大工作包 (Work Packages) 总览

```
WP3: Reward & Underlay     WP2: DQI 形式化       WP4: 实验增强
    (技术正确性)              (方法严谨性)           (证据强度)
         │                       │                    │
         └───────┬───────────────┘                    │
                 │                                    │
                 ▼                                    │
         WP1: 创新性重写                               │
         (Abstract/Intro/Related Work/Conclusion)      │
                 │                                    │
                 ▼                                    │
         WP5: 部署与开销分析                            │
                 │                                    │
                 ▼                                    │
         WP6: 语言精修 + Response Letter
```

**依赖关系**：WP3 → WP2 → WP4 → WP1 → WP5 → WP6

---

## 三、分阶段执行计划

---

### 阶段 0：准备与对齐 (第 1-2 天)

#### 任务 0.1：与导师对齐核心决策

需要导师确认以下 5 个问题（详见 `analysis/advisor_discussion_brief_bilingual.md`）：

| # | 决策问题 | 建议选项 |
|---|---------|---------|
| D1-D5 | 详见 advisor_discussion_brief | 此文档已包含完整分析与建议 |

> **注意**：D1-D5 的完整分析、双语版本和讨论上下文见 `analysis/advisor_discussion_brief_bilingual.md`，此处不重复。

#### 任务 0.2：环境与代码审计

- [ ] 确认仿真代码可运行，输出与论文当前数据一致
- [ ] 导出当前所有图表数据，建立 baseline 数据快照
- [ ] 确认 `main.tex` 可正常编译
- [ ] 备份当前版本（Git tag: `v1.0-submitted`）

---

### 阶段 1：WP3 — Reward 与 Underlay 可行性修复 (第 3-7 天)

> **优先级**: 🔴 最高 — 这是技术正确性问题，直接影响审稿人对结果的信任
> **覆盖**: R1-C3, R1-C4, R1-C8, R3-C6

#### 任务 1.1：重写 Overlay/Underlay Reward 公式

**目标**：消除歧义，确保公式与仿真代码完全一致

**具体操作**：
1. 检查仿真代码中 overlay reward 的实际计算方式
2. 重写 Eq.(12)：
   - Overlay: 明确 DQI 强调项是 `Γ · Φ'_t` 还是 `Φ'_t = Γ`，添加 case 说明
   - Underlay: 明确 power constraint 如何在 reward 中体现
3. 增加 reward normalization/clipping 说明
4. 确保所有符号在 notation table 中有定义

**修改位置**：`main.tex` Section IV-B, Eq.(12) 附近

**应对审稿人**：R1-C3

---

#### 任务 1.2：定义 Underlay 功率控制的闭式约束

**目标**：给出清晰的 underlay power 选择规则

**具体操作**：
1. 定义 `P_t^{i,j} ≤ Ψ_t^{j,PU} / |h_t^{i,PU}|^2` 作为 underlay 功率上限
2. 说明功率控制的时间粒度（每 slot 更新 vs 每 T_upd 更新）
3. 如有离散功率级别，列出可选值
4. 明确功率控制是否有反馈回路

**修改位置**：`main.tex` Section IV-B（在 reward 之前或之中）

**应对审稿人**：R1-C8

---

#### 任务 1.3：增加 Interference Violation Penalty

**目标**：防止 agent 偏向 underlay 接入

**具体操作**：
1. 在 underlay reward 中增加 violation penalty term
2. 定义 violation 条件：当 `P_t^{i,j} · |h_t^{i,PU}|^2 > Ψ_t^{j,PU}` 时施加负奖励
3. 在实验中增加 "PU interference violation rate" 指标
4. 确保 violation penalty 权重合理（不过大也不过小）

**修改位置**：`main.tex` Section IV-B (reward) + Section V (新增 violation rate 图/表)

**应对审稿人**：R3-C6, R1-C9（violation rate 部分）

---

#### 任务 1.4：解释 SU-PU 信道增益获取方式

**目标**：让 underlay 在实际 CVN 中可解释、可部署

**具体操作**：
1. 明确三种可能的获取途径（选其一或组合）：
   - **BS/RSU 辅助估计**：基站估计 SU-PU 链路并通过控制信道下发
   - **PU 协作反馈**：PU 广播其干扰容忍阈值
   - **路径损耗代理模型**：用距离/大尺度路径损耗近似
2. 在 Section III-A 系统模型中明确说明
3. 如有必要，增加 estimation error robustness 实验

**修改位置**：`main.tex` Section III-A + Section IV-B

**应对审稿人**：R1-C4

---

#### 任务 1.5：代码-论文一致性验证

- [ ] 逐一核对仿真代码中每个 reward 计算与论文公式一致
- [ ] 记录所有差异，统一修正
- [ ] 如 reward 修正影响实验结果，重新运行所有实验

---

### 阶段 2：WP2 — DQI 模块形式化 (第 8-12 天)

> **优先级**: 🔴 最高 — 审稿人对 DQI 的质疑会连带影响对整个方法的信任
> **覆盖**: R1-C2, R1-C6, R3-C3, R3-C4, R3-C5

#### 任务 2.1：定义 DQI 训练目标

**目标**：让 DQI 从一个"Transformer 输出的黑盒分数"变成"有明确物理意义的 link-quality estimator"

**具体操作**：
1. 定义 DQI target：建议使用 **normalized achievable link quality**（归一化可达链路质量）
   - 方案 A：`Φ_target = normalized achievable rate`（min-max 归一化到 [0,1]）
   - 方案 B：`Φ_target = packet success probability`（基于 SNR 的理论/仿真值）
   - 方案 C：`Φ_target = weighted normalized (SNR, RSS, B)` 加权组合作为伪标签
2. 明确 loss function：MSE（回归） 或 Binary Cross-Entropy（如果二值化）
3. 说明训练数据构造方式：
   - 输入特征：`[SNR, RSS, bandwidth]` 历史序列
   - 目标标签：由可达速率/链路成功率计算
4. 增加 DQI validation 指标：DQI 与 achievable throughput 的 Spearman/Pearson correlation

**修改位置**：`main.tex` Section III-B

**应对审稿人**：R1-C2

---

#### 任务 2.2：增加 DQI Baseline 对比

**目标**：证明 Transformer-based DQI 不是过度设计

**具体操作**：
1. 至少增加 1 个简单 DQI baseline：
   - **Weighted-Sum DQI**: `Φ = w1·SNR_norm + w2·RSS_norm + w3·B_norm`
   - 或 **MLP-DQI**: 2-3 层全连接网络
2. 在实验中对比 Transformer-DQI vs Baseline-DQI 对最终系统性能的影响
3. 从 correlation with achievable rate、对 VT throughput/PLR 的贡献等维度比较

**修改位置**：`main.tex` Section V（新增 DQI ablation 子实验）

**应对审稿人**：R3-C3

---

#### 任务 2.3：补全 Attention-LSTM Predictor 架构细节

**目标**：让预测模块不再是"黑盒"

**具体操作**：
1. 在 Section III-C 中明确：
   - LSTM 层数、hidden size
   - Attention 机制的具体形式（additive / dot-product / scaled dot-product）
   - 输入窗口长度 T
   - 优化器、学习率、batch size
   - 训练/验证/测试集划分
2. 可选：增加与简单预测器（Markov model、XGBoost）的预测精度对比

**修改位置**：`main.tex` Section III-C + Table of hyperparameters

**应对审稿人**：R1-C6

---

#### 任务 2.4：扩展 DQI 特征维度讨论

**目标**：回应 Doppler/latency 缺失的质疑

**具体操作**：
1. 在 DQI 模型描述中说明当前特征选择理由（SNR/RSS/B 是 CVN 中最易获取的参数）
2. 在 limitations 或 future work 中说明 DQI 特征向量可扩展为 `[SNR, RSS, B, Doppler, latency, coherence_time]`
3. 可选：如果仿真环境支持，快速补充一个含 Doppler 的 DQI 版本

**修改位置**：`main.tex` Section III-B + Section VI (limitations/future work)

**应对审稿人**：R3-C4

---

#### 任务 2.5：解释 State 中 Sensing/DQI/Prediction 的互补性

**目标**：说明三者不是冗余信息，而是携带不同时间尺度信息

**具体操作**：
1. 在 Section IV-A 中增加一段说明：
   - Sensing outcome：瞬时、当前 slot 的观测
   - DQI：中时间尺度（多 slot 统计）的质量评估
   - Prediction probability：短时预测的未来可用性
2. 可选：增加 feature correlation 分析或 feature ablation

**修改位置**：`main.tex` Section IV-A

**应对审稿人**：R3-C5

---

### 阶段 3：WP4 — 实验增强 (第 13-25 天)

> **优先级**: 🔴 最高 — Reviewer 1/2/3 一致认为实验强度不足
> **覆盖**: R1-C7, R1-C9, R1-C10, R2-C5, R2-C7, R3-C7, R3-C8

#### 任务 3.1：补充仿真环境完整说明

**目标**：让实验完全可复现

**具体操作**：
1. 新增 "Simulation Setup" 子节/表格，包含：
   - 路径损耗模型（如 WINNER II, 3GPP TR 38.901）
   - 衰落模型（Rayleigh/Rician，含参数）
   - 移动性模型（车辆速度范围、轨迹类型）
   - SNR/RSS/B 生成方式与范围
   - 队列模型与流量到达率
   - 频谱感知错误模型（`P_fa`, `P_md`）
   - 所有参数的具体数值

**修改位置**：`main.tex` Section V 开头

**应对审稿人**：R1-C7

---

#### 任务 3.2：增加强 DRL Baseline

**目标**：与当前最优方法公平对比

**具体操作**：
1. **必须至少增加 1 个**：
   - **DDQN**（标准双深度 Q 网络，无 ESN）：证明 ESN 加速收敛的必要性
   - 或 **PPO**（离散动作版本）：证明 value-based 方法在此问题上的适用性
2. 确保 baseline 使用相同的 state representation 和 reward
3. 报告收敛曲线、最终性能、训练时间

**修改位置**：`main.tex` Section V（新增 baseline 对比图/表）

**应对审稿人**：R2-C7, R3-C8

---

#### 任务 3.3：扩大仿真规模

**目标**：证明方法在大规模 CVN 中仍有效

**具体操作**：
1. 至少增加 1 组大规模配置：
   - `M=10, N=20`（频谱稀缺）
   - `M=20, N=10`（频谱充裕）
   - 或 `M=15, N=15`（平衡）
2. 如果计算资源允许，加到 `M=20, N=50`
3. 报告大规模场景下的收敛性和最终性能

**修改位置**：`main.tex` Section V

**应对审稿人**：R1-C10, R3-C7

---

#### 任务 3.4：增加统计置信度报告

**目标**：结果具有统计显著性

**具体操作**：
1. 所有关键实验运行 **≥5 个 random seeds**
2. 图中加 error bar（标准差）或 shaded region（95% CI）
3. 表中报告 mean ± std
4. 可选：对关键对比做 t-test 或 Wilcoxon test

**修改位置**：`main.tex` Section V 所有图表

**应对审稿人**：R1-C10

---

#### 任务 3.5：增加鲁棒性实验

**目标**：证明方法在非理想条件下仍鲁棒

**具体操作**：
1. **PU 流量变化实验**：
   - 测试不同 `p01/p10` 组合（如 `p01=0.1,0.3,0.5`）
   - 可与 R2-C5 合并
2. **预测误差鲁棒性**：
   - 人为注入不同比例的 false-alarm / miss-detection
   - 观察系统性能退化曲线
3. **信道估计误差鲁棒性**（如果做了 R1-C4 的 estimation model）：
   - 对 `|h_t^{i,PU}|^2` 加噪声，测试性能退化

**修改位置**：`main.tex` Section V（新增鲁棒性分析子节）

**应对审稿人**：R1-C9, R2-C5

---

#### 任务 3.6：增加 PU Interference Violation Rate 指标

**目标**：量化 PU 保护效果

**具体操作**：
1. 定义 violation rate：`P(underlay access AND P_t · |h|^2 > Ψ)`
2. 对所有方案报告 violation rate
3. 预期结果：所提方案的 violation rate 应显著低于 Fixed Underlay
4. 与 R3-C6（fairness/violation penalty）联动

**修改位置**：`main.tex` Section V（新增 violation rate 图/表）

**应对审稿人**：R1-C9, R3-C6

---

### 阶段 4：WP1 — 创新性重写 (第 26-32 天)

> **优先级**: 🔴 最高 — 这是决定录用与否的"故事线"
> **覆盖**: R2-C2, R2-C3, R3-C1, R3-C9, R4-C1, R4-C2, R4-C4
> **参考**: `novelty_revision_directions_bilingual.md`

#### 任务 4.1：标题修改

**当前标题**：
> A High-Quality ESN-DDQN-Based Adaptive Access Algorithm for Cognitive Vehicular Networks

**建议新标题**（与导师确认后选择）：
> **方案 A（推荐）**：A Quality-Aware and Prediction-Assisted Adaptive Overlay/Underlay Access Framework for Cognitive Vehicular Networks
>
> **方案 B**：Adaptive Spectrum Access in Cognitive Vehicular Networks: A Quality- and Prediction-Aware Deep Reinforcement Learning Approach
>
> **方案 C**：Joint Quality Assessment, Occupancy Prediction, and Constrained Reinforcement Learning for Adaptive DSA in CVNs

**核心原则**：标题应突出 **问题 + 框架**，而非**模型名称**

**修改位置**：`main.tex` `\title{}`

**应对审稿人**：R2-C2, R4-C1

---

#### 任务 4.2：Abstract 重写

**当前问题**：依次列举 Transformer → LSTM → ESN-DDQN，审稿人首先看到三个现成模型

**修改策略**：
1. 第一句：问题背景与挑战（CVN 中 idle ≠ usable, prediction + quality 双缺口）
2. 第二句：提出框架（quality-aware + prediction-assisted + adaptive access）
3. 第三句：简述方法（不强调具体模型，强调功能）
4. 第四句：关键实验结果
5. 减少/推迟具体模型名称的出现

**修改位置**：`main.tex` `\begin{abstract}...\end{abstract}`

**应对审稿人**：R2-C2, R4-C1

---

#### 任务 4.3：Introduction 贡献列表重写

**当前贡献结构**（模型中心化）：
1. Transformer-based DQI
2. Novel ESN-DDQN
3. 实验性能

**建议新贡献结构**（问题中心化）：

> 1. **Multi-Timescale State Representation**: We formulate a pre-access state representation that combines instantaneous sensing, medium-term channel quality (DQI), and short-horizon occupancy prediction — addressing the gap that existing DSA methods use only one or two of these information sources.
>
> 2. **Interference-Constrained Adaptive Access Mechanism**: We design a differentiated overlay/underlay reward with explicit PU interference constraints and violation penalties, enabling the agent to learn mode-switching policies that balance VT QoS and PU protection.
>
> 3. **Fast-Converging ESN-Assisted Policy Learning**: We develop an ESN-enhanced DDQN implementation tailored for discrete channel-mode action spaces in high-mobility CVNs, where ESN reservoir computing reduces recurrent training overhead and accelerates convergence.
>
> 4. **Regime-Dependent Design Insight**: Through systematic ablation, we reveal that quality awareness dominates under spectrum scarcity while prediction dominates interruption avoidance under spectrum abundance — providing a design principle for CVN DSA systems.

**修改位置**：`main.tex` Introduction 末尾贡献列表

**应对审稿人**：R2-C2, R2-C3, R4-C1

---

#### 任务 4.4：Related Work 增加 Gap Matrix

**目标**：用表格可视化本文相对已有工作的覆盖维度

**建议新增 Table**：

| Work | CVN DSA | Quality-Aware | Occupancy Prediction | Overlay/Underlay Switching | PU Protection Constraint | Fast Convergence | Deployment Analysis |
|------|---------|---------------|---------------------|---------------------------|-------------------------|-----------------|-------------------|
| [ref8] | ✓ | ✗ | ✗ | Overlay only | ✗ | - | ✗ |
| [ref9] | ✓ | ✗ | ✗ | Underlay only | Partial | - | ✗ |
| [ref15-17] | ✓ | Partial | ✗ | ✗ | ✗ | ✗ | ✗ |
| [ref18] | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [ref19] | Partial | ✗ | ✗ | ✗ | ✗ | Partial | ✗ |
| **This work** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**修改位置**：`main.tex` Section II 末尾（Related Work summary）

**应对审稿人**：R2-C2, R2-C3, R4-C1

---

#### 任务 4.5：增加 "Regime-Dependent Contribution Analysis" 小节

**目标**：把已有消融实验提升为系统级设计 insight

**具体操作**：
1. 在 Section V 中新增子节 "Regime-Dependent Analysis"
2. 核心论述：
   - `M < N`（频谱稀缺）：DQI 是瓶颈 → 质量感知主导 VT throughput
   - `M > N`（频谱充裕）：PU return 是瓶颈 → 预测主导 PLR 和 PU 保护
   - 这解释了为什么两个模块都需要
3. 将该 insight 同时写入 Abstract 和 Conclusion

**修改位置**：`main.tex` Section V + Abstract + Conclusion

**应对审稿人**：R2-C3, R4-C2

---

#### 任务 4.6：ESN-DDQN 选择理由说明

**目标**：回答 Reviewer 3 的 "Why DDQN, not DDPG/SAC/TD3?"

**具体操作**：
1. 在 Section IV-C 开头增加 "Rationale for ESN-DDQN" 段落：
   - 动作空间是离散的（channel index × access mode），DDQN 自然适用
   - DDPG/SAC/TD3 为连续动作设计，需要额外离散化
   - ESN 的 reservoir computing 只需训练 readout 权重，降低高移动性场景下的重训练开销
2. 在 Related Work 中引用 reservoir-computing RL 的已有工作并说明区别

**修改位置**：`main.tex` Section IV-C + Section II

**应对审稿人**：R3-C1

---

#### 任务 4.7：Conclusion 重写

**目标**：不重复 Abstract，总结设计 insight + 局限性 + 未来工作

**修改策略**：
1. 总结核心贡献（problem-centric 表述）
2. 列出关键设计 insight（regime-dependent finding）
3. 明确局限性（centralized、feature scope、simulation-only）
4. 展望未来（decentralized multi-agent、field test、Doppler/latency extension）

**修改位置**：`main.tex` Section VI

**应对审稿人**：R2-C10, R4-C2, R4-C4

---

### 阶段 5：WP5 — 部署与开销分析 (第 33-37 天)

> **优先级**: 🟡 高 — Reviewer 2 和 Reviewer 4 都关注
> **覆盖**: R1-C11, R2-C8, R2-C9, R4-C3

#### 任务 5.1：Centralized Server 架构重新解释

**目标**：将 "centralized server" 映射到实际可部署架构

**具体操作**：
1. 将 centralized server 重新解释为 **MEC/Edge Server** 或 **RSU-assisted architecture**
2. 说明在 5G NR-V2X 中，RSU/MEC 可以承担 DQI 计算和预测功能
3. 讨论信令流程：VT → RSU (sensing report) → MEC (DQI + prediction) → VT (summary broadcast)

**修改位置**：`main.tex` Section III-A + Section IV-D (新增 "Deployment Considerations")

**应对审稿人**：R2-C9, R4-C3

---

#### 任务 5.2：量化通信开销

**目标**：给出具体的 overhead 数字

**具体操作**：
1. 定义每个更新周期 T_upd 的广播 payload：
   - `M` 个 DQI 值（假设每值 8-16 bits 量化）
   - `M` 个 prediction probability（每值 8 bits）
   - 总计：`M × (16 + 8) = 24M bits` per T_upd
2. 给出具体数值示例（如 M=20 时约 60 bytes）
3. 与 VT 数据传输量对比，说明 overhead 可接受

**修改位置**：`main.tex` Section IV-D

**应对审稿人**：R1-C11

---

#### 任务 5.3：T_upd / T_stat 敏感性分析

**目标**：回应 descriptor staleness 关注

**具体操作**：
1. 测试不同 T_upd 下的性能变化（如 T_upd = 5, 10, 20, 50 slots）
2. 画性能 vs T_upd 曲线
3. 讨论 trade-off：更新越频繁 → 性能越好但开销越大

**修改位置**：`main.tex` Section V（新增 T_upd sensitivity 图/讨论）

**应对审稿人**：R1-C11

---

#### 任务 5.4：复杂度-性能 Trade-off 分析

**目标**：量化地证明性能增益值得复杂度开销

**具体操作**：
1. 新增表格对比各方案的：
   - 训练/推理时间（per step 或 per episode）
   - 模型参数量
   - 收敛所需 episode 数
   - 最终性能（VT throughput, PLR, PU throughput）
2. 讨论：是否可以用更简单的方案达到相近性能？

**修改位置**：`main.tex` Section V

**应对审稿人**：R2-C8, R3-C2

---

#### 任务 5.5：局限性明确写入

**目标**：诚实地列出当前方法限制

**具体操作**：
1. 在 Section V 末尾或 Section VI 中增加 "Limitations" 段落
2. 列出：
   - 依赖 centralized MEC/RSU 进行 DQI/prediction 计算
   - DQI 特征当前仅含 SNR/RSS/B
   - 仿真验证（非实测）
   - PU 模型假设为两状态 Markov
   - SU-PU 信道获取依赖估计

**修改位置**：`main.tex` Section V-D 或 Section VI

**应对审稿人**：R2-C8, R4-C3

---

### 阶段 6：WP6 — 语言精修与 Response Letter (第 38-45 天)

> **优先级**: 🟢 中 — 在所有技术修改完成后进行
> **覆盖**: R2-C6, R2-C10, R2-C11 + 全部 response

#### 任务 6.1：全文语言润色

- [ ] 拆分 Introduction 和 System Model 中的长句（R2-C11）
- [ ] 统一时态和术语
- [ ] 检查所有交叉引用（图、表、公式、参考文献）
- [ ] 检查 IEEE 格式合规（页数 ≤ 16 pages, 字体 ≥ 10pt）

#### 任务 6.2：增加模块交互流程图/表

- [ ] 新增 pipeline overview table（R2-C6）：
  - 列：Module | Input | Output | Update Rate | Dependency
  - 帮助审稿人理解模块间数据流

#### 任务 6.3：补全 ESN 超参数表

- [ ] 在 Table II 中增加（R1-C5）：
  - Reservoir size R
  - Spectral radius
  - Input scaling
  - Leak rate
  - Activation function + 选择理由
  - Readout regularization
  - Echo-state property 验证方式

#### 任务 6.4：撰写 Response Letter

- [ ] 基于 `response_letter.md` 模板逐条回复 35 个审稿意见
- [ ] 每条回复包含：审稿人原文 → 我们的回复 → 具体修改位置
- [ ] 语气：尊重、感谢、具体（不泛泛而谈"we have improved"）
- [ ] 标注哪些修改需要审稿人重新审查

#### 任务 6.5：最终检查

- [ ] 编译 `main.tex` 确认无错误
- [ ] 检查页数、图表分辨率、参考文献格式
- [ ] 生成最终 PDF
- [ ] Git tag: `v2.0-resubmission`

---

## 四、时间线总览

```
Week 1  (Day  1- 2):  阶段0 — 导师对齐 + 环境准备
Week 1  (Day  3- 7):  阶段1 — WP3 Reward & Underlay 修复
Week 2  (Day  8-12):  阶段2 — WP2 DQI 形式化
Week 3-4 (Day 13-25): 阶段3 — WP4 实验增强（期间可并行跑实验）
Week 5  (Day 26-32):  阶段4 — WP1 创新性重写
Week 6  (Day 33-37):  阶段5 — WP5 部署与开销分析
Week 7  (Day 38-45):  阶段6 — WP6 语言精修 + Response Letter

总计：约 45 天（120 天窗口内留有充足缓冲）
```

---

## 五、风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 新实验无法在规定时间内完成 | 中 | 高 | WP4 按优先级排序，核心实验优先；如时间不够，次要实验改为 discussion |
| 仿真代码与论文不一致 | 中 | 高 | 阶段0 即做代码审计，早发现早修复 |
| Reward 修正导致性能下降 | 低 | 高 | 保留 baseline 快照；reward 修正后重新调参 |
| 创新性重写不被导师认可 | 低 | 中 | 阶段0 先对齐核心定位决策 |
| 审稿人仍认为贡献不足 | 中 | 高 | 做好转投备选方案；修改本身已显著提升论文质量 |

---

## 六、修改-审稿人覆盖矩阵

| 审稿意见 | 阶段 | 任务 | 类型 |
|----------|------|------|------|
| R1-C1 | 全部 | Umbrella comment | - |
| R1-C2 | WP2 | 2.1 DQI 训练目标 | 文字+可选实验 |
| R1-C3 | WP3 | 1.1 Reward 重写 | 文字 |
| R1-C4 | WP3 | 1.4 SU-PU 信道获取 | 文字+可选实验 |
| R1-C5 | WP6 | 6.3 ESN 超参数表 | 文字 |
| R1-C6 | WP2 | 2.3 Predictor 架构 | 文字+可选实验 |
| R1-C7 | WP4 | 3.1 仿真环境说明 | 文字 |
| R1-C8 | WP3 | 1.2 Underlay 功率控制 | 文字 |
| R1-C9 | WP4 | 3.5 鲁棒性 + 3.6 Violation rate | **新实验** |
| R1-C10 | WP4 | 3.3 大规模 + 3.4 统计 | **新实验** |
| R1-C11 | WP5 | 5.2 开销量化 + 5.3 敏感性 | 文字+可选实验 |
| R2-C1 | WP1 | 4.3 贡献列表 + WP4 消融 | 文字 |
| R2-C2 | WP1 | 4.1-4.7 全面重写 | 文字 |
| R2-C3 | WP1 | 4.5 Regime-dependent | 文字 |
| R2-C4 | WP1 | 4.4 Related Work 补充引用 | 文字 |
| R2-C5 | WP4 | 3.5 PU 流量变化实验 | **新实验** |
| R2-C6 | WP6 | 6.2 模块流程图 | 文字 |
| R2-C7 | WP4 | 3.2 强 DRL baseline | **新实验** |
| R2-C8 | WP5 | 5.4 复杂度分析 + 5.5 局限性 | 文字+可选实验 |
| R2-C9 | WP5 | 5.1 MEC/RSU 架构 | 文字 |
| R2-C10 | WP1 | 4.7 Conclusion | 文字 |
| R2-C11 | WP6 | 6.1 语言润色 | 文字 |
| R3-C1 | WP1 | 4.6 ESN-DDQN Rationale | 文字 |
| R3-C2 | WP5 | 5.4 复杂度 trade-off | 文字+可选实验 |
| R3-C3 | WP2 | 2.2 DQI baseline | **新实验** |
| R3-C4 | WP2 | 2.4 DQI 特征扩展 | 文字 |
| R3-C5 | WP2 | 2.5 特征互补性 | 文字 |
| R3-C6 | WP3 | 1.3 Violation penalty | 文字+**新实验** |
| R3-C7 | WP4 | 3.3 大规模场景 | **新实验** |
| R3-C8 | WP4 | 3.2 强 DRL baseline | **新实验** |
| R3-C9 | WP1 | 全部 WP1 任务 | 文字 |
| R4-C1 | WP1 | 4.1-4.7 全面重写 | 文字 |
| R4-C2 | WP1 | 4.5 Regime-dependent + 4.7 | 文字 |
| R4-C3 | WP5 | 5.1-5.5 全部部署分析 | 文字+可选实验 |
| R4-C4 | WP1 | 全部 WP1 任务 | 文字 |

**统计**：
- 纯文字修改：~20 条
- 必须新实验：~8 条
- 可选新实验：~7 条

---

## 七、下一步行动（立即执行）

1. **今天**：将本计划发给导师，确认阶段0的 5 个核心决策
2. **本周**：完成代码审计，确认仿真可复现
3. **下周一开始**：进入 WP3 — Reward & Underlay 修复

---

> 附录：所有审稿意见编号与 `revision_matrix.md` 保持一致。修改过程中如发现新的审稿意见细节，应及时更新本计划和 `revision_matrix.md`。
