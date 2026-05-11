# Hu 2025 Multi-Modal Resource Allocation → Paper 3 启发

> 来源：`papercard/UAV-Task-Oriented-Communication/2025_Hu_Resource_Allocation_Multi_Modal_Semantic_Comm_UAV.md`

## 核心启发：K作为优化变量 → "协作动作也是优化变量"

Hu 2025的核心论证链：语义符号数K不应固定 → 好信道多传、差信道少传 → 可变K > 固定K。

**结构同构平移**：协作动作不应固定 → 高增益图像触发B2/B3、低增益图像保持B0 → predictor-driven trigger > always-B2。

**论文中的直接引用**：
> "Hu et al. [2025] demonstrated that treating K as a dynamic optimization variable improves the QoE-cost tradeoff. Our work applies this principle to a different decision layer: instead of optimizing how many semantic symbols to transmit, we optimize which collaboration action to trigger and which backend UAV to engage."

## 5-Baseline消融范式 → 当前论文实验矩阵模板

| Hu 2025 Baseline | 消融维度 | 当前论文对应 |
|-----------------|---------|------------|
| MHDCD-MSCFP（固定位置） | 轨迹优化 | `fixed-pair`（始终选最近back） |
| MHDCD-ISC（仅图像模态） | 多模态 | `B2-only`（仅单动作） |
| MADDPG-ISCFS（固定K=256） | 可变K | `always-B2` / `always-B3` |
| MADDPG-TC（传统编码） | 语义通信 | `always-none (B0)` |
| EA-MSC（均等分配） | 智能分配 | `random-trigger-at-budget` |

## A2A信道形式化建模

Hu 2025的A2A LoS自由空间路径损耗公式可直接引用，补强当前论文System Model中A2A链路的建模严谨性。

## QoE双Sigmoid → 效用函数非线性扩展

Hu 2025的 `QoE = sigmoid(D_th-D) × sigmoid(H-H_th)` 暴露了当前论文线性效用的局限（边际惩罚恒定）。可在Discussion中展示sigmoid扩展路径，将线性效用论证为"参数高效的工程近似"。

## 混合决策架构 → Layer 2+3接口整合

Hu 2025的"actor生成候选→critic选择最优"可简化为当前论文的Layer 2+3接口：
1. Layer 3为当前图像预测每个action的效用
2. Layer 2为每个候选back计算完整utility（含延迟/负载/精度惩罚）
3. 选utility最高且>0的(back, action)

## 应列为Future Work

- 可变payload（B2(ρ), B3(ρ)）——仿照Hu 2025的可变K
- 区域化UAV部署——使pair选择从抽象列表变为空间约束问题
- 多back全局匹配（NBS博弈论）——仿照Hu 2025的多UAV协调
