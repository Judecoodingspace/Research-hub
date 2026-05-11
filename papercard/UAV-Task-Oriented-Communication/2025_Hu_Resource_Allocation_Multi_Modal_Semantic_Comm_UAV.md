# Hu 2025 — Resource Allocation for Multi-Modal Semantic Communication in UAV Collaborative Networks

> IEEE TCOM, Vol.73, No.9, Sep 2025 | Han Hu, Xingwu Zhu, Fuhui Zhou, Wei Wu, Rose Qingyang Hu, Hongbo Zhu

---

## 1. Problem

**论文试图解决什么问题？**
现有 UAV 语义通信资源分配工作存在三个空白：① 大多只做单模态（图像），未利用多模态（图像↔文本）的灵活性和鲁棒性；② 大多忽略语义级因素（如传输语义符号数 K）对系统性能的影响，只做传统比特级资源分配；③ 多 UAV 协同中继通信和轨迹优化未被纳入语义资源分配框架。核心问题：**在多 UAV 中继协作网络中，如何联合优化 UAV 轨迹、传输功率、频谱带宽和传输语义符号数 K，在最大化用户体验质量（QoE）的同时最小化传输代价？**

问题偏向：**资源分配不合理** + **多模态语义没有统一建模**

---

## 2. Setting / Assumptions

| 维度 | 设定 |
|------|------|
| UAV 数量 | **多 UAV**（M 个区域，每个区域 1 架 UAV），UAV 间可中继协作 |
| 边缘服务器 | 无独立 MEC——UAV 直接与地面用户通信或 UAV 间中继 |
| 异构算力 | 未显式建模（所有 UAV 同构） |
| 信道假设 | A2A：LoS 自由空间路径损耗；A2G：概率 LoS/NLoS + Rician/Rayleigh 小尺度衰落 |
| 路径/任务 | 轨迹可变（每时步优化飞行距离 lm和角度 ϑm），但限制在区域内 |
| 模型切分 | 无切分（UAV 发送端做语义编码，用户接收端做解码） |
| 多视角 | 隐式存在（不同区域 UAV 拍摄互补信息），但未显式建模视角融合 |
| 模态 | **多模态**：图像↔图像（image-to-image transceiver）+ 图像→文本（image-to-text transceiver） |
| 协作机制 | **UAV 中继协作**：跨区域传输时，源 UAV → 中继 UAV → 地面用户 |

---

## 3. Core Idea

**"把语义符号数 K 作为可优化变量，与功率、带宽、轨迹并列——用混合决策 DRL（离散选 K + 连续选功率/带宽/轨迹）在多 UAV 中继网络中联合优化 QoE 与传输代价"**。

这条思路的关键跳跃是：K（语义符号数）不再是一个固定的模型超参数，而是一个**随信道和任务动态调整的决策变量**——信道好时多传符号（高精度）、信道差时少传符号（保连通）。同时，多模态（图→图、图→文本）提供了两条不同精度的传输路径，DRL 可以在资源紧张时自动切换到文本模态。

---

## 4. Key Mechanism

### 4.1 多模态语义传输架构
- **Image-to-Image transceiver**：ViT 编码器 → 信道 → Transformer 解码器 → 重建图像（SSIM 评估）
- **Image-to-Text transceiver**：ViT 编码器 → 信道 → Transformer 解码器 → 文本描述（BLEU 评估）
- 可选 K 值：图像 KI={192,256,320,384}，文本 KT={36,48,60,72}

### 4.2 QoE 定义（核心创新）
```
QoE = sigmoid(D_th - D) × sigmoid(H - H_th)
```
其中 D 是端到端传输时间，H 是接收语义信息量（语义熵）。两个 sigmoid 相乘确保体验质量要求传输快 + 信息量大同时满足。

### 4.3 语义熵与语义速率
- **近似语义熵 ˜HJ**：在无信道影响下，满足精度 ν 所需的最少语义符号数
- **语义速率**：˜HJ / 传输时间
- 精度函数 fJ(K,γ) 通过 sigmoid 曲线拟合实际测量值

### 4.4 MHDCD-MSC 算法（混合决策 DRL）
- **每个 UAV = 多子 agent**：轨迹优化子 agent + 每个关联实体（用户/其他UAV）一个资源分配子 agent
- **混合动作空间**：K（离散选择）+ P/B（连续，由 DDPG-style actor 输出）+ 轨迹（连续）
- **离散-连续解耦**：actor 先为每个候选 K 生成最优连续动作 (P,B)，critic 再选 Q 值最高的 K
- 基于 DDPG + DQN 混合架构

### 4.5 优化问题
```
max Σ(αq×QoE - αc×Cost)
s.t. 轨迹范围、功率/带宽上限、传输时间 ≤ Dth、精度 ≥ φth
```

