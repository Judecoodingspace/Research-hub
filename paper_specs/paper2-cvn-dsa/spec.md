# Paper 2: CVN 质量感知自适应频谱接入 — 文献分析专属标准

> 本文件从 `paper2_main_thread.md` 提炼而来，定义对这篇论文进行文献分析时必须使用的专属对照维度。
> 通用规则（papercard 11 条结构、比较规则、空白提炼、输出风格）见仓库根目录 `Agents.md`。

---

## 一、论文锚点（必读）

当前论文的核心问题不是"如何做频谱感知"的一般性讨论，而是：

**在认知车联网高移动性场景中，如何设计一个联合考虑信道质量（DQI）、占用预测和接入模式切换（overlay/underlay）的自适应频谱接入框架，使车载终端的通信 QoS 最大化同时保护主用户不受有害干扰？**

核心关键词（用于判断文献相关性）：
- quality-aware spectrum access / DQI-based channel assessment
- multi-timescale state representation（瞬时感知 + 中时间尺度质量 + 短时预测）
- adaptive overlay/underlay mode switching
- ESN-accelerated DRL / reservoir computing for fast convergence
- discrete action space (channel × mode)
- PU protection with explicit interference constraint
- regime-complementary components（DQI 与 Prediction 频谱状态互补）
- reviewer revision context（TVT 退稿重投，35 条审稿意见待回复）

**不是**：
- 一般性的频谱感知 / 频谱检测
- 纯 overlay-only 或 underlay-only 接入
- 连续功率控制（DDPG/SAC 类方法）
- 不考虑 PU 保护的 opportunistic 接入
- 一般性的 DRL 调度综述
- 纯物理层波形设计

---

## 二、场景与约束速查

| 参数 | 值 |
|------|-----|
| 网络类型 | 认知车联网（CVN），BS/RSU 覆盖 |
| 信道数 M | 3, 5（小规模）；审稿人要求扩展至 10~30 |
| VT 数 N | 3, 5（小规模）；审稿人要求扩展至 15~30 |
| VT 速度 | 50-120 km/h（高移动性） |
| PU 模型 | 两状态 Markov，p01=p10=0.2 |
| 带宽 | 200 kHz |
| VT 最大功率 | 1 mW |
| 部署架构 | 集中式服务器（DQI + 预测）+ VT 本地（ESN-DDQN 轻量推理） |
| 接入模式 | Overlay（空闲传输，零干扰 PU）/ Underlay（低功率共存，需满足 PU 干扰容限） |
| 动作空间 | 2M+1 离散动作（M 信道 × 2 模式 + 不接入） |
| 训练 | 20 episodes × 5000 slots |
| 流量 | Bernoulli 包到达，FIFO 队列 |
| 两种测试场景 | 频谱稀缺 M<N / 频谱充裕 M>N |

---

## 三、专属对照维度（Cross-Reference Dimensions）

精读其他论文时，**必须**对照以下维度（来源：`paper2_main_thread.md` 第六节、第七节）：

| 对照维度 | 核心问题 | papercard 位置 |
|----------|---------|---------------|
| **设定差异** | 被分析论文的频谱接入场景（单信道/多信道、overlay-only/underlay-only/混合、集中式/分布式）与当前论文有何异同？差异对当前论文是威胁还是机会？ | §2 / §10 |
| **方法验证/挑战** | 被分析论文是否联合考虑了质量评估 + 占用预测？是否区分 overlay/underlay 模式？是否处理 PU 保护约束？这些选择是否支持或质疑当前论文的 3 层 Pipeline 设计？ | §3 / §7 / §11 |
| **实验补强线索** | 被分析论文覆盖了哪些当前论文未探索的实验维度（大规模 M/N、更多 PU 流量模式、强 DRL baseline、violation rate 指标、error bar）？ | §5 |
| **写作与论证借鉴** | 被分析论文是如何论证"为什么需要这个组件而不是更简单的方案"的？审稿回复中的 Gap Matrix / 功能覆盖对比表是否可复用？ | §8 / §11 |
| **防御素材** | 被分析论文是否提供了可支撑当前论文设计合理性的外部证据（如"3 个低维特征用 Transformer 是否过度设计""ESN-RL 加速收敛的佐证""质量+预测不是冗余而是互补"）？ | §11.4 |
| **baseline 候选** | 被分析论文的方法（如 DDQN/PPO/sensing-only/overlay-only）是否可作为当前论文的对比方法或 Related Work 定位锚点？ | §10 |
| **审稿回复支撑** | 被分析论文是否覆盖了审稿人要求的某些实验维度（大规模场景、强 baseline、violation rate、误差棒）？是否可作为"已有工作也未做到 X"的防御引用？ | §10 / §11.4 |

