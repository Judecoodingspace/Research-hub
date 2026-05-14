# Liu 等 (2024) — Joint Collaborative Big Spectrum Data Sensing and Reinforcement Learning Based Dynamic Spectrum Access for CIoV

> **来源**：IEEE Transactions on Intelligent Transportation Systems, Vol. 25, No. 1, January 2024
> **作者**：Xin Liu 等
> **分析日期**：2026-05-12
> **对照主线**：`paper_specs/paper2-cvn-dsa/spec.md` | `paper_specs/paper2-cvn-dsa/paper2_main_thread.md`

---

## 1. Problem

论文试图解决**认知车联网（CIoV）中的动态频谱接入（DSA）问题**：如何在保护主用户（PU）不受有害干扰的前提下，使车载终端（VT）最大化频谱利用率和通信 QoS。

按照通用分类，该论文的问题偏向：

| 类别 | 主/辅 | 说明 |
|------|------|------|
| **传输效率不足** | **主** | VT 在频谱稀缺时仅靠 overlay（空闲传输）会导致大量通信中断；论文旨在通过多模式接入提升吞吐量 |
| **资源分配不合理** | **主** | 多信道在多 VT 间的分配未考虑 PU 保护约束下的模式选择 |
| **决策触发条件不明确** | **主** | 何时用 overlay、何时用 underlay、何时用 collaborative relay——论文引入 Q-learning 学习这一切换 |
| **感知质量不足** | **辅** | 协同频谱感知用于提高检测概率，但论文不做信道质量评估（无 DQI） |
| 推理/计算实时性不足 | 未涉及 | 使用传统 Q-learning，无收敛加速设计 |

> **Paper 2 对照**：Liu 2024 与 Paper 2 的核心问题高度重叠——都关注"信道选择 + 模式切换 + PU 保护"。但 Liu 2024 缺少 Paper 2 的核心维度：**信道质量评估（DQI）和占用预测（Prediction）**——它的频谱感知仅回答"信道是否空闲"（occupancy-only）。

---

## 2. Setting / Assumptions

| 维度 | Liu 2024 | Paper 2 | 差异评注 |
|------|----------|---------|----------|
| **网络类型** | CIoV（认知车联网） | CVN（认知车联网） | 同领域 |
| **节点数量** | M=5 信道, N=3 VT（固定） | M=3,5 / N=3,5（两种配置） | Liu 实验更单一 |
| **部署架构** | 车辆本地感知 + 本地 Q-learning（纯分布式） | 集中式服务器（DQI+预测）+ VT 本地（ESN-DDQN 轻量推理） | **重大差异**：Liu 是纯分布式，Paper 2 是混合架构 |
| **接入模式** | **三种**：Overlay / Underlay / **Collaborative (relay)** | **两种**：Overlay / Underlay | Liu 多了协作中继模式（VT 先帮 PU 传再传自己） |
| **PU 模型** | 两状态 Markov, 转移概率 50% | 两状态 Markov, p01=p10=0.2 | Liu 的 PU 更活跃（更快切换） |
| **算力条件** | 同构（每车本地独立 Q-table） | 异构（服务器重计算 + VT 轻推理） | Liu 无计算卸载概念 |
| **通信条件** | Rayleigh 衰落信道，增益 -20~0dB | 动态信道，带宽 200 kHz | 相似 |
| **移动性** | **未建模移动性** | 高移动性（50-120 km/h） | **重大差异**：Liu 无速度/多普勒建模 |
| **频谱感知** | 协同频谱感知（CSS）：多车协作检测，含 OR/AND 融合 | 瞬时感知 δ_t（VT 本地） | Liu 的感知更复杂（含协同融合规则） |
| **信道质量评估** | **无** | Transformer DQI（SNR+RSS+B） | Liu 只关心占用状态，不关心质量 |
| **占用预测** | **无** | Attention-LSTM 预测空闲概率 | Liu 不做预测 |
| **训练规模** | 100 次实验 × 20,000 slots | 20 episodes × 5,000 slots | Liu 多 5 倍 slot |
| **多视角同步** | N/A | N/A | 两者均不涉及 |

