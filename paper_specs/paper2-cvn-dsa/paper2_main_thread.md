# 小论文主线梳理 — CVN 质量感知自适应频谱接入

> 基于 `main.tex` 全文提取 + 4 位审稿人意见对照 | 生成日期: 2026-05-12
> 用于：跨对话对比分析、修改方向对齐、导师讨论

---

## 一、场景设定（Scenario）

### 物理场景
- **认知车联网（CVN）**：多条授权信道（属于主用户 PU），多个车载终端（VT，作为次级用户 SU）竞争接入
- **BS/RSU 覆盖**：基站周期采集各信道的历史测量数据（SNR、RSS、带宽），上传至集中式服务器
- **集中式服务器（MEC/RSU-assisted）**：运行 DQI 质量评估 + 信道占用预测，广播摘要给 VT
- **VT 本地**：频谱感知 + ESN-DDQN 轻量推理 → 选信道 + 选接入模式 → 传输

### 两种接入模式
- **Overlay**：只在检测到信道空闲时传输（零干扰 PU，但易被 PU 突然返回打断）
- **Underlay**：允许在 PU 占用信道时低功率共存（需满足 PU 干扰容限约束，否则违规受罚）

### 三个时序层次的信息
| 层次 | 信息 | 获取方 | 更新频率 |
|------|------|--------|---------|
| 瞬时感知 | δ_t（信道空闲/占用） | VT 本地 | 每 slot |
| 中时间尺度 | Φ'_t（DQI 信道质量指数） | 服务器→广播 | 每 T_upd slot |
| 短时预测 | θ_t（预测空闲概率） | 服务器→广播 | 每 T_upd slot |

---

## 二、核心问题（Problem）

> **在认知车联网高移动性场景中，车载终端面临一个根本矛盾：仅凭"信道是否空闲"做接入决策不可靠——空闲信道质量可能很差、感知误差和 PU 突然返回会触发碰撞与中断、underlay 机会不等于 PU 安全的接入。如何设计一个联合考虑信道质量、占用预测和接入模式切换的自适应频谱接入框架，使 VT 的通信 QoS 最大化同时保护 PU 不受有害干扰？**

拆成三个子问题：

| 子问题 | 具体表述 |
|---|---|
| **子问题 1：质量感知** | 如何用一个统一的指标（DQI）量化"这条空闲信道到底好不好用"？仅靠 SNR/RSS/带宽的瞬时值不够，需要跨信道、跨时间的联合评估 |
| **子问题 2：预测辅助** | 当前空闲 ≠ 下一秒还空闲。如何预测短时信道占用概率，提前避免 PU 返回导致的中断？ |
| **子问题 3：自适应模式切换** | 什么时候该用 overlay（安全但机会少），什么时候该用 underlay（机会多但有违规风险）？需要一个能快速收敛的 RL 策略来学习这个切换 |

### 关键约束
- **高移动性**：VT 速度 50-120 km/h，信道条件快速变化 → RL 策略必须快速收敛
- **PU 保护**：underlay 接入必须满足 `P_t × |h_su_pu|^2 ≤ Ψ_pu`，否则违规
- **VT 计算受限**：复杂的 DQI/预测计算卸载到服务器，VT 仅做轻量推理
- **离散动作空间**：channel index × access mode 是离散组合，连续控制方法（DDPG/SAC）不适合

---

## 三、研究方法（Method）

### 整体架构（3 层 Pipeline）

```
Layer 1（服务器侧）            Layer 2（服务器侧）            Layer 3（VT 侧）
DQI 信道质量评估              信道占用预测                  ESN-DDQN 自适应接入
───────────────              ───────────────              ─────────────────
输入: M 条信道 × T slot      输入: M 条信道 × T slot       输入: {δ_t, Φ'_t, θ_t}
      的 [SNR,RSS,B] 历史         的状态序列 {0,1,2}            三合一 state vector
                             输出: θ_t^j ∈ (0,1)          输出: action ∈ {0..2M}
输出: Φ'_t^j ∈ (0,1)              下一 slot 空闲概率            channel + mode
```

### Layer 1: Transformer DQI 质量评估

**流程**：
```
[SNR, RSS, B] 历史序列 (M×T)
  → W_L 嵌入压缩 (M×T→M×d_model)
  → + 可训练位置编码
  → Transformer Encoder (Self-Attention, Q/K/V)
  → W_o + b_o 输出投影
  → Sigmoid → Φ'_t^j ∈ (0,1)
```