---

## 四、当前论文的关键设计选择（用于文献对比时的压力测试）

文献对比时必须牢记以下设计选择，并评估每篇文献对这些选择的验证/挑战程度：

| 设计选择 | 说明 | 需要验证的问题 |
|----------|------|---------------|
| Transformer DQI | 3 个低维特征（SNR/RSS/B）用 Transformer 编码，含自注意力跨信道融合 + 可训练位置编码 | 是否有文献用更简单的方法实现类似的质量评估？审稿人"3 特征用 Transformer 过度设计"的质疑是否有文献反证？ |
| Attention-LSTM 预测 | 三状态（idle/PU/SU）+ 注意力时间步重加权 + 一步前瞻训练 | 是否有文献用更简单的时间序列模型（AR/普通 RNN）实现同等预测精度？是否有文献讨论预测误差对 RL 策略的鲁棒性影响？ |
| ESN-DDQN | Reservoir 固定 + Readout 可训练，加速收敛；DDQN 双估计器抑制过估计 | 是否有文献证明 ESN-RL 在高移动性场景下的收敛优势？ESN 是否在某些条件下不如 LSTM-DQN？ |
| Overlay/Underlay 模式切换 | 离散动作空间（channel × mode），非连续功率控制 | 是否有文献做连续功率控制（DDPG/SAC）？在当前离散 channel-mode 组合场景中，连续控制是否更优？ |
| 差异化 Reward | Overlay Γ 放大 DQI + 零干扰惩罚；Underlay 保持原始 DQI + PU 约束合规奖励 | 是否有文献用更简洁的 reward 设计（如单一项）？当前设计的 Γ/∂/Ω 参数是否过多？ |
| 三合一 State | 瞬时感知 δ_t + DQI Φ'_t + 预测 θ_t 联合入 state | 是否有文献只用其中 1-2 项达到相近性能？三个组件是否可能有冗余？ |
| 小规模仿真 | M=3,5 / N=3,5，20 episodes | 是否有文献在更大规模（M>20/N>30）下验证？小规模结论是否可扩展？审稿人要求的大规模实验是否有文献先例？ |

---

## 五、Critical Self-Review Rules（对当前论文保持合理怀疑）

在分析任何一篇文献时，必须将文献视为"攻击当前论文设计选择"或"暴露当前论文薄弱环节"的潜在武器。

### 5.1 识别可疑简化 / 过度设计
当前论文同时面临"某些地方可能过度设计"（Transformer for 3 features）和"某些地方可能太简单"（ESN 非全新、仿真规模小）的双向质疑：
- (a) 复杂组件的正面理由（Transformer 的自注意力跨信道融合是否是 3 特征下唯一有效方案？有无更简单的替代？）
- (b) 简单组件的崩塌条件（小规模 M,N 下的结论在大规模下是否仍然成立？ESN 在更多信道下是否仍有收敛优势？）
- (c) 文献中的替代方案应标记为"对比 candidate"还是"扩展方向"

### 5.2 不替论文辩护
不能因为当前论文"面临审稿意见需要防御"就自动将文献中所有有利发现当作支撑。文献的有利发现需要通过独立评估来确认其可靠性。

### 5.3 压力测试
对当前论文的每个设计选择，追问：
- 如果审稿人读过这篇文献，他会用文献中的什么证据来质疑当前论文？
- 当前论文（含修改计划）是否有实验证据或场景论证来回应这种质疑？
- 如果没有，这是论文的薄弱环节——必须标记（WP1-WP6 中需补充）。

### 5.4 审稿意见对齐检查
当前论文处于"退稿重投"状态，有 35 条审稿意见待回复。在分析每篇文献时必须检查：
- (a) 文献是否覆盖了审稿人要求但当前论文尚未完成的实验维度（如大规模 M/N、强 baseline、violation rate、error bar）？
- (b) 文献的方法/实验设计是否可作为"行业惯例"来支撑当前论文的某些选择？
- (c) 文献是否暴露了"已有工作也做不到"的领域瓶颈（可用于 defense: "this is an open challenge"）？