**关键判断**：Liu 2024 的设定比 Paper 2 更简单——无信道质量评估、无占用预测、无移动性代价建模、无服务器端计算。但它多了一个 Paper 2 没有的模式：**协作中继（Collaborative relay）**，即 VT 先帮助 PU 完成通信再传输自己的数据。

---

## 3. Core Idea

**用一个统一的 Q-learning agent 同时学习"选哪条信道 + 用哪种接入模式 + 是否做协作中继"**。

设计逻辑：
- 频谱稀缺 → 用 Underlay（低功率共存）或 Collaborative（先帮 PU 传再传自己）来增加接入机会
- 频谱充裕 → 用 Overlay（空闲信道传输，零干扰）
- 将 PU 保护编码为 reward 的惩罚项（干扰惩罚系数 γ × 信道增益 × 功率），使 agent 自学避免干扰 PU

---

## 4. Key Mechanism

### 4.1 三种接入模式的数学模型

| 模式 | 触发条件 | 核心机制 | PU 干扰处理 |
|------|---------|----------|------------|
| **Overlay** | 信道空闲 (st=0) | Shannnon 容量公式，正常功率 | 零干扰（只选 idle 信道） |
| **Underlay** | 信道忙 (st=1) | 功率控制至 PU 干扰门限以下；含干扰惩罚 reward | 约束 `P_t ≤ ξ_m1/|h|²`（闭式） |
| **Collaborative** | 信道忙 (st=1 或 st=2) | VT 充当中继，先帮 PU/其他 VT 传 T_c 时间，剩余时间传自己 | 零干扰（协作完成后 PU 已离开） |

### 4.2 状态空间
```
S_t^n = {st_n,1, st_n,2, ..., st_n,M}
其中 st_n,m ∈ {0,1,2,3}：
  0 = idle
  1 = 仅一个 PU 占用
  2 = 仅一个 SU 占用
  3 = 多于一个用户占用
```

### 4.3 动作空间
```
A_t^n = [at_n,1, at_n,2]
  at_n,1 ∈ {0,1,...,M}：信道索引
  at_n,2 ∈ {0, P_low, P_high}：发射功率级
```

### 4.4 Reward 设计（统一公式）
```
R_t^n = λ_n × T_t^n − χ·θ_m·W_m·T_t^n − I_n
```
其中：
- λ_n × T_t^n = 吞吐量 × 通信时间
- χ·θ_m·W_m·T_t^n = 带宽价格项（动态定价：busy 信道价格更高 θ_m,1 > θ_m,2）
- I_n = 干扰惩罚（γ × 信道增益 × 功率）

根据不同信道状态和模式，reward 分 5 种 situation 计算（见论文 §V.A-E）。

### 4.5 Q-Learning 更新
标准 Q-learning：
```
Q(S,A) ← (1-α)·Q(S,A) + α[R + β·max_a' Q(S', a')]
α = 1/(1+0.0025t)  （学习率随时间衰减）
```

### 4.6 协同频谱感知（CSS）
在接入前，多辆 VT 协作检测各信道的 PU 占用状态，使用 OR/AND 融合规则提高检测概率。

> **Paper 2 对照**：Liu 2024 的机制与 Paper 2 的 3 层 Pipeline 形成鲜明对比——它用**单一 Q-learning** 统一解决信道选择 + 模式切换，而 Paper 2 拆为 3 层专用模块（DQI Transformer + Attention-LSTM 预测 + ESN-DDQN）。这直接触及 Paper 2 审稿人的核心质疑：**"3 个模块是否必要？一个更简单的方法能不能做到？"**

---

## 5. Experiments

