# 仿真信道模型 ↔ 论文公式 符号对照与最终公式集

> 基于仿真代码 `ChannelModel` 的物理分解，转化为论文 `main.tex` 中可直接使用的数学表述。
> 所有公式采用 KaTeX 渲染，在 VS Code Markdown 预览中可见。

---

## 一、信道增益的物理分解（§III System Model）

### 1.1 VT→BS 信道增益

$$|h_t^{i,j}|^2 = |\tilde{h}_t^{i,j}|^2 \cdot 10^{-(PL_t^{j} + g_t^{j})/10}$$

| 符号 | 含义 | 仿真对应 |
|------|------|----------|
| $|\tilde{h}_t^{i,j}|^2$ | Rician 小尺度衰落分量 | `h_sq_fading` |
| $PL_t^{j}$ | 距离依赖的路径损耗 (dB)，3GPP UMi-Street Canyon, $f_c=5.9$ GHz | `PL` |
| $g_t^{j}$ | 对数正态阴影衰落 (dB)，$\sim \mathcal{N}(0, \sigma_g^2)$, $\sigma_g=4$ dB | `shadow` |

### 1.2 Rician 小尺度衰落的定义

$$|\tilde{h}_t^{i,j}|^2 = \left| \sqrt{\frac{K}{K+1}} \cdot h_{\rm LOS} + \sqrt{\frac{1}{K+1}} \cdot h_{\rm NLOS} \right|^2$$

其中 $h_{\rm LOS}=1$（归一化直射分量），$h_{\rm NLOS} \sim \mathcal{CN}(0,1)$（复高斯散射分量），$K$ 为 Rician K 因子（线性，$K_{\rm dB}=3$ dB）。

### 1.3 VT→PU 信道增益（仅仿真 ground truth，agent 不可获取）

$$|h_t^{i,{\rm PU}}|^2 = |\tilde{h}_t^{i,{\rm PU}}|^2 \cdot 10^{-(PL_t^{{\rm PU},j} + g_t^{{\rm PU},j})/10}$$

> ⚠️ **关键声明**：$|h_t^{i,{\rm PU}}|^2$ 在仿真中由 `compute_channel_gains(vt_idx, is_pu=True)` 生成，**仅用于计算 ground truth 评估指标**（如真实干扰违规率）。Agent 在训练和推理阶段**不获取**该值。

---

## 二、SNR 与 RSS 的定义（§III，修订）

### 2.1 SNR（VT→BS 链路，导频可估计）

$$\gamma_t^{i,j} = \frac{P_t^{i,j} \cdot |h_t^{i,j}|^2}{\mu_t}$$

其中 $P_t^{i,j}$ 为 VT $i$ 在信道 $j$ 上的发射功率，$\mu_t$ 为噪声功率。

### 2.2 RSS（VT→BS 链路，接收功率 dBm）

$$\xi_t^{i,j} = P_t^{i,j} - PL_t^{j} + g_t^{j} \quad \text{(dBm)}$$

---

## 三、吞吐量公式（§IV-B，修订）

### 3.1 Overlay — idle 信道（不需改）

$$C_t^{i,j} = B_t^{i,j} \log_2\!\left(1 + \frac{|h_t^{i,j}|^2 P_t^{i,j}}{\mu_t}\right)$$

$\Omega_t^{i,j} = 0$

### 3.2 Overlay — PU 占用信道（修订后）

$$C_t^{i,j} = 0$$

$$\Omega_t^{i,j} = \partial \cdot \mathbf{1}(\text{PU detected on channel } j)$$

> 固定惩罚，不依赖任何信道增益。与 overlay 零干扰承诺一致——"无论干扰大小，触碰就罚"。

### 3.3 Underlay — idle 信道（不变）

$$C_t^{i,j} = B_t^{i,j} \log_2\!\left(1 + \frac{|h_t^{i,j}|^2 P_t^{i,j}}{\mu_t}\right)$$

### 3.4 Underlay — PU 占用信道（修订后）

**SINR 分母用感知时隙测量的总干扰 $I_{\rm sensed}^{\,j}$**：

$$C_t^{i,j} = B_t^{i,j} \log_2\!\left(1 + \frac{|h_t^{i,j}|^2 P_t^{i,j}}{\mu_t + I_{\rm sensed}^{\,j}}\right)$$

其中 $I_{\rm sensed}^{\,j}$ 为 VT 在感知子时隙信道 $j$ 上测到的总接收功率（PU 信号 + 噪声，线性值 W）。