### 5.5 禁止防御性过度
在 papercard 的 §10 和 compare/overview.md 中，不能将"当前论文不做 X"直接等同于"X 不适合当前论文"。必须区分：
- "X 因场景约束不适用"（需要场景证据——如连续功率控制不适合离散 channel-mode 组合）
- "X 是合理的扩展方向但当前工作未覆盖"（标记为 future work 或审稿回复中的 limitation）
- "X 与当前方法形成互补"（可以共存）

---

## 六、与已有 DSA / DRL 频谱接入工作的区别速查

| 维度 | 已有 DSA 工作 | 本篇 Paper 2 |
|------|-------------|-------------|
| **做什么** | 主要考虑"信道是否空闲"（occupancy-only）做接入决策 | 联合考虑"是否空闲 + 质量好不好 + 未来是否还空闲"三个条件 |
| **接入模式** | 多数仅支持 overlay，少数支持 underlay | 自适应 overlay/underlay 切换，含显式 PU 干扰约束和违规惩罚 |
| **质量感知** | 极少（部分有 stability scoring，但瞬时、单维度） | 多维度 DQI（SNR+RSS+B），跨信道自注意力融合 |
| **预测** | 极少数 LSTM 预测，但与质量评估分立 | 预测概率 + DQI + 感知结果三者联合入 state |
| **收敛设计** | 标准 DQN/DDQN 或 LSTM-DQN | ESN 加速收敛：reservoir 固定 + readout 训练，参数减少 ~90% |
| **实验深度** | 通常单一 M/N 配置 | M<N 和 M>N 两种场景下的系统消融 + 收敛对比 |
| **部署考虑** | 很少讨论 | 计算卸载到服务器的通信开销分析（待增强） |
| **理论分析** | 部分有 | 复杂度 O(·) 分析 |
| **审稿状态** | — | TVT 退稿重投，35 条审稿意见 |

---

## 七、实验参数速查（用于评估文献实验覆盖度）

| 维度 | Paper 2 覆盖 | 审稿人要求新增 |
|------|-------------|---------------|
| 信道数 M | 3, 5 | 10~30 |
| VT 数 N | 3, 5 | 15~30 |
| 测试场景 | 频谱稀缺 (M<N) + 频谱充裕 (M>N) | — |
| 对比方案 | Full Model, Fixed Overlay, Fixed Underlay, No-Prediction, No-DQI | ≥1 强 DRL baseline (DDQN/PPO) |
| 训练 | 20 episodes × 5000 slots | — |
| PU 流量 | p01=p10=0.2（固定） | 多种 p01/p10 组合 |
| 随机种子 | 未报告（审稿人要求 error bar） | ≥5 random seeds |
| 指标 | PLR, VT-TP, PU-TP, Avg-DQI, Conv-Speed | Violation Rate, 标准差/置信区间 |
| 鲁棒性 | 未专门测试 | 预测误差鲁棒性 |
| 通信开销 | 未量化（审稿人要求） | T_upd 敏感性分析 |
| 收敛对比 | Q-Learning / MLP-DDQN / LSTM-DDQN / ESN-DDQN | — |

---

## 八、通用脚手架中的 Paper 2 聚焦判断

> 以下定义 Paper 2 在使用 `Agents.md` 通用脚手架时的**领域专属侧重**。
> 分析文献时，优先关注以下子项；其他子项按需选用。

### Paper 2 重点关注的 Problem 类别
在使用 §1 Problem 通用分类时，Paper 2 重点关注：
- **传输效率不足**（主：信道选择不当导致丢包/中断/低吞吐）
- **决策触发条件不明确**（主：何时 overlay？何时 underlay？选哪条信道？）
- **资源分配不合理**（主：信道资源在多 VT 间分配 + PU 保护约束下共存）
- **感知质量不足**（辅：仅靠瞬时 occupancy 感知不够，需质量+预测辅助）
- 推理/计算实时性不足（辅：高移动性下 RL 需快速收敛）

### Paper 2 重点关注的 Assumption 维度
在使用 §2 Setting/Assumptions 通用脚手架时，Paper 2 重点关注：
- 节点数量：多用户（多 VT + 多 PU）+ 集中式服务器 + BS/RSU
- 算力条件：异构（服务器做重计算 DQI+预测，VT 做轻量 ESN-DDQN）
- 通信条件：动态信道（多信道，Markov PU 占用），带宽 200 kHz
- 感知条件：含噪声（频谱感知有误差，PU 可能突然返回）
- 移动性：高动态（VT 50-120 km/h）
- 任务模型：动态任务（Bernoulli 包到达，FIFO 队列）