### 4.6 UAV 中继协作
- 同区域：UAV → 地面用户（A2G 直达）
- 跨区域：源 UAV → 中继 UAV（A2A LoS）→ 地面用户（A2G）
- A2A 仅用图像模态（确保质量），A2G 可用图/文双模态

---

## 5. Experiments

| 维度 | 详情 |
|------|------|
| 场景 | M=2 区域，半径 200m，间距 600m，UAV 高度 100m |
| 用户分布 | 每区域 Nm=5 用户，随机移动 |
| 数据集 | Karpathy splits（123287 张图 + 5 文本描述/图） |
| 语义模型 | 预训练 ViT 编码器 + Transformer 解码器（8层图像/4层文本） |
| 对比方案(5个) | ① MHDCD-MSCFP（固定位置）、② MHDCD-ISC（仅图像模态）、③ MADDPG-ISCFS（固定 K=256）、④ MADDPG-TC（传统JPEG+BPG+LDPC）、⑤ EA-MSC（均等分配+DQN选K） |
| 指标 | QoE、传输代价、QoE-Cost 权衡曲线、收敛速度 |
| 训练 | 500 episodes × 200 steps，ε-greedy=0.1，replay buffer=20000 |

**关键结论**：
- MHDCD-MSC 在 QoE 和传输代价上均优于 5 个基线
- 多模态（图+文）显著优于纯图像模态（MHDCD-ISC）
- 可变 K 优于固定 K=256（MADDPG-ISCFS）
- 轨迹优化 + 协作中继是关键贡献点
- 收敛速度快于 MADDPG

**消融实验**：**较好**。5 个基线实质上构成了消融：
- MHDCD-MSCFP 消融了轨迹优化
- MHDCD-ISC 消融了多模态
- MADDPG-ISCFS 消融了可变 K
- MADDPG-TC 消融了语义通信本身
- EA-MSC 消融了智能资源分配

**部署验证**：无。纯仿真，未在真实 UAV 上测试。

---

## 6. Strength

- **K 作为语义级优化变量**：这是本文最核心的贡献，将语义符号数从超参数提升为决策变量，建立了"语义级资源分配"的新维度
- **多模态灵活性**：图像↔文本双路径使 UAV 可以在资源紧张时自动降级到文本模态，提升系统鲁棒性
- **混合决策 DRL 设计精巧**：离散 K 选择 + 连续 P/B/轨迹 的解耦方案（actor 先算连续、critic 再选离散），避免了离散化或松弛的精度损失
- **baseline 丰富且合理**：5 个对比方案清晰地展示了轨迹优化、多模态、可变 K、语义通信 4 个维度的独立贡献
- **UAV 中继协作**：将 A2A + A2G 联合建模，考虑了跨区域信息获取场景

---

## 7. Weakness

- **UAV 同构假设**：所有 UAV 相同算力、相同模型——未考虑异构算力下的模型切分或负载分配
- **无 trigger/reject 机制**：所有采集图像都经过语义传输，没有"该不该传"的决策
- **QoE 定义与下游任务脱节**：QoE 基于语义熵和传输时间，但未与具体的下游任务指标（如检测 mAP、分类准确率）挂钩——用户最终关心的是任务完成质量，而非"收到多少语义信息"
- **ViT + Transformer 的计算代价**：在 UAV 嵌入设备上的推理延迟未报告，部署可行性存疑
- **A2A 只用图像模态**：未探索 A2A 也可用文本模态进一步压缩
- **区域划分固定**：UAV 区域预分配，未考虑动态区域调整

---

## 8. Reusable Part

| 可复用内容 | 说明 |
|-----------|------|
| K 作为决策变量 | 当前论文可将"传输 proposal 数量"或"B2/B3 特征压缩率"作为类似的可调节变量 |
| 混合决策 DRL 架构 | actor→连续, critic→离散 的解耦方案可复用到 Layer 2 pair 选择器 |
| QoE 定义的双 sigmoid | 可改造为当前论文的 utility formula：sigmoid(ΔF1) × sigmoid(-latency) |
| 多基线消融逻辑 | 5 基线对应 4 维独立贡献——当前论文可借鉴这种"每个 baseline 消融一个维度"的设计 |
| A2A+A2G 联合建模 | 当前论文已区分 A2A 和排队延迟，Hu 2025 的 A2A 路径损耗模型可辅助建模 |
| semantic entropy 概念 | 可启发当前论文定义"proposal 的信息量"指标 |

---

## 9. Attack Point

- **K 优化是"一维语义控制"**：当前论文的动作空间更丰富（B0/B2/B3 + pair selection），本质上是多维语义协作动作选择
- **缺少任务闭环**：当前论文直接用检测 mAP/F1 定义效用，比 Hu 2025 的"语义熵"更贴近实际任务
- **无预算约束的全局 trigger**：当前论文的 budget 约束触发策略是 Hu 2025 未涉及的新维度
- **无图像级增益预测**：当前论文的 ridge predictor (17 features, <1ms) 比 Hu 2025 的 ViT + Transformer + DRL 在部署效率上有明显优势

