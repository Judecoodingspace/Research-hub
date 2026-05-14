# CVN-DSA 横向比较

## 比较对象
- **Liu 2024** — Joint Collaborative Big Spectrum Data Sensing and RL-Based DSA for CIoV (IEEE TITS 2024)
- *（待后续文献加入扩展）*

## 总体判断

Liu 2024 是典型的"occupancy-only Q-learning for DSA"类工作，与 Paper 2 同属认知车联网频谱接入领域。两者的核心差异在于：

| 维度 | Liu 2024 | Paper 2 |
|------|----------|---------|
| 状态表征 | occupancy-only | 三合一（感知+质量+预测） |
| 接入模式 | Overlay/Underlay/Collaborative（3种） | Overlay/Underlay（2种，但含自适应切换） |
| 学习方法 | 标准 Q-learning（tabular） | ESN-DDQN（NN-based + 加速收敛） |
| 质量评估 | 无 | Transformer DQI |
| 占用预测 | 无 | Attention-LSTM |
| 移动性建模 | 无 | 50-120 km/h |
| 部署架构 | 纯分布式 | 服务器+客户端混合 |
| 实验消融 | 无 | 有（No-DQI / No-Prediction） |
| 实验规模 | 100×20,000 slots | 20×5,000 slots |
| PU 保护编码 | 干扰惩罚 + 动态定价 | 差异化 reward + 违规惩罚 |

**核心发现**：Liu 2024 的存在反过来验证了 Paper 2 的核心主张——仅靠"信道是否空闲"做接入决策是不够的，需要质量评估（DQI）和占用预测（Prediction）的补充。同时，Liu 2024 的实验设计弱点（无消融、无 error bar、无 violation rate）可作为 Paper 2 审稿回复中的"行业惯例"局部防御素材。

## 问题定义对比
（待扩展）

## 方法机制对比
（详见 papercard §4 Key Mechanism 对照）

## 与审稿意见的对应
| 审稿意见 | Liu 2024 的支撑价值 |
|----------|-------------------|
| R3-C1: ESN-RL 非全新 | Liu 2024 Ref [13] 是 ESN DSA 早期尝试，Paper 2 需引用和区隔 |
| R3-C3: Transformer 过度设计 | Liu 的 occupancy-only 更简单但导致 PU 干扰——反证单纯简化不够 |
| R1-C10: 缺 error bar / 大规模 | Liu 2024 也没有——行业惯例防御 |
| R2-C7: 缺强 DRL baseline | Liu 2024 也没有——行业惯例防御 |
| R1-C9: 缺 violation rate | Liu 2024 用"平均干扰功率"替代——violation rate 尚未成为标准指标 |