**关键点**：
- 自注意力捕捉跨信道质量特征的共性（信道 i 和信道 j 之间的质量关系）
- 位置编码捕捉时间依赖（T slot 内的质量演变）
- 输出 DQI 是 0~1 标量，直接作为接入决策输入
- ⚠️ 审稿人质疑：3 个低维特征用 Transformer 是否过度设计？（R3-C3）
- ⚠️ 审稿人质疑：缺少 Doppler/时延特征（R3-C4）

### Layer 2: Attention-LSTM 信道预测

**流程**：
```
Y_{t-T:t-1} (M×T, 值域{0,1,2})
  → 嵌入层 (3→hidden)
  → LSTM (含注意力时间步重加权)
  → 输出 θ_t^j ∈ (0,1) 每信道的预测空闲概率
```

**关键点**：
- 三状态建模：0=idle, 1=PU-occupied, 2=SU-occupied
- 一步前瞻训练：用 Y_{t-T:t-2} 预测 Y_{t-1}
- 注意力机制解决 vanilla LSTM 的长序列信息瓶颈
- ⚠️ 审稿人质疑：architecture details 不完整（R1-C6）

### Layer 3: ESN-DDQN 接入决策

**State Space**：
```
S_t^i = {δ_t^i (M 维, 感知), Φ'_t (M 维, DQI), θ_t (M 维, 预测)}
总维度: M × 3
```

**Action Space**：
```
action ∈ {0, 1, ..., 2M}
  0: 不接入
  2j-1: 接入信道 j, overlay 模式
  2j:   接入信道 j, underlay 模式

总维度: 2M + 1
```

**Differentiated Reward**：

| 场景 | Overlay Reward | Underlay Reward |
|------|---------------|-----------------|
| Idle 信道 | `r = Γ·(C/C_max)` | `r = Φ'·(C/C_max)` |
| PU-occupied 信道 | `r = −∂·|h_su_pu|²·P_tx/Ψ` (重罚) | `r = Φ'·(C/C_max) + ∂·(Ψ−|h|²·P)` |
| SU-occupied 信道 | `r = −∂·|h_su_su|²·P_tx` | 同上（惩罚） |

**核心设计逻辑**：
- **Overlay**：Γ=2 放大 DQI → 鼓励选高质量信道；碰到 PU 就重罚 → 避免碰撞
- **Underlay**：保持原始 DQI（不放大）→ 优先完成传输而非选最高质量；Ω 项可为正（满足约束时）→ 奖励合规的共存
- ⚠️ **审稿人指出的问题**（R1-C3, R3-C6）：原公式有歧义、缺少 interference violation penalty

**ESN-DDQN 网络结构**：
```
State → ESN Reservoir (固定, ReLU, leaky integrator)
      → W_out Readout (唯一可训练)
      → FC(256) → ReLU → FC(128) → ReLU → FC(action_dim)
```

**DDQN 更新**：
```
Q_target = r + β·Q_target(s', argmax_a Q_eval(s', a))
Loss = MSE(Q_eval(s,a), Q_target)
```

**选择 ESN 而非 LSTM 的理由**：
- Reservoir 权重固定 → 每次更新只需训练 readout 层
- BPTT 开销远低于 LSTM → 高移动性下快速收敛
- ⚠️ 审稿人质疑：ESN-RL 非全新（R3-C1）

---

## 四、实验设置（Experiments）

### 仿真环境（原论文）
| 参数 | 值 |
|------|-----|
| 信道数 M | 3, 5 |
| VT 数 N | 3, 5 |
| PU 模型 | 两状态 Markov, p01=p10=0.2 |
| 带宽 | 200 kHz |
| VT 最大功率 | 1 mW |
| 训练 | 20 episodes × 5000 slots |
| 流量 | Bernoulli 包到达, FIFO 队列 |

### 对比方案（5 个）
| 方案 | 类型 |
|------|------|
| Full Model (Proposed) | 本文完整方法 |
| Fixed Overlay | Baseline — 只 overlay |
| Fixed Underlay | Baseline — 只 underlay |
| No-Prediction | Ablation — 去掉预测模块 |
| No-DQI | Ablation — 去掉 DQI 模块 |

### 实验矩阵（两种环境）
| 环境 | M | N | 特征 |
|------|---|---|------|
| 频谱稀缺 (Scarcity) | 3 | 5 | M<N, idle 信道少 |
| 频谱充裕 (Abundance) | 5 | 3 | M>N, idle 信道多 |