### 5.1 实验设置
| 参数 | Liu 2024 | Paper 2 比较 |
|------|----------|-------------|
| M, N | M=5, N=3 (M>N)；M=3, N=5 (M<N，隐含) | 同有 M<N 和 M>N 两种场景 |
| 训练规模 | **100 次实验 × 20,000 slots** | 20 episodes × 5,000 slots |
| 对比方案 | Overlay-only / Underlay-only / Collaborative（三者互相对比，**无消融**） | Full Model + 4 个 ablation（No-DQI, No-Prediction, Fixed Overlay, Fixed Underlay） |
| 指标 | Avg-Reward, CIoV Throughput, PU Throughput, Interference Power, Outage Ratio | PLR, VT-TP, PU-TP, Avg-DQI, Conv-Speed |
| 信道模型 | Rayleigh fading (-20~0dB) | 未详细说明 |

### 5.2 关键实验结果

**M<N（频谱稀缺，3信道/5车）**：
- Underlay 奖励 > Collaborative > Overlay
- Collaborative 的 CIoV 吞吐最高（因无功率限制 + 可利用 busy 信道）
- Collaborative 的 PU 吞吐 = Overlay（学习后避免干扰 PU）
- Underlay 的干扰功率最高且不收敛到 0（无法完全避免）
- Collaborative 的中断比最低（收敛至 ~0.05）

**M>N（频谱充裕，5信道/3车）**：
- Underlay 的 CIoV 吞吐反而低于 Overlay（频谱充裕时，underlay 功率受限是劣势）
- 三种模式的 PU 吞吐和中断比都接近，差异缩小

### 5.3 实验评价（对照 Paper 2 需求）

| Paper 2 的审稿人需求 | Liu 2024 是否覆盖？ | 评注 |
|----------------------|-------------------|------|
| 大规模 M/N (10~30, 15~30) | ❌ 未覆盖 | 仅 M=3,5 / N=3,5 |
| 强 DRL baseline (DDQN/PPO) | ❌ 未覆盖 | 仅三种模式互相对比，无其他 RL baseline |
| Violation Rate | ❌ 未显式给出 | 有"干扰功率"指标但无违规率 |
| Error bar / 置信区间 | ❌ 未给 | 仅给出 100 次实验的平均值 |
| 多种 PU 流量 (p01/p10 组合) | ❌ 未覆盖 | 固定 50% 转移概率 |
| 预测误差鲁棒性 | ❌ N/A | 无预测模块 |
| 消融实验 | ❌ **无** | 三种模式互相作为 baseline，但没有逐步移除组件的消融 |
| 通信开销分析 | ❌ 无 | 纯分布式，无服务器→VT 通信 |

**关键发现**：Liu 2024 的实验虽然比 Paper 2 多 10 倍 slot 数（100×20,000 vs 20×5,000），但实验设计更简单——没有消融、没有多 DRL baseline、没有 error bar、单 PU 流量模式。**这说明"已有工作也没做到 Paper 2 审稿人要求的实验深度"**，可作为 Paper 2 审稿回复中的局部防御素材（见 §11.4）。

---

## 6. Strength

1. **三模式联合建模**：Overlay + Underlay + Collaborative 在同一个 Q-learning 框架中统一了信道选择与模式切换，比仅做 overlay/underlay 二选一的工作更完整
2. **协作中继模式**：VT 先帮助 PU 通信、再传输自己的数据——这种 win-win 的中继设计在 Paper 2 中完全没有考虑，是一个有潜力的扩展方向
3. **动态频谱定价机制**：利用 θ_m（busy/idle 动态带宽价格）引导 agent 避免选 busy 信道——一种非惩罚方式实现 PU 保护
4. **协同频谱感知**：多车协作检测提高检测概率，含 OR/AND 融合规则的可切换设计
5. **两种频谱供需场景**：M<N 和 M>N 下的对比实验揭示了频谱充裕度对模式选择的影响（Underlay 在 M>N 时反而劣势）——与 Paper 2 的 Finding 4 形式相近

---

## 7. Weakness