### Paper 2 重点关注的 Key Mechanism
在使用 §4 Key Mechanism 通用脚手架时，Paper 2 重点关注：
- 任务建模方式：马尔可夫决策过程（MDP），离散动作空间
- 信息表征方式：多时间尺度融合（瞬时感知 + DQI 质量指数 + 预测空闲概率）
- 学习类方法：ESN-DDQN（reservoir 加速 + 双估计器），奖励函数 = 差异化 Overlay/Underlay reward
- 资源调度方法：自适应 overlay/underlay 模式切换 + 干扰约束下的信道选择
- 传输与压缩机制：DQI 服务器→VT 广播通信开销（待量化）

### Paper 2 重点关注的 Weakness 类型
在使用 §7 Weakness 通用分类时，Paper 2 优先寻找：
- 算法/模型选择缺乏场景必要性论证（技术堆砌嫌疑——尤其 Transformer for 3 features）
- 方法复杂但实验支撑不足（小规模仿真、无 error bar、无 violation rate）
- 只在理想条件下成立，难以在真实平台部署（仿真环境简化，无实际硬件验证）
- 强调通信但没有体现任务完成效果（DSA 文献常见：优化 throughput 但未考虑 PU 保护/公平性）

---

## 九、四条核心贡献（修改后，用于评估文献支撑价值）

1. **多时间尺度接入前状态表征**：首次为 CVN DSA 联合构建了"瞬时感知 + 中时间尺度质量评估 + 短时占用预测"三合一的 state representation——已有方法最多只覆盖其中一到两个。

2. **干扰约束的自适应 overlay/underlay 接入机制**：差异化 reward——overlay 强调质量（Γ 放大 DQI）+ 零干扰，underlay 强调完成传输 + PU 阈值合规——含闭式功率约束和违规惩罚。

3. **储备池计算加速的离散动作策略学习**：ESN reservoir 固定循环动力学消去 BPTT 训练开销，仅需训练 readout 权重，在高移动性 CVN 中显著加速 DDQN 收敛。DDQN 双估计器抑制离散 channel-mode 动作空间中的过估计。

4. **频谱状态依赖的设计规律**：系统消融首次揭示——频谱稀缺时 DQI 主导 VT 吞吐量，频谱充裕时预测主导中断避免和 PU 保护——证明质量评估和占用预测是频谱状态互补的，而非冗余。

---

## 十、审稿回复专项（Paper 2 独有）

> Paper 2 处于 TVT 退稿重投状态，35 条审稿意见。文献分析需额外服务审稿回复。

### 审稿意见分类与文献支撑需求

| 审稿关注点 | 示例意见 | 文献分析目标 |
|-----------|---------|-------------|
| 方法原创性 | R3-C1: ESN-RL 非全新 | 寻找已有工作中 ESN-RL 在频谱接入中的先例/差异 |
| 设计合理性 | R3-C3: 3 特征用 Transformer 过度设计 | 寻找文献中 Transformer 用于低维特征编码的辩护/反例 |
| 实验充分性 | R1-C10: 缺 error bar + 大规模场景 | 寻找文献中大规模频谱接入实验的行业标准 |
| baseline 强度 | R2-C7, R3-C8: 缺强 DRL baseline | 寻找文献中频谱接入的标准 DRL baseline 集合 |
| 指标完整性 | R1-C9, R3-C6: 缺 violation rate | 寻找文献中 PU 保护指标的常用定义和测量方法 |
| 写作表达 | R1-C3: reward 公式有歧义 | 寻找文献中 reward 公式的清晰表达方式 |

### 文献分析时的审稿回复思维

分析每篇文献时额外回答：
- 该文献能否作为"行业惯例"引用以支撑当前论文的某个选择？
- 该文献是否暴露了"已有工作也做不到 X"（可用于 limitation defense）？
- 该文献的方法/实验是否可直接对标审稿人的某条意见？

---

*关联主线文档：`paper_specs/paper2-cvn-dsa/paper2_main_thread.md`*
*关联审稿材料：`rebuttal/cvn-dsa/`*
*关联比较结果：`compare/CVN-DSA/`*
*关联空白分析：`gap_map/CVN-DSA/`*
