# 论文到代码迁移指南：CVN 质量感知自适应频谱接入框架

> 目标：在新 VS Code 工作区中独立搭建仿真实验，产出可信、可复现、可开源的研究代码。
> 对应论文：`main.tex` (VT-2026-02444)
> 日期：2026-05-08

---

## 目录

1. [系统架构全景图](#1-系统架构全景图)
2. [仿真环境设计](#2-仿真环境设计)
3. [代码模块化拆解](#3-代码模块化拆解)
4. [推荐技术栈](#4-推荐技术栈)
5. [实验矩阵设计](#5-实验矩阵设计)
6. [开源项目结构建议](#6-开源项目结构建议)
7. [里程碑与工作量估算](#7-里程碑与工作量估算)

---

## 1. 系统架构全景图

先帮你把论文的整个 pipeline 画成一张可编码的架构图：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CENTRALIZED SERVER (MEC/RSU)                  │
│                                                                      │
│  ┌──────────────────────────┐    ┌──────────────────────────────┐   │
│  │  Module 1: DQI Evaluator │    │  Module 2: Channel Predictor │   │
│  │  (Transformer Encoder)   │    │  (Attention-LSTM)            │   │
│  │                          │    │                              │   │
│  │  Input: X_t^j [γ,ξ,B]   │    │  Input: Y_{t-T:t-1}          │   │
│  │  Output: Φ'_t^j (0~1)   │    │  Output: θ_t^j (0~1)         │   │
│  │  Update: every T_upd     │    │  Update: every T_upd         │   │
│  └────────────┬─────────────┘    └────────────┬─────────────────┘   │
│               │                               │                     │
│               └───────────┬───────────────────┘                     │
│                           │                                         │
│                    Broadcast Summary                                 │
│              {Φ'_t^j, θ_t^j} for j=1..M                             │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ (wireless broadcast, periodic)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      VEHICULAR TERMINAL (VT i)                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  State Constructor                                            │   │
│  │  S_t^i = {δ_t^i (sensing), Φ'_t (DQI), θ_t (prediction)}     │   │
│  └──────────────────────────────┬───────────────────────────────┘   │
│                                 │                                    │
│                                 ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Module 3: ESN-DDQN Agent                                     │   │
│  │                                                                │   │
│  │  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐    │   │
│  │  │   ESN    │───▶│  Eval Q-Net  │───▶│  Action Select   │    │   │
│  │  │ Reservoir│    │  (DDQN)      │    │  a_t^i = {ch, mode}│   │   │
│  │  └──────────┘    └──────────────┘    └────────┬─────────┘    │   │
│  │                                                │              │   │
│  │  Experience Replay Buffer ◀────────────────────┘              │   │
│  │  (S_t, a_t, r_{t+1}, S_{t+1})                                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Action: a_t^i = {channel_index, overlay/underlay}                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 数据流时间线

```
Slot t:
  1. Server 广播 DQI Φ'_t 和预测 θ_t（如果 T_upd 到期）
  2. VT 本地感知 → δ_t^i
  3. VT 构造 state S_t^i = {δ_t^i, Φ'_t, θ_t}
  4. VT 用 ESN-DDQN 选 action a_t^i
  5. VT 执行接入，传输数据
  6. VT 观察结果 → reward r_{t+1}^i, next_state S_{t+1}^i
  7. (S_t, a_t, r_{t+1}, S_{t+1}) → replay buffer
  8. 从 buffer 采样训练 ESN-DDQN
```

---

## 2. 仿真环境设计

### 2.1 环境参数（需要比原论文丰富 10 倍）

#### 拓扑与移动性

| 参数 | 原论文值 | 建议新值 | 说明 |
|------|---------|---------|------|
| 区域大小 | 未说明 | 500m × 500m | 城市街区尺度 |
| VT 数量 N | 3, 5 | 5, 10, 15, 20, 30 | 多组配置 |
| 信道数 M | 3, 5 | 5, 10, 15, 20, 30 | 多组配置 |
| VT 速度 | 未说明 | 30-80 km/h (城市), 80-120 km/h (高速) | 两类场景 |
| 移动模型 | 未说明 | Gauss-Markov Mobility Model | 比 Random Waypoint 更真实 |
| BS/RSU 位置 | 未说明 | 区域中心 1 个 BS, 四角各 1 个 RSU | 实际部署参考 |

#### 信道模型

| 参数 | 建议值 | 说明 |
|------|--------|------|
| 路径损耗模型 | 3GPP TR 38.901 UMi-Street Canyon | 标准模型 |
| 载波频率 | 5.9 GHz (V2X 频段) | 或 2.4/3.5 GHz |
| 小尺度衰落 | Rayleigh (NLOS) / Rician K=3dB (LOS) | 根据 VT-BS 距离切换 |
| 阴影衰落 | Log-normal, σ=4 dB (LOS), σ=8 dB (NLOS) | |
| 噪声功率谱密度 μ₀ | -174 dBm/Hz | |
| 每信道带宽 B | 200 kHz (窄带) / 10 MHz (宽带) | 两档 |
| VT 最大发射功率 | 23 dBm (200 mW) | 比原论文的 1mW 更实际 |

#### PU 活动模型

| 参数 | 原论文值 | 建议新值 | 说明 |
|------|---------|---------|------|
| 模型 | 两状态 Markov | 两状态 Markov + 周期占用 + 突发占用 | 多种 PU 模式 |
| p01 (idle→busy) | 0.2 | 0.1, 0.2, 0.3, 0.5 | 多组测试 |
| p10 (busy→idle) | 0.2 | 0.1, 0.2, 0.3, 0.5 | 多组测试 |
| PU 发射功率 | 未说明 | 30 dBm (1W) | |
| PU 干扰容限 Ψ | 未说明 | -90 dBm ~ -100 dBm | |

#### 频谱感知模型

| 参数 | 建议值 |
|------|--------|
| 检测概率 Pd | 0.9, 0.95 |
| 虚警概率 Pfa | 0.05, 0.1 |
| 感知延迟 | 1 slot |

#### 流量模型

| 参数 | 建议值 |
|------|--------|
| 包到达模型 | Bernoulli，速率 pa = 0.3, 0.5, 0.7 |
| 包大小 | 500 bytes (safety) / 1500 bytes (non-safety) |
| 队列容量 | 10, 20 packets |
| Slot 时长 Δt | 1 ms (URLLC-like) / 10 ms (eMBB-like) |

### 2.2 环境状态空间完整定义

```python
# 每个 slot t，每台 VT i 能获取的信息：

# 1. 本地感知结果（VT 自己执行）
sensing_outcome = {
    "delta": [0, 1, 0, 1, 0],  # M 个信道: 0=idle, 1=busy, 带有 Pd/Pfa 误差
}

# 2. 服务器下发的 DQI（每 T_upd slot 更新一次）
dqi_broadcast = {
    "Phi_prime": [0.72, 0.35, 0.88, 0.15, 0.61],  # M 个值, 0~1
    "staleness": 3,  # 距上次更新的 slot 数
}

# 3. 服务器下发的预测概率（每 T_upd slot 更新一次）
prediction_broadcast = {
    "theta": [0.80, 0.10, 0.65, 0.30, 0.55],  # M 个值, 0~1 (idle prob)
    "staleness": 3,
}

# 4. 组合成 DDQN 的 state vector
# shape: (M * 3,) 即每信道 3 个特征
state = {
    "delta": [0, 1, 0, 1, 0],
    "Phi_prime": [0.72, 0.35, 0.88, 0.15, 0.61],
    "theta": [0.80, 0.10, 0.65, 0.30, 0.55],
}
```

### 2.3 动作空间

```python
# 动作是一个元组 (channel_index, access_mode)
# channel_index ∈ {0, 1, ..., M}  其中 0 = 不接入
# access_mode  ∈ {0, 1}          其中 0 = overlay, 1 = underlay

# 如果用单一离散动作编码：
# action ∈ {0, 1, ..., 2M}
# action = 0: 不接入
# action = 2j - 1: 接入信道 j, overlay 模式
# action = 2j:     接入信道 j, underlay 模式

def action_to_channel_mode(action, M):
    if action == 0:
        return 0, None  # 不接入
    channel = (action + 1) // 2
    mode = 0 if action % 2 == 1 else 1  # 0=overlay, 1=underlay
    return channel, mode
```

### 2.4 Reward 计算（修正版，可直接编码）

```python
def compute_reward(vt_i, channel_j, mode, true_channel_state, 
                   h_su, h_su_pu, psi_pu, P_tx, B, mu, 
                   C_max, penalty_coeff, gamma=2.0):
    """
    计算即时奖励

    Args:
        vt_i: VT 索引
        channel_j: 信道索引 (1-indexed)
        mode: 0=overlay, 1=underlay
        true_channel_state: 真实信道状态 {0:idle, 1:PU_occupied, 2:SU_occupied}
        h_su: VT 到 BS 的信道增益 |h_t^{i,j}|^2
        h_su_pu: VT 到 PU 的信道增益 |h_t^{i,PU}|^2
        psi_pu: PU 干扰容限 Ψ_t^{j,PU}
        P_tx: VT 发射功率 P_t^{i,j}
        B: 带宽
        mu: 噪声功率
        C_max: 最大吞吐量 (归一化因子)
        penalty_coeff: 惩罚系数 ∂
        gamma: 质量强调指数 Γ (overlay 模式下放大 DQI)

    Returns:
        reward: 标量奖励
        throughput: 实际吞吐量
        interference: 干扰量
    """

    # 获取 DQI
    dqi = get_dqi(channel_j)  # Φ'_t^{j}

    # 如果不接入
    if channel_j == 0:
        return 0.0, 0.0, 0.0

    # === 不接入时的计算 ===
    # 对应 Eq. (no_access)
    # C = 0, Ω = 0

    # === 接入空闲信道 ===
    # 对应 Eq. (access_idle)
    # C = B * log2(1 + |h|^2 * P / mu)
    # Ω = 0
    if true_channel_state == 0:  # Idle
        throughput = B * np.log2(1 + h_su * P_tx / mu)
        interference = 0.0

    elif true_channel_state == 1:  # PU occupied
        if mode == 0:  # Overlay mode on PU-occupied channel → penalty
            # 对应 overlay Eq. for PU-occupied
            # C = 0
            # Ω = ∂ * |h_su_pu|^2 * P_tx / psi_pu
            throughput = 0.0
            interference = penalty_coeff * h_su_pu * P_tx / psi_pu

        else:  # mode == 1, Underlay mode on PU-occupied channel
            # 对应 underlay Eq. for PU-occupied
            # C = B * log2(1 + |h_su|^2 * P_tx / (mu + |h_su_pu|^2 * P_max))
            # Ω = ∂ * (psi_pu - |h_su_pu|^2 * P_tx)
            P_max = get_max_power(channel_j)
            throughput = B * np.log2(1 + h_su * P_tx / (mu + h_su_pu * P_max))
            interference = penalty_coeff * (psi_pu - h_su_pu * P_tx)

    elif true_channel_state == 2:  # SU (other VT) occupied
        # 对应 overlay Eq. for SU-occupied
        # C = 0
        # Ω = ∂ * |h_su_su|^2 * P_tx
        throughput = 0.0
        # 需要 VT-VT 信道增益
        h_su_su = get_su_su_channel(vt_i, channel_j)
        interference = penalty_coeff * h_su_su * P_tx

    # === 根据模式组合奖励 ===
    # Overlay: r = (Γ * C / C_max) - Ω   (Eq. reward_definition_final, overlay case)
    #   — DQI 被放大为 Γ, 鼓励选高 DQI 信道
    # Underlay: r = (Φ' * C / C_max) + Ω  (Eq. reward_v3, underlay case)
    #   — 原始 DQI, Ω 为正值时表示满足约束的程度

    if mode == 0:  # Overlay
        reward = gamma * (throughput / C_max) - interference
    else:  # Underlay
        reward = dqi * (throughput / C_max) + interference

    # ⚠️ 审稿人建议的修正：增加 interference violation penalty
    # 在 underlay 下，如果违反干扰约束，施加额外惩罚
    if mode == 1 and true_channel_state == 1:
        # 检查是否违反 PU 干扰约束
        if h_su_pu * P_tx > psi_pu:
            violation_penalty = penalty_coeff * (h_su_pu * P_tx - psi_pu) / psi_pu
            reward -= violation_penalty  # 这是审稿人 R3-C6 要求的修正

    # 可选：Reward clipping
    reward = np.clip(reward, -10.0, 10.0)

    return reward, throughput, interference
```

### 2.5 Underlay 功率控制（闭式约束）

```python
def underlay_power_control(h_su_pu, psi_pu, P_max):
    """
    Underlay 模式下的功率控制
    对应审稿人 R1-C8 的要求

    Args:
        h_su_pu: |h_t^{i,PU}|^2 — VT 到 PU 的信道增益
        psi_pu: Ψ_t^{j,PU} — PU 干扰容限
        P_max: P_t^{MAX,j} — 最大发射功率

    Returns:
        P_tx: 实际发射功率
    """
    # 闭式功率约束: P_t^{i,j} = min(P_max, psi_pu / h_su_pu)
    if h_su_pu > 0:
        P_allowed = psi_pu / h_su_pu
    else:
        P_allowed = P_max  # 没有 PU 干扰时用最大功率

    P_tx = min(P_max, P_allowed)

    # 可选：离散化功率级别
    # power_levels = np.linspace(0.1 * P_max, P_max, 5)  # 5 档
    # P_tx = power_levels[np.searchsorted(power_levels, P_allowed) - 1]

    return P_tx
```

---

## 3. 代码模块化拆解

### 3.1 模块总览

```
c:\...\cvn-dsa-esn-ddqn\
├── environment/
│   ├── __init__.py
│   ├── cvn_env.py            # Gym-style 仿真环境（核心）
│   ├── channel.py             # 信道模型（路径损耗、衰落、SNR/RSS）
│   ├── pu_model.py            # PU 活动模型（Markov chain）
│   ├── sensing.py             # 频谱感知模型（Pd/Pfa）
│   ├── traffic.py             # 流量模型（包到达、队列）
│   └── mobility.py            # 车辆移动性模型
│
├── models/
│   ├── __init__.py
│   ├── dqi.py                 # Module 1: Transformer DQI Evaluator
│   ├── predictor.py           # Module 2: Attention-LSTM Predictor
│   ├── esn.py                 # Module 3: Echo State Network
│   ├── ddqn.py                # Module 3: DDQN networks (eval + target)
│   └── agent.py               # Module 3: ESN-DDQN Agent (整合)
│
├── training/
│   ├── __init__.py
│   ├── trainer.py             # 训练主循环
│   ├── replay_buffer.py       # 经验回放缓冲区
│   └── reward.py              # Reward 函数（见上文 2.4）
│
├── baselines/
│   ├── __init__.py
│   ├── q_learning.py          # Tabular Q-learning
│   ├── mlp_ddqn.py            # MLP-DDQN
│   ├── lstm_ddqn.py           # LSTM-DDQN
│   ├── ddqn_baseline.py       # 标准 DDQN (no ESN)
│   └── ppo_baseline.py        # PPO baseline（审稿人要求）
│
├── experiments/
│   ├── configs/               # YAML/JSON 实验配置文件
│   │   ├── base.yaml
│   │   ├── large_scale.yaml
│   │   ├── robustness.yaml
│   │   └── ablation.yaml
│   ├── run_experiment.py      # 单次实验入口
│   └── run_sweep.py           # 批量实验 + 参数扫描
│
├── analysis/
│   ├── plot_plr.py            # PLR 图
│   ├── plot_throughput.py     # 吞吐量图
│   ├── plot_convergence.py    # 收敛曲线
│   ├── plot_ablation.py       # 消融实验分析
│   └── statistical_tests.py   # 统计检验
│
├── tests/
│   ├── test_env.py
│   ├── test_dqi.py
│   ├── test_reward.py
│   └── test_agent.py
│
├── configs/                   # 全局配置
│   └── default.yaml
│
├── requirements.txt
├── setup.py
├── README.md
├── LICENSE
└── CITATION.cff
```

### 3.2 核心模块接口定义

#### 3.2.1 环境模块 (Gym-style)

```python
# environment/cvn_env.py

class CVNEnvironment:
    """
    CVN 频谱接入仿真环境

    遵循 Gymnasium 接口规范，便于集成 Stable-Baselines3 等框架
    """

    def __init__(self, config: dict):
        """
        Args:
            config: 包含所有环境参数的字典
                - M: int, 信道数
                - N: int, VT 数
                - slot_duration: float, slot 时长
                - p01, p10: float, PU Markov 转移概率
                - P_fa, P_md: float, 感知误差概率
                - pa: float, 包到达概率
                - T_upd: int, DQI/预测更新间隔
                - T_stat: int, 统计描述子有效期
                - mobility_model: str, 移动模型类型
                - channel_model: str, 信道模型类型
                - seed: int, 随机种子
        """
        ...

    def reset(self) -> np.ndarray:
        """重置环境，返回初始 state"""
        ...

    def step(self, actions: np.ndarray) -> tuple:
        """
        执行 N 个 VT 的动作

        Args:
            actions: shape (N,), 每台 VT 的动作

        Returns:
            states: shape (N, state_dim), 下一状态
            rewards: shape (N,), 即时奖励
            dones: shape (N,), 是否终止
            info: dict, 含 throughput, interference, violation_rate 等统计
        """
        ...

    def get_state(self, vt_idx: int) -> np.ndarray:
        """
        构造 VT 的状态向量
        S_t^i = {δ_t^i, Φ'_t, θ_t}
        """
        ...

    @property
    def state_dim(self) -> int:
        """状态空间维度"""
        return self.M * 3  # sensing + DQI + prediction per channel

    @property
    def action_dim(self) -> int:
        """动作空间维度"""
        return 2 * self.M + 1  # no-access + overlay + underlay per channel
```

#### 3.2.2 DQI 模块

```python
# models/dqi.py

class TransformerDQI(nn.Module):
    """
    基于 Transformer Encoder 的信道质量评估器

    输入: 历史特征序列 X_t^j = [γ, ξ, B] over T slots, for j=1..M
    输出: DQI Φ'_t^j ∈ (0, 1), 归一化链路质量指标

    论文 Section III-B
    """

    def __init__(self, M, T, d_model=64, nhead=4, num_layers=2):
        """
        Args:
            M: 信道数
            T: 观测窗口长度 (slots)
            d_model: Transformer 隐层维度
            nhead: 注意力头数
            num_layers: Encoder 层数
        """
        super().__init__()
        # W_L: Learnable embedding matrix (压缩)
        self.embedding = nn.Linear(T, d_model)

        # Positional encoding (可训练)
        self.pos_encoding = nn.Parameter(torch.randn(M, d_model))

        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=256, dropout=0.1, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Output: W_o and b_o
        self.output = nn.Linear(d_model, 1)

        # Final sigmoid
        self.sigmoid = nn.Sigmoid()

    def forward(self, U):
        """
        Args:
            U: shape (batch, M, T)
               每行为一个信道的 T-slot 历史特征向量

        Returns:
            Phi_prime: shape (batch, M)
               每信道的 DQI, 0~1
        """
        # Step 1: Embedding → shape (batch, M, d_model)
        #   U 的每行是 T 维，通过 W_L 压缩到 d_model
        #   Eq. (compression): Ū = W_L · U
        batch_size = U.shape[0]
        U_bar = self.embedding(U)  # (batch, M, d_model)

        # Step 2: Positional Encoding
        #   Eq. (position): Ũ = Ū + Ũ_p
        U_tilde = U_bar + self.pos_encoding.unsqueeze(0)  # (batch, M, d_model)

        # Step 3: Self-Attention via Transformer Encoder
        #   Q = ŨW_q, K = ŨW_k, V = ŨW_v  (built into encoder)
        #   Θ^{i,j} = (1/√d_k) q_i k_j^T
        #   z^{i,j} = Σ_j Θ^{i,j} v_j
        Z = self.encoder(U_tilde)  # (batch, M, d_model)

        # Step 4: Output projection + Sigmoid
        #   Φ = Z W_o + b_o
        #   Φ'_j = σ(Φ_j)
        Phi = self.output(Z).squeeze(-1)  # (batch, M)
        Phi_prime = self.sigmoid(Phi)

        return Phi_prime
```

#### 3.2.3 Predictor 模块

```python
# models/predictor.py

class AttentionLSTM(nn.Module):
    """
    注意力增强 LSTM 信道预测器

    输入: Y_{t-T:t-1} ∈ {0,1,2}^{M×T}
    输出: θ_t^j ∈ (0,1) — 下一 slot 的空闲概率

    论文 Section III-C
    """

    def __init__(self, M, T, hidden_size=128, num_layers=2):
        super().__init__()
        self.M = M
        self.T = T

        # 输入嵌入: {0,1,2} → embedding_dim
        self.embedding = nn.Embedding(3, hidden_size)

        # LSTM
        self.lstm = nn.LSTM(
            input_size=M * hidden_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )

        # Attention
        self.attention = nn.Linear(hidden_size, 1)

        # Output
        self.output = nn.Linear(hidden_size, M)

        self.sigmoid = nn.Sigmoid()

    def forward(self, Y_history):
        """
        Args:
            Y_history: shape (batch, M, T)
               每个 channel 的 T-slot 状态序列
               值域 {0, 1, 2}

        Returns:
            theta: shape (batch, M)
               每个 channel 的 predicted idle probability
        """
        ...


class SimplePredictor(nn.Module):
    """
    简单预测器 baseline（审稿人 R3-C3 要求的 DQI baseline 的对应物）
    可选：Markov model, XGBoost, 或 2-layer MLP
    """
    ...
```

#### 3.2.4 ESN 模块

```python
# models/esn.py

class EchoStateNetwork(nn.Module):
    """
    回声状态网络

    论文 Section IV-C

    关键特征:
    - 只训练 readout 权重
    - Reservoir 权重随机初始化后固定
    - 满足 echo-state property
    """

    def __init__(self, input_dim, reservoir_size=200, spectral_radius=0.9,
                 input_scaling=0.1, leak_rate=0.3):
        """
        Args:
            input_dim: 输入维度 (= state_dim)
            reservoir_size: R — reservoir 神经元数
            spectral_radius: ρ(W_res) — 谱半径 (< 1 保证 echo-state)
            input_scaling: 输入缩放因子
            leak_rate: α — leaky integrator 速率
        """
        super().__init__()

        # 随机初始化 reservoir 权重（固定，不训练）
        W_res = torch.randn(reservoir_size, reservoir_size)
        rho = torch.linalg.eigvals(W_res).abs().max()
        self.W_res = nn.Parameter(W_res * (spectral_radius / rho),
                                   requires_grad=False)  # 固定!

        # 输入权重
        self.W_in = nn.Parameter(
            torch.randn(reservoir_size, input_dim) * input_scaling,
            requires_grad=False  # 固定!
        )

        # Feedback 权重（可选）
        self.W_fb = nn.Parameter(
            torch.randn(reservoir_size, input_dim) * 0.01,
            requires_grad=False
        )

        # Readout 权重（唯一可训练的部分）
        self.W_out = nn.Linear(reservoir_size, input_dim)

        self.reservoir_size = reservoir_size
        self.leak_rate = leak_rate
        self.activation = nn.ReLU()  # 原论文用 ReLU

        # 初始 reservoir state
        self.register_buffer('reservoir_state',
                              torch.zeros(reservoir_size))

    def forward(self, x):
        """
        Args:
            x: shape (batch, input_dim) — state vector S_t

        Returns:
            q_values: shape (batch, output_dim) — Q-values
        """
        # Reservoir state update:
        #   r̃_t = f(W_in·x_t + W_res·r_{t-1})
        #   r_t = (1-α)·r_{t-1} + α·r̃_t  (leaky integration)
        pre_activation = (torch.matmul(x, self.W_in.T) +
                          torch.matmul(self.reservoir_state, self.W_res.T))

        r_tilde = self.activation(pre_activation)

        self.reservoir_state = (
            (1 - self.leak_rate) * self.reservoir_state +
            self.leak_rate * r_tilde
        )

        # Readout
        return self.W_out(self.reservoir_state)

    def reset_state(self):
        """重置 reservoir 状态"""
        self.reservoir_state.zero_()
```

#### 3.2.5 ESN-DDQN Agent

```python
# models/agent.py

class ESNDDQNAgent:
    """
    ESN-DDQN 智能体

    整合 ESN + DDQN (eval network + target network)
    """

    def __init__(self, state_dim, action_dim, config):
        """
        Args:
            state_dim: 状态维度
            action_dim: 动作维度 (2M+1)
            config: 超参数配置
        """
        # ESN 层
        self.esn = EchoStateNetwork(
            input_dim=state_dim,
            reservoir_size=config.get('reservoir_size', 200),
            spectral_radius=config.get('spectral_radius', 0.9),
            input_scaling=config.get('input_scaling', 0.1),
            leak_rate=config.get('leak_rate', 0.3),
        )

        # Eval DDQN: ESN + FC layers
        self.eval_net = nn.Sequential(
            self.esn,
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim),
        )

        # Target DDQN: 同样的结构
        self.target_net = copy.deepcopy(self.eval_net)
        self.target_net.eval()

        self.optimizer = optim.Adam(self.eval_net.parameters(),
                                     lr=config['lr'])

        self.gamma = config.get('gamma', 0.9)       # discount
        self.epsilon = config.get('epsilon', 1.0)     # exploration
        self.epsilon_min = config.get('epsilon_min', 0.01)
        self.epsilon_decay = config.get('epsilon_decay', 0.995)
        self.target_update_freq = config.get('target_update_freq', 100)

    def select_action(self, state):
        """ε-greedy 动作选择"""
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        else:
            with torch.no_grad():
                q_values = self.eval_net(state)
                return q_values.argmax().item()

    def update(self, replay_buffer, batch_size):
        """
        DDQN 更新:
        1. 从 replay buffer 采样
        2. Current Q: eval_net(state)[action]
        3. Next action: argmax_a eval_net(next_state)
        4. Target Q: reward + γ * target_net(next_state)[next_action]
        5. Loss: MSE(current_Q, target_Q)
        """
        ...
```

---

## 4. 推荐技术栈

| 层级 | 技术选择 | 理由 |
|------|---------|------|
| 语言 | Python 3.10+ | 生态最成熟 |
| 深度学习框架 | **PyTorch 2.x** | DRL 社区首选，灵活性高 |
| 环境接口 | **Gymnasium (gym)** | 标准化接口，可与 SB3 互操作 |
| DRL baseline 库 | **Stable-Baselines3** (仅用于 baseline) | 提供 PPO/DQN/SAC 标准实现 |
| 配置管理 | **Hydra** 或 OmegaConf | 实验参数管理 |
| 日志与追踪 | **Weights & Biases** 或 TensorBoard | 实验追踪、可视化 |
| 数组计算 | NumPy, SciPy | |
| 绘图 | Matplotlib + Seaborn | 论文级图表 |
| 代码质量 | ruff (lint), mypy (type check), pytest | |
| 版本控制 | Git + GitHub | 开源必备 |

### requirements.txt 示例

```
torch>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
gymnasium>=0.29.0
stable-baselines3>=2.0.0
hydra-core>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
tqdm>=4.65.0
wandb>=0.15.0       # 可选
pytest>=7.3.0
ruff>=0.0.260
```

---

## 5. 实验矩阵设计

### 5.1 核心实验配置矩阵

| Exp ID | 实验目的 | M | N | p01 | p10 | pa | 速度 | 随机种子 | 对应审稿人 |
|--------|---------|---|---|-----|-----|-----|------|---------|-----------|
| E1 | 基线小规模（原论文） | 3 | 5 | 0.2 | 0.2 | 0.5 | 50 | 5 seeds | 保留 |
| E2 | 基线小规模 | 5 | 3 | 0.2 | 0.2 | 0.5 | 50 | 5 seeds | 保留 |
| **E3** | **中等规模** | 10 | 15 | 0.2 | 0.2 | 0.5 | 50 | 5 seeds | R1-C10, R3-C7 |
| **E4** | **中等规模** | 15 | 10 | 0.2 | 0.2 | 0.5 | 50 | 5 seeds | R1-C10, R3-C7 |
| **E5** | **大规模（稀缺）** | 20 | 30 | 0.2 | 0.2 | 0.5 | 80 | 3 seeds | R1-C10, R3-C7 |
| **E6** | **大规模（充裕）** | 30 | 20 | 0.2 | 0.2 | 0.5 | 80 | 3 seeds | R1-C10, R3-C7 |
| E7 | PU 流量变化 | 10 | 15 | 0.1 | 0.3 | 0.5 | 50 | 3 seeds | R2-C5 |
| E8 | PU 流量变化 | 10 | 15 | 0.3 | 0.1 | 0.5 | 50 | 3 seeds | R2-C5 |
| E9 | PU 流量变化 | 10 | 15 | 0.5 | 0.1 | 0.5 | 50 | 3 seeds | R2-C5 |
| E10 | 高速场景 | 10 | 15 | 0.2 | 0.2 | 0.5 | 120 | 3 seeds | R1-C10 |
| E11 | 预测误差鲁棒性 | 10 | 15 | 0.2 | 0.2 | 0.5 | 50 | 3 seeds | R1-C9 |
| E12 | T_upd 敏感性 | 10 | 15 | 0.2 | 0.2 | 0.5 | 50 | 3 seeds | R1-C11 |

### 5.2 方案矩阵（每个实验配置下都跑）

| 方案 ID | 方案名 | 类型 | 说明 |
|---------|--------|------|------|
| S1 | **Proposed (Full Model)** | 本文方法 | ESN-DDQN + DQI + Prediction |
| S2 | Fixed Overlay | Baseline | 只接入 idle 信道 |
| S3 | Fixed Underlay | Baseline | 允许低功率共存 |
| S4 | No-Prediction | Ablation | 去掉预测模块 |
| S5 | No-DQI | Ablation | 去掉 DQI 模块 |
| **S6** | **Standard DDQN** | **新 Baseline** | DDQN 无 ESN（审稿人 R2-C7） |
| **S7** | **PPO (Discrete)** | **新 Baseline** | PPO 离散动作版（审稿人 R3-C8） |
| **S8** | **Weighted-Sum DQI** | **新 Ablation** | 简单加权 DQI 替代 Transformer（审稿人 R3-C3） |
| S9 | Q-Learning | Baseline | Tabular（保留原论文） |
| S10 | MLP-DDQN | Baseline | 保留原论文 |
| S11 | LSTM-DDQN | Baseline | 保留原论文 |

### 5.3 评价指标矩阵

| 指标 | 缩写 | 说明 | 对应原论文图 |
|------|------|------|------------|
| VT 丢包率 | PLR | dropped / total packets | Fig.4, Fig.5 |
| VT 平均吞吐量 | VT-TP | bps/Hz per VT | Fig.10, Fig.11 |
| PU 平均吞吐量 | PU-TP | bps/Hz per PU | Fig.6, Fig.7 |
| 平均选中 DQI | Avg-DQI | DQI of selected channel | Fig.8, Fig.9 |
| 收敛迭代数 | Conv-Iter | 达到稳态的 episode/slot 数 | Fig.12 |
| **PU 干扰违反率** ⭐ | **PU-VR** | P(violation) per underlay access | **新增** |
| **预测准确率** ⭐ | **Pred-Acc** | Idle/busy prediction accuracy | **新增** |
| **训练时间** ⭐ | **Train-Time** | Wall-clock training time | **新增** |
| **推理延迟** ⭐ | **Inf-Lat** | Per-decision inference time (ms) | **新增** |
| **通信开销** ⭐ | **Comm-OH** | Broadcast payload size (bits/T_upd) | **新增** |

⭐ = 审稿人要求新增的指标

### 5.4 实验执行优先级

```
P0 (必须做):
  E1-E6 (所有规模)  ×  S1-S8 (所有方案)
  → 产出: 完整的性能对比图 + error bars

P1 (强烈建议):
  E7-E9 (PU 流量变化)  ×  S1-S7 (核心方案)
  E11 (预测误差鲁棒性)  ×  S1, S4, S6
  → 产出: 鲁棒性分析图

P2 (锦上添花):
  E10 (高速场景)
  E12 (T_upd 敏感性)
  → 产出: 额外敏感性分析
```

---

## 6. 开源项目结构建议

### 6.1 GitHub 仓库 README 大纲

```markdown
# CVN-DSA-ESN-DDQN

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)

## Overview

Official implementation of **"A High-Quality ESN-DDQN-Based Adaptive Access Algorithm for Cognitive Vehicular Networks"**.

This repository provides:
- A realistic CVN simulation environment for DSA
- Transformer-based Dynamic Quality Index (DQI) evaluation
- Attention-LSTM channel occupancy prediction
- ESN-DDQN adaptive overlay/underlay access agent
- Comprehensive baselines (DDQN, PPO, Q-Learning, etc.)
- Reproducible experiment configurations

## Key Features

- ✅ Fully reproducible experiments with random seed control
- ✅ Multiple scales: from 3ch/5VTs to 30ch/20VTs
- ✅ Realistic channel models (3GPP TR 38.901)
- ✅ Configurable PU traffic patterns (Markov + periodic)
- ✅ Imperfect spectrum sensing (Pd/Pfa)
- ✅ Comprehensive metrics (PLR, throughput, PU violation rate)
- ✅ Modular design for easy extension

## Quick Start

### Installation

```bash
git clone https://github.com/yourname/cvn-dsa-esn-ddqn.git
cd cvn-dsa-esn-ddqn
pip install -e .
```

### Run a Quick Experiment

```bash
python experiments/run_experiment.py --config configs/base.yaml
```

### Reproduce Paper Results

```bash
python experiments/run_sweep.py --sweep configs/paper_reproduce.yaml
```

## Project Structure

[... 目录树 ...]

## Citation

If you use this code in your research, please cite:

```bibtex
@article{yang2026cvn,
  title={...},
  author={Yang, Zumin and Li, Guoquan and Wu, Ruiheng and Lin, Jinzhao and Pang, Yu},
  journal={IEEE Transactions on Vehicular Technology},
  year={2026}
}
```

## License

MIT License.
```

### 6.2 CITATION.cff

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite the paper."
authors:
  - family-names: Yang
    given-names: Zumin
  - family-names: Li
    given-names: Guoquan
  - family-names: Wu
    given-names: Ruiheng
  - family-names: Lin
    given-names: Jinzhao
  - family-names: Pang
    given-names: Yu
title: "A High-Quality ESN-DDQN-Based Adaptive Access Algorithm for Cognitive Vehicular Networks"
repository-code: "https://github.com/yourname/cvn-dsa-esn-ddqn"
license: MIT
```

---

## 7. 里程碑与工作量估算

### 第 1-3 天：环境搭建

- [ ] 创建 VS Code workspace，初始化 Git
- [ ] 搭建 Python 虚拟环境，安装依赖
- [ ] 实现 `environment/channel.py`（信道模型）
- [ ] 实现 `environment/pu_model.py`（PU Markov chain）
- [ ] 实现 `environment/sensing.py`（频谱感知）
- [ ] 实现 `environment/traffic.py`（流量模型）
- [ ] 实现 `environment/mobility.py`（移动性）
- [ ] 整合为 `environment/cvn_env.py`
- [ ] 编写环境单元测试

### 第 4-6 天：模型实现

- [ ] 实现 `models/esn.py`
- [ ] 实现 `models/ddqn.py`（eval + target network）
- [ ] 实现 `models/agent.py`（ESN-DDQN agent）
- [ ] 实现 `training/replay_buffer.py`
- [ ] 实现 `training/reward.py`
- [ ] 实现 `training/trainer.py`
- [ ] 跑通一个最小实验（M=3, N=3）

### 第 7-10 天：DQI + Predictor

- [ ] 实现 `models/dqi.py`（Transformer DQI）
- [ ] 实现 `models/predictor.py`（Attention-LSTM）
- [ ] DQI 训练 pipeline
- [ ] Predictor 训练 pipeline
- [ ] 集成到环境 + agent

### 第 11-16 天：Baseline

- [ ] 实现 Q-Learning, MLP-DDQN, LSTM-DDQN
- [ ] 实现标准 DDQN (no ESN)
- [ ] 实现 PPO (discrete)
- [ ] 实现 Weighted-Sum DQI
- [ ] 跑出全部 baseline 数据

### 第 17-22 天：大规模实验

- [ ] 跑 E1-E6 所有规模
- [ ] 绘制所有对比图（带 CI/error bar）
- [ ] 跑 E7-E12 鲁棒性实验

### 第 23-28 天：分析 + 论文修改

- [ ] 统计分析（t-test, ANOVA）
- [ ] 绘制论文级图表
- [ ] 更新 `main.tex` 实验部分
- [ ] 撰写 response letter
- [ ] 清理代码、写 README
- [ ] 开源发布

**总计：约 4 周全职，或 6-8 周兼职。**

---

## 附录：论文公式 → 代码对照表

| 论文公式 | 行号 | 代码位置 | 说明 |
|---------|------|---------|------|
| SNR Eq.(1) | ~170 | `environment/channel.py` | 每 slot 计算 |
| RSS Eq.(2) | ~175 | `environment/channel.py` | 每 slot 计算 |
| Compression Eq. | ~200 | `models/dqi.py:forward()` step 1 | W_L 嵌入 |
| Position Eq. | ~205 | `models/dqi.py:forward()` step 2 | Positional encoding |
| Attention Θ Eq. | ~215 | `models/dqi.py:forward()` step 3 | Transformer 内部 |
| DQI output Eq. | ~225 | `models/dqi.py:forward()` step 4 | Sigmoid |
| State space Eq. | ~260 | `environment/cvn_env.py:get_state()` | |
| Action space Eq. | ~265 | `environment/cvn_env.py:step()` | |
| Overlay reward Eq.(12) | ~275 | `training/reward.py:compute_reward()` | mode=0 |
| Underlay reward Eq. | ~300 | `training/reward.py:compute_reward()` | mode=1 |
| ε-greedy Eq. | ~330 | `models/agent.py:select_action()` | |
| DDQN target Eq. | ~335 | `models/agent.py:update()` | |
| MSE loss Eq. | ~340 | `models/agent.py:update()` | |