| 弱点类型 | 具体表现 | Paper 2 对照 |
|----------|---------|-------------|
| **只做局部优化** | 仅做信道接入决策，无质量评估、无预测 | 衬托 Paper 2 的 3 层 Pipeline 提供了更完整的全链路视角 |
| **强调通信但缺乏任务导向** | 优化吞吐、中断比，但 PU 保护的语义不明确（只有干扰功率，没有违规率） | Paper 2 同样面临此质疑（审稿人要求加 violation rate） |
| **无移动性建模** | 论文标题是"CIoV"，但未建模车辆速度、多普勒效应、信道切换成本 | Paper 2 显式建模速度 50-120 km/h，是差异化优势 |
| **无消融实验** | 三种模式互相对比不能证明各组件的必要性 | Paper 2 的消融（No-DQI/No-Prediction）实验设计更强 |
| **Q-learning 的维度诅咒** | state 维度 = M（信道数）× 通信状态数，扩展到大规模会很困难 | Paper 2 用 ESN-DDQN 缓解此问题 |
| **动作空间粗糙** | 仅 3 级功率（0/P_low/P_high），非连续控制 | Paper 2 用离散 channel×mode 动作（2M+1）更细粒度 |
| **实验支撑不足** | 无 error bar、无 violation rate、无多 DRL baseline、无大规模测试 | 同 Paper 2 的弱点，但 Liu 更弱（甚至无消融） |
| **方法陈旧** | Q-learning（1989 年）作为 2024 年 IEEE TITS 论文的主要方法，创新性存疑 | 衬托 Paper 2 的 ESN-DDQN + Transformer DQI 有更强的技术前沿性论证空间 |

---

## 8. Reusable Part

### 可直接复用于 Paper 2 的内容：

1. **Collaborative relay 模式的建模方式**（§V.D）：可作为 Paper 2 的 future work 扩展方向——在"自适应 overlay/underlay 切换"基础上增加协作中继选项
2. **动态频谱定价机制**（θ_m busy/idle 差异化价格）：可作为 Paper 2 reward 设计中除 Γ/∂/Ω 之外的备选 PU 保护编码方式
3. **协同频谱感知（CSS）的融合规则**（OR/AND）：可为 Paper 2 的"瞬时感知 δ_t"模块提供更细粒度的感知建模参考
4. **两场景（M<N / M>N）对比实验的叙述逻辑**：Liu 的表述方式（"频谱充裕时 underlay 反而劣势"）可作为 Paper 2 Finding 4 的外部佐证
5. **Related Work 的文献列举**：Liu 引用 [13] Chang 2019 "Distributive DSA through DRL: A reservoir computing-based approach"——这篇是关于 ESN 在 DSA 中的早期工作，Paper 2 必须引用和区隔
6. **问题陈述逻辑**："频谱稀缺 → 需要非 overlay 的接入模式"的递进论述，Paper 2 可复用

---

## 9. Attack Point

| 切入维度 | 具体方向 | Paper 2 的差异化优势 |
|----------|---------|---------------------|
| **缺少质量感知** | Liu 只判断"信道空不空"，不判断"信道好不好" | Paper 2 的 DQI 正是填补此空白 |
| **缺少占用预测** | Liu 不做预测，agent 只能反应式选信道 | Paper 2 的 Attention-LSTM 预测能提前避免中断 |
| **无移动性适应** | Liu 是静态信道模型 | Paper 2 的高移动性 ESN-DDQN 快速收敛是有场景支撑的差异化 |
| **无计算卸载** | Liu 是纯分布式，所有 VT 各自维护 Q-table | Paper 2 的服务器-客户端混合架构有部署新颖性 |
| **无消融实验** | 无法证明各组件的独立贡献 | Paper 2 的系统消融（No-DQI/No-Prediction/No-Predict/Full Model）是方法论优势 |
| **Q-learning 扩展性差** | Q-table 随 M 线性增长，不适合大规模 | Paper 2 的 NN-based DDQN 可处理更大状态空间 |

> **Attack Point 的核心叙事**：Liu 2024 代表了"occupancy-only Q-learning for DSA"这一类典型工作，Paper 2 可将其定位为 baseline 锚点，然后逐层论证"DQI 质量评估 + 占用预测 + ESN 加速收敛"三个新增维度的必要性。

---

## 10. Relation to My Topic