---

## 10. Relation to My Topic

**与当前论文（conditional semantic collaboration / multi-action selector）的关系**：

- **互补关系且可作高层对照**：Hu 2025 的优化变量是 K（语义符号数）、P（功率）、B（带宽）、轨迹——这是**资源分配层**。当前论文的优化变量是"是否触发 B2/B3 + 选哪个后端 UAV"——这是**协作决策层**。两层不直接竞争。
- **可作为写作支撑**：Hu 2025 的"K 作为可优化变量"思路可以佐证当前论文"协作动作选择也是可优化变量"的合理性——既然语义符号数都需要动态调整，协作策略当然更需要。
- **关键差异**：当前论文的核心是 trigger + pair selection（有没有增益），Hu 2025 是资源分配（有多少资源）。前者是"该不该传"，后者是"怎么传"。这个差异恰好可以用来在 Related Work 中定位当前论文的独特性。
- **可作为 baseline**：Hu 2025 的 EA-MSC（均等分配）对应当前论文的 always-B2/always-none 基线；MADDPG-ISCFS（固定 K）对应当前论文的固定阈值方案。

---

## 11. Scenario-Experiment Justification（场景-实验双重合理化）

### 11.1 Scenario → Algorithm Mapping

| 场景特征 | 引发的技术需求 | 选择的算法/模型 | 必要性强度 |
|----------|--------------|----------------|-----------|
| 多 UAV 区域覆盖，跨区域信息需求 | 需要 UAV 中继协作 | A2A LoS + A2G 两跳传输 | 强 |
| UAV 能量和带宽有限 | 传输代价需纳入优化 | 加权代价函数 αp·P+αb·B | 强 |
| 信道动态变化 | 传输策略需适应信道 | DRL（MHDCD-MSC） | 中 |
| 多模态灵活传输需求 | 图↔图 + 图→文本双路径 | ViT + Transformer 语义编解码 | 中 |
| 离散(K)+连续(P/B/轨迹)混合变量 | 需要混合决策优化 | actor-continuous + critic-discrete 解耦 | 中 |
| 无明显场景约束 | 为何用 ViT 而非 CNN？为何用 DRL 而非优化求解器？ | ViT + DDPG/DQN 混合 | **可疑** |

**关键分析**：论文在"为何需要 UAV 中继""为何需要多模态"上有场景支撑（跨区域、资源紧张），但在"为何用 ViT 而非更轻量编码器""为何必须用 DRL 而非基于模型的优化"上缺乏论证。

### 11.2 Ablation & Necessity Evidence

- **消融实验质量较高**：5 个 baseline 清晰对应 4 个维度的独立贡献
  - 轨迹优化：MHDCD-MSCFP vs. MHDCD-MSC（固定位置 vs. 可变轨迹）
  - 多模态：MHDCD-ISC vs. MHDCD-MSC（仅图像 vs. 图+文）
  - 可变 K：MADDPG-ISCFS vs. MHDCD-MSC（固定 K vs. 可变 K）
  - 语义通信本身：MADDPG-TC vs. MHDCD-MSC（传统编码 vs. 语义通信）
- **缺失**：没有单独移除子 agent 架构（集中式 vs. 分布式）的消融；没有单独移除 ViT（换用 ResNet）的消融

### 11.3 "Why Not Simpler" Logic

- **部分覆盖**：EA-MSC（均等分配+DQN）是一个较简单的 baseline，可以回答"为什么不用简单分配方案"
- **未覆盖**：未讨论"为什么不用基于模型的凸优化求解器"（如 block coordinate descent）——尤其是当精度函数 fJ(K,γ) 已有拟合曲线时，问题可能可用传统优化方法求解
- **未覆盖**：未讨论"为什么不用轻量级 CNN 编码器"——ViT 的计算代价在 UAV 场景下是否合理
- 存在**"杀鸡用牛刀"的局部嫌疑**：在精度函数可拟合的前提下，DRL 的必要性减弱

### 11.4 Defensibility Summary

**基本能经受"技术堆砌"质疑，但不够完美**。得益于 5 个 baseline 的消融设计，论文能展示轨迹、多模态、可变 K、语义通信 4 个维度的独立贡献。但 ViT 和 DRL 的选择缺乏"为什么不更简单"的论证。整体而言，这篇论文的论证结构值得当前论文借鉴：**每个核心机制对应一个消融 baseline**，让读者看到"去掉这个就不行"。

---

> 对照 `paper3_main_thread.md`：Hu 2025 的 K 优化与当前论文的 action selector 在决策维度上互补（资源级 vs. 协作决策级）。其消融 baseline 设计范式（每维一个 baseline）直接可作为当前论文实验矩阵设计的参考。其"QoE 定义与任务脱节"的弱点也反衬出当前论文将 utility 直接与检测 F1 挂钩的优势。