---

## 四、干扰裕量与 Sigmoid 门控奖励（§IV-B，修订）

### 4.1 干扰裕量 $\Delta_t^{i,j}$

$$\Delta_t^{i,j} = \Psi_t^{j,{\rm PU}} - \hat{g}_t^{i,{\rm PU}} \cdot F \cdot P_t^{i,j}$$

| 符号 | 含义 | 来源 |
|------|------|------|
| $\Psi_t^{j,{\rm PU}}$ | PU 干扰容忍阈值 (W) | BS 从 PU QoS 闭式导出 |
| $\hat{g}_t^{i,{\rm PU}}$ | VT→PU 路径损耗代理 $= 1/PL(d_{ij})$ | BS 计算并广播 |
| $F$ | 衰落裕量，乘性安全系数 $F=\sqrt{2}\approx 1.414$ ($\approx 3$ dB) | 工程参数，Rician $K=3$ dB |
| $P_t^{i,j}$ | VT 实际发射功率 | $\min(P_{\max}, \Psi/(\hat{g}\cdot F))$ |

### 4.2 Sigmoid 门控奖励

$$r_t^{i,j} = \Phi_t^{'i,j} \cdot \frac{C_t^{i,j}}{C_{\max}} \cdot \sigma(\alpha \Delta_t^{i,j}) \;-\; \kappa \big[1 - \sigma(\alpha \Delta_t^{i,j})\big]$$

其中 $\sigma(x) = \dfrac{1}{1 + e^{-x}}$ 为 sigmoid 函数。

### 4.3 门控的物理行为

| 干扰状态 | $\Delta_t^{i,j}$ | $\sigma(\alpha\Delta)$ | $r_t^{i,j}$ |
|----------|:---:|:---:|------|
| 深度合规（干扰远低于阈值） | $\gg 0$ | $\to 1$ | $\approx \Phi' \cdot C/C_{\max}$（全额吞吐量奖励） |
| 临界区域 | $\approx 0$ | $\approx 0.5$ | $\approx 0.5\Phi' \cdot C/C_{\max} - 0.5\kappa$ |
| 深度超标（干扰远高于阈值） | $\ll 0$ | $\to 0$ | $\approx -\kappa$（全额违规惩罚） |

| 参数 | 含义 | 建议取值 |
|------|------|:---:|
| $\alpha$ | 门控锐度（越大越趋近硬门控） | 实验中测 $\{1,5,10,20\}$ |
| $\kappa$ | 违规惩罚常数（超标时 $r \to -\kappa$） | 正数，实验中调优 |

---

## 五、功率闭式约束（§IV-B，新增）

$$P_t^{i,j} = \min\!\left(P_{\max},\; \frac{\Psi_t^{j,{\rm PU}}}{\hat{g}_t^{i,{\rm PU}} \cdot F}\right)$$

| 约束 | 含义 |
|------|------|
| $P_{\max}$ | VT 射频前端硬件最大发射功率（物理极限） |
| $\Psi_t^{j,{\rm PU}} / (\hat{g}_t^{i,{\rm PU}} \cdot F)$ | 在最坏情况衰落（放大 $F$ 倍）下仍不超 PU 容忍阈值的最大功率 |

---

## 六、PU 干扰容忍阈值导出（§III 新增）

$$\Psi_t^{j,{\rm PU}} = \frac{|h_j^{\rm PU}|^2 \cdot P_{\rm PU}^j}{2^{C_{\min}/W_j} - 1} - W_j n_0$$

| 符号 | 含义 | 来源 |
|------|------|------|
| $C_{\min}$ | PU 最小传输速率需求 (bps) | PU 服务类型推断 |
| $|h_j^{\rm PU}|^2$ | PU 自身链路信道增益 | BS 监听 ACK/NACK 推断 |
| $P_{\rm PU}^j$ | PU 当前发射功率档位 | BS RSS 聚类 → 离散分类 |
| $W_j$ | 信道带宽 | BS 已知 |
| $n_0$ | 噪声功率谱密度 | 物理常数 |

---

## 七、路径损耗代理 $\hat{g}$ 与信息防火墙

### 7.1 代理定义

$$\hat{g}_t^{i,{\rm PU}} = \frac{1}{PL(d_{ij})}, \quad d_{ij} = \|\text{VT}_i - \text{PU发射机}_j\|_2$$

其中 $PL(\cdot)$ 为 3GPP UMi-Street Canyon 路径损耗模型（$f_c=5.9$ GHz）：

$$PL(d) = 20\log_{10}\!\left(\frac{4\pi f_c d}{c}\right) + 10\log_{10}\!\left(\frac{d}{10}\right) \quad \text{(dB)}$$

### 7.2 $\hat{g}$ 与真实 $|h|^2$ 的关系

$$|h_t^{i,{\rm PU}}|^2 = \underbrace{\hat{g}_t^{i,{\rm PU}}}_{\text{路径损耗代理}} \cdot \underbrace{10^{-g_t^{{\rm PU},j}/10}}_{\text{阴影衰落}} \cdot \underbrace{|\tilde{h}_t^{i,{\rm PU}}|^2}_{\text{Rician 小尺度}}$$

### 7.3 信息防火墙：Agent 可用 vs. Ground Truth

| 量 | Agent 可用（可部署） | 仅用于 Ground Truth 评估 |
|------|------|------|
| VT→BS 信道增益 | $|h_t^{i,j}|^2$（导频估计） | 真实 Rician + PL + shadow |
| SINR 分母干扰 | $I_{\rm sensed}^{\,j}$（感知时隙测量） | $|h_t^{i,{\rm PU}}|^2 P_{\rm PU}^j$ |
| VT→PU 信道 | $\hat{g}_t^{i,{\rm PU}}$（BS 路径损耗代理，+ 裕量 $F$） | $|h_t^{i,{\rm PU}}|^2$（用于 violation rate 统计） |
| PU 容忍阈值 | $\Psi_t^{j,{\rm PU}}$（BS 闭式导出） | 同 agent 可用 |
| PU 发射功率 | $P_{\rm PU}^j$（BS 离散分类） | 真实 $P_{\rm PU}^j$ |

---

## 八、完整 Underlay Reward（一张公式汇总）

$$r_t^{i,j} = \underbrace{\Phi_t^{'i,j}}_{\text{DQI}} \cdot \underbrace{\frac{C_t^{i,j}}{C_{\max}}}_{\text{归一化吞吐量}} \cdot \underbrace{\sigma\!\big(\alpha\,(\Psi_t^{j,{\rm PU}} - \hat{g}_t^{i,{\rm PU}} \cdot F \cdot P_t^{i,j})\big)}_{\text{sigmoid 门控：合规→1, 超标→0}} \;-\; \underbrace{\kappa\big[1 - \sigma(\cdot)\big]}_{\text{违规惩罚}}$$

其中：

$$
\begin{aligned}
C_t^{i,j} &= B_t^{i,j} \log_2\!\left(1 + \frac{|h_t^{i,j}|^2 P_t^{i,j}}{\mu_t + I_{\rm sensed}^{\,j}}\right) \\[4pt]
P_t^{i,j} &= \min\!\left(P_{\max},\; \frac{\Psi_t^{j,{\rm PU}}}{\hat{g}_t^{i,{\rm PU}} \cdot F}\right) \\[4pt]
\sigma(x) &= \frac{1}{1 + e^{-x}}
\end{aligned}
$$

---

## 九、新旧公式对照速查

| 位置 | 原稿 | 修订后 |
|------|------|--------|
| Overlay 碰撞惩罚 | $\displaystyle \Omega = \frac{\partial |h_t^{i,{\rm PU}}|^2 P_t^{i,j}}{\Psi_t^{j,{\rm PU}}}$ | $\Omega = \partial \cdot \mathbf{1}(\text{PU detected})$ |
| Underlay SINR 分母 | $\mu_t + |h_t^{i,{\rm PU}}|^2 P_t^{{\rm MAX},j}$ | $\mu_t + I_{\rm sensed}^{\,j}$ |
| Underlay 干扰项 Ω | $\partial(\Psi_t^{j,{\rm PU}} - |h_t^{i,{\rm PU}}|^2 P_t^{i,j})$ | 移入 sigmoid 门控 $\Delta_t^{i,j}$ |
| 功率选择 | 无闭式约束 | $P = \min(P_{\max}, \Psi/(\hat{g} \cdot F))$ |
| Agent 获知 $|h_t^{i,{\rm PU}}|^2$ | ✅ 获知（Oracle 仿真） | ❌ 不获知（仅用于 GT 评估） |

---

> **文档用途**：此文档中所有公式均可直接粘贴到 `main.tex` 中。渲染效果等同于论文最终 PDF。
> 符号命名与当前 `main.tex` 的 Notation Table (`\label{tab:notations}`) 一致，新增符号需同步追加到 Notation Table。