### Paper 2 与 Liu 2024 的关系矩阵

| 维度 | Liu 2024 | Paper 2 | 关系 |
|------|----------|---------|------|
| 问题域 | CIoV 频谱接入 | CVN 频谱接入 | **同域，可直接比较** |
| 接入模式 | Overlay / Underlay / Collaborative | Overlay / Underlay | Paper 2 少了 Collaborative，Liu 可作为 future work 引用 |
| 状态表征 | occupancy-only（4 值信道状态） | 三合一：感知+质量+预测 | **Paper 2 的状态设计是 Liu 的超集** |
| 决策方法 | 标准 Q-learning | ESN-DDQN | Paper 2 方法更先进 |
| 质量感知 | 无 | Transformer DQI | **Paper 2 独有的维度** |
| 预测 | 无 | Attention-LSTM | **Paper 2 独有的维度** |
| 实验深度 | 无消融、无 error bar | 有消融、计划加 error bar | Paper 2 实验设计更强 |
| PU 保护编码 | 干扰惩罚 + 动态定价 | 差异化 reward + 违规惩罚 | 互补关系 |

### 具体定位：

| 定位角色 | 说明 |
|----------|------|
| **前置工作 / baseline 锚点** | Liu 2024 是典型的"occupancy-only Q-learning DSA"，Paper 2 可将其作为 Related Work 中的 baseline 级引用，展示从"只看空闲"到"看质量+预测"的演进 |
| **功能覆盖对比的参照物** | Paper 2 的 Gap Matrix 可将 Liu 列为"A 行"——覆盖了 overlay/underlay/collaborative 但缺失 DQI/Prediction/ESN/mobility |
| **实验深度的行业对标** | Liu 2024（IEEE TITS 2024）的实验也只有 M=3,5、无 error bar、无 violation rate——可用于防御"已有工作也做不到大规模/多指标" |
| **Future work 的方向提示** | Liu 的 Collaborative relay 模式可作为 Paper 2 结论中 limitations 段落的扩展方向 |

---

## 11. Scenario-Experiment Justification（场景-实验双重合理化）

### 11.1 Scenario → Algorithm Mapping（场景特征到算法选择的必要性映射）

| 场景特征 | 引发的技术需求 | 选择的算法/模型 | 必要性强度 | 评注 |
|----------|--------------|----------------|-----------|------|
| 多信道 + PU 随机占用 | 需要区分信道状态做接入 | Q-learning（occupancy-based state） | **强** | Q-learning 是解决此问题的合理选择 |
| 频谱稀缺（M<N） | 仅 overlay 不够，需要更多接入机会 | Underlay + Collaborative 模式 | **强** | Underlay/Collaborative 的场景驱动力合理 |
| PU 需保护 | 避免 SU 干扰 PU | 干扰惩罚 reward + 动态定价 θ_m | **中** | 两种 PU 保护编码有冗余嫌疑（为何需要两种？） |
| 单 VT 频谱感知不可靠 | 需要多 VT 协作检测 | 协同频谱感知（CSS）OR/AND 融合 | **中** | CSS 在 2024 年已是成熟技术，创新有限 |
| 无移动性要求 | 无 | 不需要收敛加速 | N/A | 论文标题含"CIoV"但无移动性建模是缺失 |

**是否存在"因为某技术流行所以使用"的嫌疑？**：Q-learning 和 CSS 的选择有场景支撑，但**动态频谱定价机制（θ_m）与干扰惩罚（γ）同时存在**——两者都是 PU 保护的编码方式，论文未论证为什么两者都需要，存在技术冗余嫌疑。

### 11.2 Ablation & Necessity Evidence（消融与必要性证据）

| 问题 | 答案 |
|------|------|
| 论文是否提供了消融实验？ | **否**。三种模式（Overlay/Underlay/Collaborative）互相对比，但这是模式级别的对比，不是组件级别的消融 |
| 是否证明了每个模块的独立贡献？ | **否**。无法区分"Q-learning 的贡献"vs"某种模式的贡献"vs"CGS 的贡献" |
| 组合收益是否大于各部分之和？ | **无法判断**（无消融数据） |
| 无消融时用什么其他方式论证？ | 通过不同模式在不同频谱供需场景下的性能反转来间接论证（M<N 时 Underlay>Overlay，M>N 时反转） |

