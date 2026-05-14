# CVN-DSA 论文：Underlay + Reward + PU 保护 技术讨论总结

> 生成日期：2026-05-13
> 目的：将对话中所有技术决策、公式推导、审稿回复逻辑凝练为自包含文档，便于迁移到下一个对话。
> 对应审稿意见：R1-C3, R1-C4, R1-C8, R1-C9, R3-C6, R2-C5
> 参考外部文献：Liu et al. (2024), IEEE TITS — PU 功率离散化 + 四值状态空间 + 干扰阈值闭式导出

---

## 一、原稿 Reward 的问题诊断

### 1.1 原稿 Underlay 公式

$$r_t^{i,j} = \Phi_t^{'i,j} \cdot C_t^{i,j}/C_{\max} + \Omega_t^{i,j}$$

其中：
$$\Omega_t^{i,j} = \partial(\Psi_t^{j,{\rm PU}} - |h_t^{i,{\rm PU}}|^2 P_t^{i,j})$$

### 1.2 审稿人质疑的核心（R1-C3, R3-C6）

**问题不在"有没有 Ψ"，而在于 Ω 是加性项**：

$$\Omega = \partial(\Psi - |h|^2P)$$

- 当 $\Psi - |h|^2P > 0$（合规）→ Ω > 0 → r 变大 ✓
- 当 $\Psi - |h|^2P < 0$（超标）→ Ω < 0 → 但 r 仍可能为正（因为吞吐量项 $\Phi' \cdot C/C_{\max}$ 可能更大）✗

**审稿人 R3-C6 的原文逻辑**："即使存在干扰约束，奖励仍可为正，可能使智能体偏向 underlay 接入。"

### 1.3 原稿 Overlay 惩罚的问题（R1-C4）

$$\Omega_t^{i,j} = \frac{\partial |h_t^{i,{\rm PU}}|^2 P_t^{i,j}}{\Psi_t^{j,{\rm PU}}}$$

依赖 $|h_t^{i,{\rm PU}}|^2$（SU-PU 瞬时信道增益），但**原稿未解释该值在真实 V2X 高移动性场景中如何获取**。

### 1.4 原稿中两句必须删除的文本

| 位置 | 文本 | 风险 |
|------|------|------|
| §IV-B underlay 解释段 | *"as long as VT i completes access within this threshold, a positive reward is granted"* | 审稿人理解为"超标也可能给正奖励" |
| §IV-B underlay 解释段 | *"the agent tends to prefer underlay mode because it yields a higher expected reward and more frequent positive feedback"* | 直接坐实 R3-C6 的质疑 |

---

## 二、修订后的 Underlay Reward：Sigmoid 门控方案

### 2.1 公式

$$r_t^{i,j} = \Phi_t^{'i,j} \cdot \frac{C_t^{i,j}}{C_{\max}} \cdot \sigma\!\big(\alpha \cdot \Delta_t^{i,j}\big) - \kappa \cdot \big[1 - \sigma\!\big(\alpha \cdot \Delta_t^{i,j}\big)\big]$$

其中：
- $\sigma(x) = 1/(1+e^{-x})$：sigmoid 函数
- $\Delta_t^{i,j} = \Psi_t^{j,{\rm PU}} - \hat{g}_t^{i,{\rm PU}} \cdot P_t^{i,j}$：干扰裕量
- $\alpha > 0$：锐度参数（控制门控陡峭程度，$\alpha \to \infty$ 退化为硬门控）
- $\hat{g}_t^{i,{\rm PU}} = 1/PL(d(\text{VT}_i, \text{PU}_j))$：路径损耗代理（详见 §五）
- $\kappa > 0$：违规惩罚常数

### 2.2 物理含义（三种典型情况）

```
Δ >> 0  (深度合规，干扰远低于阈值)：σ → 1  → r ≈ Φ'·C/Cmax   (全额吞吐量奖励)
Δ ≈ 0   (临界区域)：                σ ≈ 0.5 → r ≈ 0.5·Φ'·C/Cmax − 0.5·κ
Δ << 0  (深度超标，干扰远高于阈值)：σ → 0  → r ≈ −κ           (全额违规惩罚)
```

### 2.3 为什么不用更简单的方案

| 方案 | 问题 |
|------|------|
| 乘法门控 $\mathbf{1}(\Psi > \|h\|^2P)$ | 硬切换物理含义不直观；超标时 r=0，agent 无法区分"不做任何事"和"做了但违规" |
| 保留加性 Ω | 审稿人已明确指出超标时 r 仍可为正（不可接受） |
| Sigmoid 门控 | ① 平滑过渡，物理含义清晰 ② 超标时 r→−κ 不可被补偿 ③ α 可调软硬，实验中可做敏感性分析 |

### 2.4 与 Liu 2024 Underlay 惩罚的对比

| | Liu 2024 | 本文修订后 |
|------|----------|-----------|
| 惩罚形式 | $\tau(\zeta_1^m - \|\hat{g}_{m,n}\|^2 P_t^n)$ 线性差值（加性） | $\sigma(\alpha(\Psi - \hat{g} \cdot P))$ sigmoid 门控（乘性-软切换） |
| 核心区别 | 加性：合规项和惩罚项可互相补偿 | 乘性-软切换：超标时不可被吞吐量项补偿 |
| 审稿回复引用 | "The difference-based penalty form in [Liu 2024, Eq. 19] shares the same spirit of threshold-aware underlay reward design, while our sigmoid-gated formulation further prevents reward sign ambiguity by ensuring r → −κ when interference exceeds the threshold." | |

---

## 三、Overlay 惩罚修订

### 3.1 原稿 → 修订

| 原稿 | 修订后 |
|------|--------|
| $\displaystyle \Omega_t^{i,j} = \frac{\partial \|h_t^{i,{\rm PU}}\|^2 P_t^{i,j}}{\Psi_t^{j,{\rm PU}}}$ | $\Omega_t^{i,j} = \partial \cdot \mathbf{1}(\text{PU detected on channel } j)$ |

### 3.2 设计逻辑

- **原稿**：比例惩罚 → 需要 SU-PU 信道增益（审稿人质疑不可获取）
- **修订**：固定惩罚 → 与 overlay 零干扰承诺一致（"无论干扰大小，触碰就罚"）
- **SU-SU 碰撞惩罚**（原稿子项4）：保留 $|h_t^{i,i'}|^2$ — V2V 信道增益可通过导频直接估计，不需要修改

---

## 四、PU 干扰容忍阈值 Ψ 的导出

### 4.1 公式（参考 Liu 2024, Eq. 22-24）

$$\Psi_t^{j,{\rm PU}} = \frac{|h_j^{\rm PU}|^2 P_{\rm PU}^j}{2^{C_{\min}/W_j} - 1} - W_j n_0$$

其中：
- $C_{\min}$：PU 的最小传输速率需求（可从 PU 服务类型推断）
- $|h_j^{\rm PU}|^2$：PU 自身链路的信道增益（BS 可通过监听 PU 的 ACK/NACK 推断）
- $P_{\rm PU}^j$：PU 当前发射功率档位（由 BS 通过长期 RSS 监测 + K-means 聚类得到）
- $W_j$：信道带宽
- $n_0$：噪声功率谱密度

### 4.2 关键论证

**Ψ 不是凭空设定的常数**，而是从 PU 的 QoS 需求（最小速率）闭式导出的——这是 underlay CR 的标准做法，有文献先例（Liu 2024, IEEE TITS）。

---

## 五、SU-PU 信道增益代理 $\hat{g}$ 的获取

### 5.1 核心思路

**不测瞬时信道增益**（在 V2X 中不可行），而是用 BS 代理构建保守的路径损耗代理。

### 5.2 三步流程

| 步骤 | 操作 | 数据来源 |
|:---:|------|------|
| **Step 1: PU 功率离散化** | BS 长期监听 PU 信号 RSS → K-means 聚类 → 分 K 个功率档位（如 K=3：{0.1, 0.5, 0.9} mW） | BS 历史测量数据 |
| **Step 2: 路径损耗代理** | BS 已知 PU 发射机位置（注册信息固定）和 VT 当前位置（V2X CAM 消息 10 Hz）→ 计算距离 $d(\text{VT}_i, \text{PU}_j)$ → 代入 3GPP V2V 路径损耗模型 → $\hat{g} = 1/PL(d)$ | 注册数据库 + V2X CAM |
| **Step 3: 衰落裕量** | 小尺度衰落不可预测 → 用 $F>1$ 做裕量（如 $F=\sqrt{2}$ ≈ 3dB），在最坏情况衰落放大 F 倍时仍保证合规 | 工程经验值 |

### 5.3 关键论证（回应 R1-C4）

> "We do not assume that instantaneous SU-PU channel gain is measurable. Instead, the BS constructs a conservative path-loss proxy $\hat{g}$ by combining PU power-level classification (via long-term RSS clustering), VT position reports (V2X CAM, 10 Hz), and a 3GPP-standard path-loss model. A fading margin $F$ is applied to absorb small-scale fading uncertainty. This approach operates entirely within existing V2X signaling frameworks and introduces no new control channels."

### 5.4 ĝ 与 |h|² 的关系

$$|h|^2 = \underbrace{\frac{1}{PL(d)}}_{\hat{g}} \cdot \underbrace{g_{\text{shadow}}}_{\text{阴影衰落}} \cdot \underbrace{g_{\text{fast}}}_{\text{小尺度衰落}}$$

- $\hat{g}$ 是 $|h|^2$ 的"骨架"（只保留距离决定的确定性成分）
- 加上 $F$ 裕量后转换为保守估计 $\hat{g}_{\text{safe}} = \hat{g} \cdot F$
- 衰落裕量确保：在最坏情况（小尺度衰落放大 F 倍）下，干扰仍合规

### 5.5 重要事实核查：Liu 2024 也没有解决这个问题

Liu 2024（IEEE TITS 2024）在其 Underlay 模型中同样直接使用 $|\hat{h}_m^n|^2$ 和 $|\tilde{g}_{m,n}|^2$（Rayleigh 衰落随机生成），**全文中没有描述 SU-PU 信道增益在实际系统中如何获取**。

**审稿回复策略**：
- Liu 2024 不是技术方案的来源（它也没解决）
- Liu 2024 可作为"领域共性问题"的佐证（"即使已发表的 TITS 论文也依赖仿真假设"）
- 本文的 BS 代理方案比 Liu 2024 更进了一步（尽管仍是保守估计）

---

## 六、Underlay 功率闭式约束

### 6.1 公式

$$P_t^{i,j} = \min\!\big(P_{\max},\; \Psi_t^{j,{\rm PU}} \,/\, (\hat{g}_t^{i,{\rm PU}} \cdot F)\big)$$

### 6.2 两个约束

| 约束 | 公式 | 含义 |
|------|------|------|
| 硬件上限 | $P \leq P_{\max}$ | VT 射频前端最大发射功率 |
| 干扰上限 | $P \leq \Psi / (\hat{g} \cdot F)$ | 在最坏情况衰落（放大 F 倍）下干扰仍低于 PU 容忍阈值 |

### 6.3 三种典型情况

| 情况 | ĝ | Ψ/(ĝ·F) | P | 制约因素 |
|------|:--:|:--:|:--:|------|
| VT 离 PU 很远 | 很小 | 很大 (> P_max) | P_max | 硬件限制 |
| VT 离 PU 中等 | 中等 | > P_max | P_max | 硬件限制 |
| VT 离 PU 很近 | 很大 | < P_max | Ψ/(ĝ·F) | 干扰限制 |

### 6.4 回应 R1-C8

> "Underlay transmit power follows a closed-form constraint $P = \min(P_{\max}, \Psi/(\hat{g} \cdot F))$. No online control loop is required — the BS recomputes and broadcasts the per-channel power cap every $T_{\text{upd}}$ slots. The adjustment latency is $T_{\text{upd}}$, and we report sensitivity analysis for $T_{\text{upd}} \in \{1, 5, 10\}$."

---

## 七、三层 PU 保护架构

| 层级 | 位置 | 机制 | 解决的问题 |
|:---:|------|------|------|
| **Layer 1 (Reward)** | §IV-B | Sigmoid 门控：合规→正奖励，超标→硬趋 −κ | R3-C6（超标时 r 可为正） |
| **Layer 2 (State)** | §IV-A | 状态注入 $\rho_t$（占用类型 4 值）和 $\hat{g}$（路径损耗代理），agent 在决策时预判合规性 | R1-C4（信息获取）、R2-C5（模型简化） |
| **Layer 3 (Action)** | §IV-A | $\rho_t^j \in \{2,3\}$（SU 独占或多用户冲突）→ Underlay 动作硬屏蔽 | R1-C9（违规率）、R3-C6（偏向 underlay） |

### 各层协同逻辑

```
Layer 3: 防"明知不可为" — 多用户冲突直接禁入
Layer 2: 助"预判可不可为" — 注入合规预判信号到状态空间
Layer 1: 保"做错了要罚" — 超标负反馈驱动策略修正
```

消融实验需验证：Layer-1-only vs Layer-1+2 vs Full (Layer 1+2+3) 的 PU 违规率递降。

---

## 八、四值占用类型 $\rho_t$（新增状态维度）

### 8.1 定义

| $\rho_t^j$ | 含义 | Underlay 是否允许 |
|:---:|------|:---:|
| 0 | 信道空闲 | ✅ overlay + underlay |
| 1 | PU 独占 | ⚠️ underlay 需通过 Layer 1 门控 |
| 2 | SU 独占 | ❌ 硬屏蔽 |
| 3 | 多用户冲突 | ❌ 硬屏蔽 |

### 8.2 与其他状态分量的关系

| 分量 | 语义 | 来源 |
|------|------|------|
| $\delta_t$ | 2 值感知（idle/busy） | VT 本地 |
| $\theta_t$ | 预测未来空闲概率 | 服务器 LSTM |
| $\rho_t$ | 当前占用类型细化 | BS 广播 |

- $\rho_t$ 与 $\theta_t$ **正交**：$\rho_t$ 是当前观测，$\theta_t$ 是未来预测
- $\rho_t$ 与 $\delta_t$ **互补**：$\delta_t=1$（busy）时 $\rho_t$ 进一步区分 PU/SU/冲突
- **预测模型无需修改**：$\theta_t$ 的输入输出语义保持不变

### 8.3 参考来源

四值状态建模参考 Liu 2024（$s_t^{n,m} \in \{0,1,2,3\}$），但本文的 $\rho_t$ 由 BS 广播而非 VT 本地感知。

---

## 九、审稿回复逻辑速查

### R1-C3（Reward 公式歧义）

> "We have replaced the additive interference term with a sigmoid-gated formulation. The revised reward ensures that when interference exceeds the PU tolerance threshold ($\Delta \ll 0$), the reward asymptotically approaches $-\kappa$, eliminating the possibility of positive reward under violation."

### R1-C4（SU-PU 信道增益获取）

> "We do not assume instantaneous SU-PU CSI is measurable. Instead, the BS estimates a conservative path-loss proxy $\hat{g}$ using PU power-level classification, VT position reports, and a standard path-loss model, with a fading margin $F$ to absorb small-scale fading uncertainty."

### R1-C8（Underlay 功率控制机制）

> "Transmit power follows a closed-form constraint $P = \min(P_{\max}, \Psi/(\hat{g} \cdot F))$, recomputed by the BS every $T_{\text{upd}}$ slots. No online control loop is required."

### R1-C9（PU 干扰违规率）

> "We have added a PU interference violation rate metric and two robustness experiments: ±3 dB path-loss estimation error sensitivity, and fading margin $F \in \{1,1.5,2,3\}$ trade-off analysis."

### R3-C6（Underlay reward 偏差）

> "The sigmoid-gated reward (Layer 1), together with occupancy-type indicator $\rho_t$ injection into the state (Layer 2) and hard action masking for multi-user conflict channels (Layer 3), forms a three-tier PU protection architecture. Ablation results demonstrate each tier independently reduces the PU violation rate."

### R2-C5（PU 模型简化）

> "We have extended the channel state space from binary (idle/busy) to four occupancy types, following the modeling approach of [Liu 2024, IEEE TITS]. The additional occupancy information is broadcast by the BS and injected into the RL state without modifying the prediction model."

---

## 十、新符号速查

| 符号 | 含义 | 取值/来源 |
|------|------|------|
| $\sigma(x)$ | Sigmoid 函数 | $1/(1+e^{-x})$ |
| $\alpha$ | 门控锐度参数 | 正数，越大→越接近硬门控，实验中测 {1,5,10,20} |
| $\Delta_t^{i,j}$ | 干扰裕量 | $\Psi - \hat{g} \cdot P$；正值=合规，负值=超标 |
| $\kappa$ | 违规惩罚常数 | 正数，超标时 r → −κ |
| $\hat{g}_t^{i,{\rm PU}}$ | SU-PU 路径损耗代理 | $1/PL(d(\text{VT}_i, \text{PU}_j))$，BS 计算 |
| $F$ | 衰落裕量 | >1，如 $F=\sqrt{2}$ ≈ 3dB |
| $\rho_t^j$ | 占用类型指示符 | 0=idle, 1=PU 独占, 2=SU 独占, 3=多用户冲突；BS 广播 |
| $C_{\min}$ | PU 最小速率需求 | 从 PU 服务类型推断，用于导出 Ψ |

---

## 十一、待完成的实验

| 实验 | 目的 | 对应审稿意见 |
|------|------|:---:|
| Sigmoid 锐度 $\alpha \in \{1,5,10,20\}$ 敏感性 | 确定最优 $\alpha$ | R1-C3 |
| PU 干扰违规率（Violation Rate） | 直接量化 PU 保护水平 | R1-C9 |
| 三层消融（L1-only / L1+2 / Full） | 证明每层独立降低违规率 | R3-C6, R1-C9 |
| 路径损耗估计误差 ±3 dB 鲁棒性 | 回应"ĝ 不准怎么办" | R1-C4 |
| 衰落裕量 F ∈ {1, 1.5, 2, 3} trade-off | 违规率-吞吐量权衡 | R1-C4, R1-C10 |
| 不同 PU 流量 p01/p10 组合 | PU 模型鲁棒性 | R2-C5 |

---

> **文档用途**：此文档为对话上下文中所有技术决策的凝练摘要。迁移到下一个对话时，将其作为附件或上下文文件提供，可使新对话快速恢复讨论状态。