### 关键指标（原论文已有）
| 指标 | 缩写 | 含义 |
|------|------|------|
| 丢包率 | PLR | 丢弃包 / 总生成包 |
| VT 平均吞吐量 | VT-TP | 每 VT 的 bps |
| PU 平均吞吐量 | PU-TP | 每 PU 的 bps |
| 平均选中 DQI | Avg-DQI | 所选信道的 DQI 均值 |
| 收敛速度 | Conv-Speed | 达到稳态的迭代数 |

### ⚠️ 审稿人要求新增的指标（实验增强 WP4）
| 指标 | 对应意见 |
|------|---------|
| PU 干扰违规率（Violation Rate） | R1-C9, R3-C6 |
| 标准差 / 置信区间 | R1-C10 |
| 大规模场景 (M=10~30, N=15~30) | R1-C10, R3-C7 |
| 强 DRL baseline (DDQN/PPO) | R2-C7, R3-C8 |
| PU 流量变化 (p01/p10 不同组合) | R2-C5 |
| 预测误差鲁棒性 | R1-C9 |

---

## 五、关键发现（Key Findings）

### Finding 1（消融实验的核心洞察）
**DQI 和 Prediction 在不同频谱供需关系下各自主导不同的性能指标**：

| 指标 | M<N (稀缺) | M>N (充裕) |
|------|-----------|-----------|
| VT Throughput | **DQI 主导**（No-DQI 急剧退化） | Prediction 主导 |
| PLR | DQI 主导 | **Prediction 主导**（No-Prediction 退化至 overlay baseline） |
| PU Throughput | **Prediction 主导**（No-Prediction 退化至 underlay baseline） | **Prediction 主导** |

→ 这是本文最有价值的系统级 insight：**质量评估和占用预测不是冗余组件，而是频谱状态互补的**（regime-complementary）。只在一种 M/N 下测试会严重低估另一个模块的价值。

### Finding 2（收敛速度）
**ESN-DDQN 在所有 baseline 中收敛最快**：
- ESN-DDQN << MLP-DDQN < Q-Learning << LSTM-DDQN
- LSTM-DDQN 最慢：BPTT 训练开销大
- ESN 的优势：reservoir 权重固定，只训练 readout → 参数减少 ~90%

### Finding 3（Full Model 综合性能）
- Full Model 在所有指标上优于 Fixed Overlay 和 Fixed Underlay
- PU Throughput 接近 Fixed Overlay（PU 保护上界）
- 同时实现高 VT QoS + 高 PU 保护 → 证明了自适应模式切换的价值

### Finding 4（Baseline 角色反转）
- M<N 时：Fixed Underlay > Fixed Overlay（共存提供更多传输机会）
- M>N 时：Fixed Overlay > Fixed Underlay（idle 信道充足，underlay 功率受限反而劣势）

---

## 六、与已有 DSA / DRL 频谱接入工作的区别

| 维度 | 已有 DSA 工作 | 本篇 |
|------|-------------|------|
| **做什么** | 主要考虑"信道是否空闲"（occupancy-only）做接入决策 | 联合考虑"是否空闲 + 质量好不好 + 未来是否还空闲"三个条件 |
| **接入模式** | 多数仅支持 overlay，少数支持 underlay | 自适应 overlay/underlay 切换，含显式 PU 干扰约束和违规惩罚 |
| **质量感知** | 极少（部分有 stability scoring，但瞬时、单维度） | 多维度 DQI（SNR+RSS+B），跨信道自注意力融合 |
| **预测** | 极少数 LSTM 预测，但与质量评估分立 | 预测概率 + DQI + 感知结果三者联合入 state |
| **收敛设计** | 标准 DQN/DDQN 或 LSTM-DQN | ESN 加速收敛：reservoir 固定 + readout 训练 |
| **实验深度** | 通常单一 M/N 配置 | M<N 和 M>N 两种场景下的系统消融 + 收敛对比 |
| **部署考虑** | 很少讨论 | 计算卸载到服务器的通信开销分析（虽然还不充分） |
| **理论分析** | 部分有 | 复杂度 O(·) 分析 |

---

## 七、当前状态与待完成

### ✅ 已完成（原论文）
- Transformer DQI + Attention-LSTM Predictor + ESN-DDQN 联合框架设计与实现
- 5 方案 × 2 场景（M<N, M>N）的完整实验
- 收敛速度对比（Q-Learning / MLP-DDQN / LSTM-DDQN / ESN-DDQN）
- 计算复杂度分析
- LaTeX 稿件（IEEEtran 格式，已投稿 TVT）