> **Paper 2 对照**：这是 Liu 2024 最薄弱的环节，也是 Paper 2 最强的防御点。Paper 2 的消融设计（No-DQI/No-Prediction 分别移除）直接展示了每个模块在两种 M/N 场景下的独立贡献——这正是审稿人最想看到的"为什么需要 X"的证据。

### 11.3 "Why Not Simpler" Logic（替代方案排除逻辑）

| 问题 | 答案 |
|------|------|
| 论文是否讨论了"为什么不用更简单的方案"？ | **否**。没有论证为什么选 Q-learning 而不是 rule-based（如优先选 idle 信道、固定功率），没有论证为什么需要 3 种模式而不是 2 种 |
| 是否设置了简单 baseline？ | 部分有——Overlay-only 和 Underlay-only 可作为简单 baseline，但**无 random、无 fixed-threshold、无 rule-based** |
| 是否存在"杀鸡用牛刀"的过度设计嫌疑？ | **轻微**。Q-learning 本身不算重，但 2024 年仍用 tabular Q-learning 反而引发"为什么不用 DQN"的反向质疑 |

### 11.4 Defensibility Summary（可防御性总结）

**对 Liu 2024 的总结**：

Liu 2024 的方法论**不能很好地经受"你在堆砌技术"的质疑**。场景约束到技术选择的因果链部分成立（频谱稀缺 → 需要 Underlay/Collaborative），但存在两个关键漏洞：(1) **双重 PU 保护机制（干扰惩罚 + 动态定价）缺乏必要性论证**——为什么两者都要？(2) **无消融实验**使每个组件的独立贡献不可知。

**对 Paper 2 的防御价值**：

Liu 2024 为 Paper 2 提供了两类防御素材：
1. **弱 baseline 对比**：Liu 2024（IEEE TITS 2024）的实验也缺少 error bar、violation rate、大规模 M/N、强 DRL baseline——Paper 2 可在审稿回复中引用："Even recent TITS publications in the same domain (e.g., Liu 2024) do not report error bars or violation rates, indicating this is a broader community practice rather than an isolated weakness of our work."
2. **"为什么需要质量评估+预测"的反证**：Liu 2024 只做 occupancy-only 接入，实验显示其在 M<N 时 Underlay 模式下的 PU 干扰功率持续存在——说明"只看信道是否空闲"不足以保护 PU。这从外部佐证了 Paper 2 引入 DQI 和 Prediction 的必要性。

---

## 12. 审稿回复专项价值

| 审稿关注点 | Liu 2024 的支撑价值 |
|-----------|-------------------|
| R3-C1: ESN-RL 非全新 | Liu 2024 Ref [13] Chang 2019 是 ESN 在 DSA 中的早期尝试——Paper 2 需引用并区隔（"early attempt without quality+prediction"） |
| R3-C3: 3 特征用 Transformer 过度设计 | Liu 2024 的 occupancy-only state 更简单但导致 PU 干扰——反证单纯简化不够 |
| R1-C10: 缺 error bar + 大规模场景 | Liu 2024 也没有——可作为"行业惯例"防御 |
| R2-C7: 缺强 DRL baseline | Liu 2024 也没有强 baseline——可用"行业惯例"防御，但更建议 Paper 2 主动补齐 |
| R1-C9: 缺 violation rate | Liu 2024 也没有 violation rate，只用"平均干扰功率"——说明 violation rate 在 DSA 领域尚未成为标准指标 |

---

> **后续行动**：
> - 将本文加入 `papercard/CVN-DSA/index.md` 文献列表
> - 更新 `compare/CVN-DSA/overview.md` 加入 Liu 2024 的对比位置
> - 在 `rebuttal/cvn-dsa/planning/lit_support_matrix.md` 中注册本文的审稿回复支撑条目
