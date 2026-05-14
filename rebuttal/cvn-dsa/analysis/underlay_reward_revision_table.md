# Underlay + Reward 修改对照表（修订版 v2）

> 基于 2026-05-13 对话上下文全程提取。
> **v1→v2 修正**：(i) 原稿公式编号以实际 `main.tex` label 为准；(ii) $|h|^{2}$ 替换为 $\hat{g}$ 的语义明确；(iii) 新增 Liu 2024 对照事实核查；(iv) Underlay reward 改用 sigmoid 门控方案。
> 原稿位置引用 `paper_specs/paper2-cvn-dsa/main.tex`。

---

## 0. 关键事实核查：Liu 2024 是否描述了 SU-PU 信道增益的获取方式？

**否。** Liu 2024 在其 Underlay 接入模型（§V-C）中直接使用了 $|\hat{h}_m^n|^2$（PU 发射机到 SU 接收机的信道增益）和 $|\tilde{g}_{m,n}|^2$（SU 到 PU 接收机的信道增益），但**全文中没有描述这些 SU-PU 链路的信道增益在实际系统中如何获取**。其仿真设定中信道增益按 Rayleigh 衰落随机生成（-20~0dB），等价于仿真层面"已知"——这与您的原稿问题完全相同。

> **结论**：Liu 2024 在"SU-PU 信道信息获取"这个问题上**不是解决方案的来源**，而是**同类问题的佐证**——"即使是已发表的 IEEE TITS 2024 论文，在 SU-PU 信道获取上也没有给出实际方案"。这可以用于审稿回复的局部防御（"该问题是领域共性问题"），但不能作为技术方案的直接支撑。

**Liu 2024 真正可复用的部分**（与 SU-PU 信道获取无关）：
- PU 功率离散化为有限档位（仿真中使用 $\{0.1, 0.5, 0.9\}$ mW）
- 干扰阈值 $\Psi$ 从 PU 最小速率需求闭式导出（Eq. 22-25）
- 四值信道状态空间
- Underlay 惩罚项的结构 $\tau(\zeta_1^m - |\hat{g}_{m,n}|^2 P_t^n)$——"阈值减去实际干扰"的差值形式

---