### ⬜ 待完成（审稿人要求 + 修改计划）

#### 文字修改（WP1 + WP2，约 6.5h）
- [ ] 标题重写：从"ESN-DDQN-Based Algorithm" → "Quality-Aware Framework"
- [ ] Abstract 重写：不依次列模型名，先讲三个矛盾再讲框架
- [ ] 贡献列表重写：4 条新贡献（多时间尺度状态 → 约束接入机制 → 快速策略学习 → regime insight）
- [ ] Introduction 过渡段重写
- [ ] Related Work 新增功能覆盖维度对比表（Gap Matrix）
- [ ] 实验部分新增 "Regime-Dependent Contribution Analysis" 小节
- [ ] ESN-DDQN 选择理由段落（回应 R3-C1）
- [ ] Conclusion 重写 + Limitations 段落
- [ ] 全文术语统一（删 "novel"，弱化模型名）

#### 技术修正（WP3，约 2h）
- [ ] Reward 公式重写：消除 Φ 和 Γ 的歧义（R1-C3）
- [ ] Underlay 功率控制闭式约束 P_t ≤ Ψ/|h|²（R1-C8）
- [ ] 增加 interference violation penalty（R3-C6）
- [ ] SU-PU 信道获取方式说明（R1-C4）

#### 方法补全（WP2，约 2h）
- [ ] DQI 训练目标、loss、data 定义（R1-C2）
- [ ] ESN 完整超参数表（R1-C5）
- [ ] Predictor 架构详细说明（R1-C6）
- [ ] 仿真环境完整参数表（R1-C7）

#### 实验增强（WP4，约 2-3 周）
- [ ] 至少 1 个强 DRL baseline（DDQN 或 PPO）
- [ ] 大规模场景（M=10~30, N=15~30）
- [ ] 所有图加 error bar（≥5 random seeds）
- [ ] PU interference violation rate 指标
- [ ] 不同 p01/p10 的 PU 流量鲁棒性
- [ ] 预测误差鲁棒性

#### 部署分析（WP5，约 1h）
- [ ] 通信开销公式和量化（R1-C11）
- [ ] T_upd 敏感性分析（R1-C11）
- [ ] MEC/RSU 架构重新解释（R2-C9）
- [ ] 复杂度-性能 trade-off 表（R2-C8）

#### Response Letter（WP6）
- [ ] 逐条回复 35 个审稿意见

---

## 八、核心贡献（修改后的 4 条表述）

1. **多时间尺度接入前状态表征**：首次为 CVN DSA 联合构建了"瞬时感知 + 中时间尺度质量评估 + 短时占用预测"三合一的 state representation，同时回答"信道是否空闲、是否够好、是否持续够好"三个条件——已有方法最多只覆盖其中一到两个。

2. **干扰约束的自适应 overlay/underlay 接入机制**：设计了差异化 reward——overlay 强调质量（Γ 放大 DQI）+ 零干扰，underlay 强调完成传输 + PU 阈值合规——并嵌入闭式功率约束和违规惩罚，使 agent 学习到同时平衡 VT QoS 和 PU 保护的模式切换策略。

3. **储备池计算加速的离散动作策略学习**：利用 ESN reservoir 的固定循环动力学消去 BPTT 训练开销，仅需训练 readout 权重，在高移动性 CVN 中显著加速 DDQN 收敛。DDQN 的双估计器机制抑制离散 channel-mode 动作空间中的过估计。

4. **频谱状态依赖的设计规律**：通过系统消融首次揭示——频谱稀缺时 DQI 质量感知主导 VT 吞吐量，频谱充裕时预测主导中断避免和 PU 保护——证明了质量评估和占用预测是频谱状态互补的，而非冗余。该发现解释了已有工作中两类方法未被联合考虑的可能原因。

---

> **与 `paper3_main_thread.md` 对照使用提示**：本文是研究生阶段第二个工作点，与第一个工作点（UAV 语义融合中的触发决策）在方法论上有相似结构（都是"RL/预测驱动的决策触发/选择"），但应用场景从 UAV 感知迁移到 CVN 频谱接入。两篇共享的核心方法论 DNA 是：**用轻量预测 + 约束优化解决"该不该做某件事"的系统级决策问题**。