## 1. Overlay 模式下信道占用时的惩罚项

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §IV-B "Overlay Access Reward" 子项3，`\label{eq:reward_definition_final}` 后的 enumerate 第3条 (~line 299–307) | 同位置，公式替换 |
| **原稿公式** | $\displaystyle \Omega_t^{i,j} = \frac{\partial |h_t^{i,{\rm PU}}|^2 P_t^{i,j}}{\Psi_t^{j,{\rm PU}}}$ — 依赖 SU-PU 瞬时信道增益 $h_t^{i,{\rm PU}}$ | $\Omega_t^{i,j} = \partial \cdot \mathbf{1}(\text{PU detected on channel } j)$ — 固定惩罚，不依赖任何信道增益 |
| **原稿中对 $h_t^{i,{\rm PU}}$ 的说明** | "where $h_t^{i,{\rm{PU}}}$ is the channel gain between VT $i$ and PU at time $t$" (~line 307) — **未解释如何获取** | 删除该句。替换为："$h_t^{i,{\rm PU}}$ is not required in the revised formulation; a fixed penalty $\partial$ is applied whenever VT $i$ selects an occupied channel under overlay mode, reflecting the zero-interference commitment of overlay access." |
| **设计逻辑变化** | 按"干扰功率 / 容忍阈值"的比例惩罚 → 需要 $|h|^2$ | 与 overlay 零干扰承诺一致——"无论干扰大小，触碰就罚"。比例惩罚转移到 Underlay 模式（见 §2） |
| **审稿意见映射** | **R1-C4**（$|h_t^{i,{\rm PU}}|^2$ 如何获取？） | 彻底消除 overlay 惩罚中对 SU-PU 瞬时 CSI 的依赖 |
| **改动量** | — | 删除 $|h_t^{i,{\rm PU}}|^2$ 和分母 $\Psi_t^{j,{\rm PU}}$，改为示性函数 |
| **注意事项** | — | 对 SU-SU 碰撞（原稿子项4），仍保留 $|h_t^{i,i'}|^2$——VT 之间的信道增益可通过 V2V 导频直接估计，无需修改 |

---

## 2. Underlay 模式奖励公式（核心修改）—— Sigmoid 门控方案

### 2.1 为什么不采用乘法门控 $r = \Phi'\cdot C/C_{\max} \cdot \mathbf{1}(\Psi > |h|^2P)$

前一轮讨论中提出的"乘法门控"方案存在一个表述问题：**示性函数 $\mathbf{1}(\cdot)$ 的硬切换在数学上简洁，但物理含义不直观**——它等价于"合规时正常奖励，超标时突然归零"，审稿人可能追问"为什么不是平滑过渡？"

因此改用 **sigmoid 软门控**，既保留"合规→正 / 超标→负"的语义，又具有平滑可微的形式。

### 2.2 修订后的 Underlay Reward 公式

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §IV-B "Underlay Access Reward"，`\label{eq:reward_v3}` (~line 319–342) | 同位置，公式 + 解释段落全部替换 |
| **原稿公式** | $r_t^{i,j} = \Phi_t^{'i,j} \cdot C_t^{i,j}/C_{\max} + \Omega_t^{i,j}$，其中 $\Omega_t^{i,j} = \partial(\Psi_t^{j,{\rm PU}} - |h_t^{i,{\rm PU}}|^2 P_t^{i,j})$ | $r_t^{i,j} = \Phi_t^{'i,j} \cdot \dfrac{C_t^{i,j}}{C_{\max}} \cdot \sigma\!\big(\alpha(\Psi_t^{j,{\rm PU}} - \hat{g}_t^{i,{\rm PU}} \cdot P_t^{i,j})\big) - \kappa \cdot \big[1 - \sigma(\cdot)\big]$ |
| **新增符号定义** | — | $\sigma(x) = 1/(1+e^{-x})$ 为 sigmoid 函数；$\alpha > 0$ 为锐度参数（控制门控在阈值附近的陡峭程度）；$\hat{g}_t^{i,{\rm PU}} = 1/PL(d(\text{VT}_i, \text{PU}_j))$ 为路径损耗代理（详见 §4）；$\kappa > 0$ 为违规惩罚常数 |

### 2.3 Sigmoid 门控的物理含义

```
令 Δ = Ψ − ĝ·P  （干扰裕量，正值 = 合规，负值 = 超标）

σ(α·Δ) 在 Δ 上的行为：
  Δ >> 0  (深度合规)：σ → 1  → r ≈ Φ'·C/Cmax   (全额吞吐量奖励)
  Δ ≈ 0   (临界)：    σ ≈ 0.5 → r ≈ 0.5·Φ'·C/Cmax − 0.5·κ
  Δ << 0  (深度超标)：σ → 0  → r ≈ −κ           (全额违规惩罚)
```

**与审稿人沟通的要点**：
- R3-C6 质疑的核心是"超标时 r 仍可为正"。Sigmoid 方案确保：**当 $\Delta \ll 0$ 时 $r \to -\kappa$**，且 $\kappa$ 是显式可调的惩罚强度
- 锐度参数 $\alpha$ 控制门控的"软硬程度"：$\alpha \to \infty$ 退化为硬门控，$\alpha$ 适中则为平滑过渡——可在实验中测试 $\alpha \in \{1, 5, 10, 20\}$ 的敏感性

### 2.4 Underlay 惩罚项中使用路径损耗代理 $\hat{g}$ 替代 $|h|^2$

| 原稿 | 修订后 | 原因 |
|------|--------|------|
| $\Omega_t^{i,j} = \partial(\Psi_t^{j,{\rm PU}} - |h_t^{i,{\rm PU}}|^2 P_t^{i,j})$ — 使用瞬时信道增益 | $\Delta = \Psi_t^{j,{\rm PU}} - \hat{g}_t^{i,{\rm PU}} \cdot P_t^{i,j}$ — 使用路径损耗代理 | $|h|^2$ 在真实 V2X 中无法获取（审稿人 R1-C4 核心质疑） |
| $\hat{g}_t^{i,{\rm PU}}$ 的物理含义未定义 | $\hat{g}_t^{i,{\rm PU}} = 1/PL(d(\text{VT}_i, \text{PU}_j))$ — 仅保留距离决定的确定性路径损耗成分（大尺度），忽略阴影和小尺度衰落 | 路径损耗代理是 BS 通过 VT 位置报告 + 路径损耗模型可计算的（详见 §4） |

**重要提醒**：$\hat{g}$ 不是 $|h|^2$ 的替代品——它忽略小尺度衰落。但 sigmoid 门控 + 锐度参数 $\alpha$ 的设计使得**在阈值附近有过渡带**，而非硬判决，从而容忍估计误差。

### 2.5 与 Liu 2024 Underlay 惩罚结构的比较

| | Liu 2024 | 本文修订后 | 差异 |
|------|----------|-----------|------|
| 惩罚形式 | $\tau(\zeta_1^m - |\hat{g}_{m,n}|^2 P_t^n)$ — 线性差值 | $\sigma(\alpha(\Psi - \hat{g} \cdot P))$ — sigmoid 门控 | Liu 用线性差值（加性），本文用非线性门控（乘性-软切换） |
| 信道增益 | 仿真生成 Rayleigh 衰落（~line VI: "All channels are modeled as Rayleigh fading with gains within the range of −20 to 0dB"） | BS 计算路径损耗代理 $\hat{g} = 1/PL(d)$ | **Liu 同样未解决实际问题**——两者均依赖仿真假设 |
| 审稿回复引用策略 | — | "The difference-based penalty form in [Liu 2024, Eq. 19] shares the same spirit of threshold-aware underlay reward design, while our sigmoid-gated formulation further prevents reward sign ambiguity (R3-C6) by ensuring $r \to -\kappa$ when interference exceeds the threshold." | — |

---

## 3. Underlay 功率闭式约束（原稿缺失，新增）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | 无对应公式 | §IV-B 新增子段落，紧接 Underlay reward 之后 |
| **公式** | — | $P_t^{i,j} = \min\!\big(P_{\max},\; \Psi_t^{j,{\rm PU}} \,/\, (\hat{g}_t^{i,{\rm PU}} \cdot F)\big)$ |
| **符号说明** | — | $P_{\max}$ = VT 硬件最大发射功率（物理极限）；$\hat{g}_t^{i,{\rm PU}}$ = 路径损耗代理；$F > 1$ = 衰落裕量（如 $F = \sqrt{2}$ ≈ 3dB），用于吸收小尺度衰落的不确定性 |
| **设计逻辑** | — | 同时满足两个约束：(i) 不超硬件极限 $P_{\max}$；(ii) 在最坏情况衰落（放大 $F$ 倍）下干扰仍低于 PU 容忍阈值 |
| **审稿意见映射** | **R1-C8**（功率如何选择？控制回路？） | 闭式约束，每次 $T_{\text{upd}}$ 由 BS 重算并广播给 VT——无在线控制回路，延迟为 $T_{\text{upd}}$ |
| **改动量** | — | 新增公式 + 一段解释（~5 行） |

---

## 4. SU-PU 链路信息获取——BS 代理方案（原稿缺失，新增）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | 无对应描述 | **§III（System Model）新增子段落** "SU-PU Link Information Proxy via BS" |
| **原稿隐含假设** | 公式中直接使用 $|h_t^{i,{\rm PU}}|^2$，但未定义现实获取方式 | 明确声明：**本文不假设 SU 能测量瞬时 SU-PU 信道增益**。改用保守的路径损耗代理： |
| **Step 1: PU 功率离散化** | — | BS 长期监听各信道 PU 信号 RSS → K-means 聚类 → 分 $K$ 个功率档位（如 $K=3$：{0.1, 0.5, 0.9} mW，参考 Liu 2024 仿真设定）。将连续功率估计问题退化为离散分类问题 |
| **Step 2: 路径损耗代理** | — | BS 已知 PU 发射机位置（注册信息）和 VT 当前位置（V2X CAM 消息 10 Hz）→ 计算 $d(\text{VT}_i, \text{PU}_j)$ → 代入 3GPP V2V 路径损耗模型 → $\hat{g}_t^{i,{\rm PU}} = 1/PL(d)$ |
| **Step 3: 衰落裕量** | — | 小尺度衰落不可预测，但可通过 $F>1$ 的裕量将估计误差转换为保守的安全余量——在最坏情况衰落放大 $F$ 倍时仍保证干扰合规 |
| **审稿意见映射** | **R1-C4**（$|h|^2$ 如何实际获取？） | 不测瞬时信道增益——用"功率档位分类 + VT 位置 + 路径损耗模型 + 衰落裕量"四步构建合规预判，所有操作在 V2X 现有信令框架内完成 |
| **改动量** | — | §III 新增~8 行段落 + §IV-B 中将 $|h|^{2}$ 替换为 $\hat{g}$ + Notation Table 新增 $\hat{g}_t^{i,{\rm PU}}$ 和 $F$ 条目 |

---

## 5. 信道状态空间扩展——四值占用类型（新增维度）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §IV-A, `\label{eq:state_space}` (~line 248) | 同位置公式扩展 + §III 新增 BS 广播机制解释 |
| **原稿状态向量** | $\mathbf{S_t} = \{\delta_t, \Phi_t, \theta_t\}$ — 3 分量 | $\mathbf{S_t} = \{\delta_t, \Phi_t, \theta_t, \mathbf{\rho_t}\}$ — 新增第 4 分量 |
| **$\rho_t^j$ 的取值** | 无 | BS 广播的占用类型指示符：0=idle, 1=PU 独占, 2=SU 独占, 3=多用户冲突 |
| **$\rho_t$ 与 $\theta_t$ 的关系** | — | $\rho_t$ = 当前观测的细化类型（BS 侧实时判断），$\theta_t$ = 未来空闲概率预测（不变）——两者**正交**，不需要修改预测模型 |
| **$\rho_t$ 与 $\delta_t$ 的关系** | — | $\delta_t$ 维持 2 值感知（不变），$\rho_t$ 提供 BS 侧的补充细化——当 $\delta_t=1$（busy）时，$\rho_t$ 进一步区分 PU/SU/冲突 |
| **Action Masking** | 无 | $\rho_t^j \in \{2,3\}$ 时 → Underlay 动作被硬屏蔽（Layer 3 硬阻断） |
| **参考来源** | — | 四值状态建模参考 Liu 2024（$s_t^{n,m} \in \{0,1,2,3\}$），但本文的 $\rho_t$ 由 BS 广播而非 VT 本地感知 |
| **审稿意见映射** | **R2-C5**（PU 模型简化）、**R3-C5**（状态冗余需分析） | 引用 Liu 2024 四值先例 + 明确 $\rho_t$ 与 $\delta_t/\theta_t$ 的正交性 |
| **改动量** | — | 状态公式扩展 + §III 新增一段 + Action Masking 规则（~10 行） |

---

## 6. 三层 PU 保护架构（新增系统级描述）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §IV-B（仅 reward 软惩罚） | §IV-B 末尾新增 "Three-Tier PU Protection Architecture" 段落 |
| **Layer 1 (Reward)** | $\Omega$ 加性惩罚 | Sigmoid 门控：合规→正奖励，超标→硬趋 $-\kappa$ |
| **Layer 2 (State)** | 无 | 状态注入 $\rho_t$ 和 $\hat{g}$，使 agent 在**决策时**预判合规性 |
| **Layer 3 (Action)** | 无 | $\rho_t^j \in \{2,3\}$ 时硬屏蔽 underlay 动作 |
| **各层互补逻辑** | — | Layer 3 防"明知不可为"（多用户冲突）；Layer 2 助"预判可不可为"（SU-PU 链路预判）；Layer 1 保"做错了要罚"（超标负反馈） |
| **审稿意见映射** | **R3-C6**（偏向 underlay）、**R1-C9**（缺违规率）、**R1-C4**（信息获取） | 三层协同，消融实验需验证每层独立降低违规率 |
| **改动量** | — | 新增~12 行段落 + 消融实验新增 Layer-1-only / Layer-1+2 / Full 三组 |

---

## 7. 仿真实验——新增指标与鲁棒性测试

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §V | §V 新增指标 + 鲁棒性实验 |
| **新增指标** | — | **PU Interference Violation Rate** = 超标次数 / 总 underlay 接入次数 |
| **鲁棒性实验 1** | — | 路径损耗估计误差 $\pm 3$ dB 下的违规率与吞吐量退化 |
| **鲁棒性实验 2** | — | 衰落裕量 $F \in \{1, 1.5, 2, 3\}$（对应 0, 1.8, 3, 4.8 dB）的违规率-吞吐量 trade-off 曲线 |
| **审稿意见映射** | **R1-C9**（违规率）、**R1-C10**（鲁棒性）、**R1-C4**（估计误差敏感性） | 直接以数据回应"您的方案在估计不准时还能工作吗" |
| **改动量** | — | 1 个新指标 + 2 组新实验（~1 页） |

---

## 8. 文本删除列表——防止诱导审稿人误读的表述

| 位置 | 原稿文本 | 处理方式 | 风险说明 |
|------|---------|:---:|------|
| §IV-B underlay reward 解释段 (~line 315) | *"as long as VT i completes access within this threshold, a positive reward is granted"* | **删除** | 审稿人读出："超标也可能给正奖励吧？"——与 R1-C3 和 R3-C6 的质疑直接对应 |
| §IV-B underlay reward 解释段 (~line 316–317) | *"the agent tends to prefer underlay mode because it yields a higher expected reward and more frequent positive feedback"* | **删除** | 这句话直接坐实了 R3-C6 的质疑——"你自己都说 agent 会偏向 underlay" |
| §I Contribution 2 (~line 55) | *"a novel ESN-DDQN network"* | 改为 *"an ESN-assisted DDQN implementation optimized for fast discrete channel-mode switching"* | 弱化 "novel algorithm" 表达，回应 R3-C1 和 R4-C1 |

---

## 9. 审稿意见覆盖矩阵

| 修改编号 | 涉及内容 | 回应审稿意见 | 改动类型 |
|:---:|------|------|:---:|
| 1 | Overlay 惩罚简化为固定惩罚 | **R1-C4** ($|h|^2$ 获取) | 公式替换 |
| 2 | Underlay reward → sigmoid 门控 | **R1-C3** (公式歧义), **R3-C6** (偏向 underlay) | 公式重写 + 解释文本 |
| 3 | Underlay 功率闭式约束 | **R1-C8** (功率控制) | 新增公式 |
| 4 | SU-PU 链路信息 BS 代理 | **R1-C4** (可行性) | 新增 §III 段落 |
| 5 | 状态空间扩展 (4 值 $\rho_t$) | **R2-C5** (PU 模型简化), **R3-C5** (状态冗余) | 公式扩展 + 段落 |
| 6 | 三层 PU 保护架构 | **R3-C6**, **R1-C9**, **R1-C4** | 新增段落 |
| 7 | 违规率 + 鲁棒性实验 | **R1-C9**, **R1-C10**, **R1-C4** | 新增实验 |
| 8 | 删除误导性文本 (3 处) | **R3-C6**, **R3-C1**, **R4-C1** | 文本删除/修改 |

---

> **生成日期**：2026-05-13（v2，基于用户反馈全面修正）
> **v1→v2 修正项**：
> (i) 原稿公式编号修正（原 v1 误标 "Eq.10" — 实际 `eq:state_space` 是状态空间公式）
> (ii) Overlay 惩罚修改中明确以 $\hat{g}$（路径损耗代理）替代 $|h|^2$ 的语义
> (iii) 新增 §0 关键事实核查：Liu 2024 同样未解决 SU-PU 信道增益获取问题
> (iv) Underlay reward 从乘法门控 $\mathbf{1}(\cdot)$ 改为 sigmoid 软门控 $\sigma(\cdot)$
> (v) 删除 v1 中关于 Liu 2024 "描述过信道增益获取方式"的错误表述
> **参考外部文献**：Liu et al. (2024), IEEE TITS — PU 功率离散化 + 四值状态空间 + 干扰阈值闭式导出 + 差值型 underlay 惩罚（结构参考，非信道获取方案来源）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §IV-B, Eq.(10) 子项3 (~line 290–304) | 同位置，公式替换 |
| **原稿描述** | `\Omega_t^{i,j} = \frac{\partial |h_t^{i,PU}|^2 P_t^{i,j}}{\Psi_T^{j,PU}}` — 依赖 SU-PU 瞬时信道增益 | `\Omega_t^{i,j} = \partial \cdot \mathbf{1}(\text{PU detected on channel } j)` — 固定惩罚，不依赖信道增益 |
| **设计逻辑** | 按"干扰功率 / 容忍阈值"比例惩罚 | 与 overlay 零干扰承诺一致——"无论干扰大小，触碰就罚" |
| **审稿意见映射** | **R1-C4**（$|h_t^{i,PU}|^2$ 如何获取？） | 彻底消除对 SU-PU 瞬时 CSI 的依赖 |
| **改动量** | — | 删除 `|h_t^{i,PU}|^2` 和 `\Psi_T^{j,PU}` 两项，改为示性函数 |

---

## 2. Underlay 模式的奖励公式（核心修改）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §IV-B, Eq.(12) (~line 312–335) | 同位置，公式替换 + 新增解释段落 |
| **原稿公式** | `r_t^{i,j} = \Phi_t^{'i,j} \cdot C_t^{i,j}/C_{\max} + \Omega_t^{i,j}`，其中 `\Omega_t^{i,j} = \partial(\Psi_t^{j,PU} - |h_t^{i,PU}|^2 P_t^{i,j})` | `r_t^{i,j} = \Phi_t^{'i,j} \cdot C_t^{i,j}/C_{\max} \cdot \mathbb{1}(\Psi > |h|^2P) - \kappa \cdot \mathbb{1}(\Psi \leq |h|^2P)` |
| **原稿关键文本** | _"the underlay mode uses compliance with the PU's power/interference tolerance threshold as the criterion for positive reward: as long as VT i completes access within this threshold, a positive reward is granted"_ (~line 316) | 删除"positive reward as long as within threshold"的表述，改为："合规时获得吞吐量奖励，超标时施加固定负惩罚，两者通过门控函数互斥" |
| **原稿关键文本 2** | _"After iterative training, when a candidate channel contains a PU, the agent tends to prefer underlay mode because it yields a higher expected reward and more frequent positive feedback"_ (~line 316–317) | **删除此段**。替换为："The multiplicative gating ensures that interference violation yields strictly negative reward, while the occupancy-type indicator $\rho_t$ enables the agent to anticipate infeasible underlay access before execution." |
| **设计逻辑变化** | Ω 为**加性项**——干扰合规时奖励 +Ω（正），干扰超标时理论上为负，但可被吞吐量项补偿 | 改为**乘法门控 + 显式负惩罚**——合规与超标互斥，超标恒为 $-\kappa$，不可被补偿 |
| **审稿意见映射** | **R3-C6**（即使存在干扰约束奖励仍可为正→偏向 underlay）、**R1-C3**（公式歧义/错误） | 超标信号与合规信号在数值上不再可混叠 |
| **改动量** | — | 公式重写 + 删除 2 句可能诱导审稿人误解的解释文本 + 新增 1 段防御性解释 |

---

## 3. Underlay 功率控制机制（原稿缺失）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | 无对应公式 | §IV-B 新增子段落，紧接 Eq.(12) 之后 |
| **原稿描述** | 仅暗示"transmit power below interference tolerance"，未给出功率选择方式 | `P_t^{i,j} = \min(P_{\max},\; \Psi_t^{j,PU} / \hat{g}_{\text{safe}})` |
| **新增解释** | — | (i) $P_{\max}$ = VT 硬件上限；(ii) $\hat{g}_{\text{safe}} = 1/PL(d) \times F$ 为含衰落裕量 $F$ 的路径损耗代理；(iii) 二者取 min 同时满足物理极限与 PU 保护 |
| **审稿意见映射** | **R1-C8**（功率如何选择？控制回路？） | 闭式约束，无需在线控制回路——每 $T_{\text{upd}}$ 由 BS 重算一次 |
| **改动量** | — | 新增公式 + 一段解释（~4-6 行） |

---

## 4. SU-PU 信道信息获取方式（原稿隐含假设，未明确定义）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §III（System Model）无对应描述；§IV-B 公式中直接使用 `|h_t^{i,PU}|^2` | §III 新增子段落 "SU-PU Link Information via BS Proxy"；§IV-B 以 $\hat{g}$ 替代 |
| **原稿描述** | 假设仿真中可以获取 `|h_t^{i,PU}|^2`，未讨论现实可行性 | (i) PU 功率离散化为有限档位（BS 长期监听 RSS → K-means 聚类，参考 Liu 2024 TITS）；(ii) VT 位置来自 V2X CAM 消息；(iii) BS 计算 $\hat{g} = 1/PL(d(\text{VT}_i, \text{PU}_j))$；(iv) 加入衰落裕量 $F$ 吸收小尺度衰落误差 |
| **审稿意见映射** | **R1-C4**（"How is `|h|^{2}` actually obtained in high-mobility CVN?"） | 明确声明不依赖瞬时 CSI，用路径损耗代理 + 裕量做保守估计 |
| **改动量** | — | §III 新增~6-8 行；§IV-B 将 `|h|^{2}` 替换为 `\hat{g}` |

---

## 5. 信道状态空间——从 2 值到 4 值（新增占用类型维度）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §IV-A, Eq.(7) (~line 247–252) | 同位置，公式扩展 + §III 新增 BS 广播机制解释 |
| **原稿描述** | `\mathbf{S_t} = \{\delta_t, \Phi_t, \theta_t\}` — 仅 3 分量 | `\mathbf{S_t} = \{\delta_t, \Phi_t, \theta_t, \mathbf{\rho_t}\}` — 新增 BS 广播的占用类型指示符 |
| **原稿中** $\delta_t$ **的取值** | 2 值（0=idle, 1=busy） | 不变（感知仍为 2 值），但新增 $\rho_t$ 提供 4 值细化（0=idle, 1=PU 独占, 2=SU 独占, 3=多用户冲突） |
| **预测模型** $\theta_t$ | 预测下一 slot 空闲概率（3 值训练：0/1/2） | **不变**——$\theta_t$ 的输入和输出语义均不改变，$\rho_t$ 是正交的当前观测维度 |
| **Action Masking** | 无 | 当 $\rho_t^j \in \{2,3\}$（SU 独占或多用户冲突）→ Underlay 动作被硬屏蔽 |
| **审稿意见映射** | **R2-C5**（PU 模型简化）、**R3-C5**（状态冗余需特征选择分析） | 引用 Liu 2024 四值状态建模先例；明确 $\rho_t$ 与 $\theta_t/\delta_t$ 的正交性 |
| **改动量** | — | 状态向量公式扩展 + §III 新增 BS 广播机制段落 + Action Masking 规则一段（~8 行） |

---

## 6. PU 保护架构——从软约束到三层防御（新增系统级描述）

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §IV-B（仅 reward 层面的惩罚） | §IV-B 末尾新增 "Three-Tier PU Protection Architecture" 段落 |
| **原稿描述** | 仅在 reward 中通过 $\Omega$ 项施加软惩罚 | **Layer 1** (Reward): 乘法门控 + 违规负惩罚 `−κ`；**Layer 2** (State): 状态向量中注入 $\rho_t$ 和 $\hat{g}$ 使 agent 预判合规性；**Layer 3** (Action): $\rho_t \in \{2,3\}$ 时 underlay 动作被硬屏蔽 |
| **审稿意见映射** | **R3-C6**（偏向 underlay）、**R1-C9**（PU 干扰违规率未报告）、**R1-C4**（信息获取） | 三层协同，每层独立降低违规率——消融实验验证各层独立贡献 |
| **改动量** | — | 新增~10-12 行 + 消融实验中新增 Layer-1-only / Layer-1+2 / Full 三组对比 |

---

## 7. 仿真实验——新增 PU 违规率指标与鲁棒性测试

| 维度 | 原稿 | 修订后 |
|------|------|--------|
| **位置** | §V（Performance Evaluation） | §V 新增指标 + 新增鲁棒性实验 |
| **原稿指标** | PLR, VT-TP, PU-TP, Avg-DQI, Conv-Speed（5 项） | 新增：**PU Interference Violation Rate** = 超标次数 / 总 underlay 接入次数 |
| **鲁棒性测试** | 无 | 新增：(i) 路径损耗估计误差 $\pm 3$ dB 下的违规率和吞吐量退化；(ii) 不同衰落裕量 $F \in \{1, 1.5, 2, 3\}$ 的违规率-吞吐量 trade-off |
| **审稿意见映射** | **R1-C9**（违规率未报告）、**R1-C10**（缺鲁棒性）、**R1-C4**（估计误差敏感性） | 违规率直接量化 PU 保护水平；估计误差实验回应可行性疑虑 |
| **改动量** | — | 新增 1 个指标 + 2 组鲁棒性实验（~1 页） |

---

## 8. 文本层面——删除可能诱导审稿人误解的表述

| 位置 | 原稿文本 | 修订后 | 原因 |
|------|---------|--------|------|
| §IV-B, ~line 316 | *"the agent tends to prefer underlay mode because it yields a higher expected reward and more frequent positive feedback"* | **删除** | 直接坐实了 R3-C6 的质疑——"你自己都说 agent 会偏向 underlay" |
| §IV-B, ~line 315 | *"as long as VT i completes access within this threshold, a positive reward is granted"* | 改为 "access within the threshold yields a throughput-proportional reward, while violation triggers a fixed negative penalty" | 原表述暗示"只要合规就给正奖励"——审稿人读出"超标也可能给正" |
| §I, ~line 55 (Contribution 2) | *"a novel ESN-DDQN network"* | 改为 "an ESN-assisted DDQN implementation optimized for fast discrete channel-mode switching" | R3-C1 和 R4-C1 质疑 ESN-RL 非全新——弱化"novel algorithm"表述 |
| §IV-B 标题 | *"Differentiated Reward Function"* | 不变（仍为 Differentiated Reward），但新增副标题强调 "with Interference-Aware Gating" | 让审稿人一眼看到 reward 的核心是"门控"而非"差异化" |

---

## 9. 修改汇总与审稿意见覆盖矩阵

| 修改编号 | 涉及内容 | 回应审稿意见 | 改动类型 |
|:--:|------|------|:--:|
| 1 | Overlay 惩罚简化为固定惩罚 | R1-C4 ($|h|^2$ 获取) | 公式替换 |
| 2 | Underlay reward 乘法门控 + 负惩罚 | R1-C3 (公式歧义), R3-C6 (偏向 underlay) | 公式重写 + 解释文本修改 |
| 3 | Underlay 功率闭式约束 | R1-C8 (功率控制机制) | 新增公式 |
| 4 | SU-PU 信道信息 BS 代理机制 | R1-C4 (可行性) | 新增段落 (§III) |
| 5 | 状态空间扩展 (4 值占用类型) | R2-C5 (PU 模型简化), R3-C5 (状态冗余) | 公式扩展 + 新增段落 |
| 6 | 三层 PU 保护架构 | R3-C6 (偏向), R1-C9 (违规率), R1-C4 | 新增段落 |
| 7 | 新增违规率指标 + 鲁棒性实验 | R1-C9, R1-C10, R1-C4 | 新增实验 |
| 8 | 删除/修改误导性表述 | R3-C6, R3-C1, R4-C1 | 文本修改 |

---

> 生成日期: 2026-05-13
> 基于对话: Underlay + Reward 技术正确性分析全程
> 参考外部文献: Liu et al. (2024), IEEE TITS — PU 功率离散化 + 四值状态空间 + 干扰阈值闭式导出
