# 2024 Qin - DRL-Based Resource Allocation and Trajectory Planning for NOMA-Enabled Multi-UAV Collaborative Caching 6G Network

## 基本信息
- 标题：DRL-Based Resource Allocation and Trajectory Planning for NOMA-Enabled Multi-UAV Collaborative Caching 6G Network
- 作者：Peng Qin, Yang Fu, Jing Zhang, Suiyan Geng, Jiayan Liu, Xiongwen Zhao
- 年份：2024
- 来源：IEEE Transactions on Vehicular Technology, vol. 73, no. 6, pp. 8750-8764
- DOI：10.1109/TVT.2024.3357086
- 本地 PDF：`papers/UAV-Resource-Alloaction/Qin 等 - 2024 - DRL-Based Resource Allocation and Trajectory Planning for NOMA-Enabled Multi-UAV Collaborative Cachi.pdf`

## 相关性 / 标签
- 相关性等级：中高相关
- 子方向标签：资源分配与调度；路径规划；边缘智能 / 空地协同
- 判断理由：论文是典型的“多 UAV 通信资源分配 + 轨迹规划”工作，而且显式讨论 NOMA 信道复用、功率控制和 UAV 协同缓存。但它的核心对象是内容缓存/分发，而不是任务计算与任务语义，因此与当前主线是“资源分配层面相关”，而非“任务导向层面直接贴合”。

## 1. Problem
论文研究热点区域中的 NOMA-enabled multi-UAV collaborative caching 6G network。作者要解决的问题是：在内容热度动态变化、用户移动、频谱资源有限的条件下，如何联合优化 UAV 缓存决策、3D 轨迹规划、功率分配和信道复用，从而最小化用户内容获取时延。

按当前主线分类，这篇论文更偏向：
- 传输效率不足
- 资源分配不合理
- 协同机制不足

它本质上是“低时延内容分发”问题，而不是“计算任务执行”问题。

## 2. Setting / Assumptions
- 场景包含 1 个 HAPS、多个 UAV 和大量移动用户（MUs）。
- 采用双时间尺度：大时间尺度做 caching decision，小时间尺度做内容投递和无线资源分配。
- UAV 预缓存热点内容；当本地缓存未命中时，可经其他 UAV 通过 HAPS 协作获取，若全局都未命中，则再从云端获取。
- UAV 采用 3D 轨迹建模，但默认恒定飞行速度，用球坐标方向角表示移动。
- U-M 链路采用概率 LoS/NLoS 路损模型。
- 频谱层采用 multi-cell NOMA with single-cell processing；每个正交子信道可被多个 UAV 复用，但复用上限预先给定。
- 论文没有显式计算模型，也没有 CPU/排队/算力预算建模；“资源分配”主要指缓存、功率和信道复用。
- 内容热度由用户请求统计得到，强调动态内容流行度。

## 3. Core Idea
核心思想是把原问题按照时间尺度和变量类型分解。

一方面，缓存决策在较慢时间尺度上变化，作者把它单独抽出，转化为“最大化长期加权缓存命中率”的多智能体决策问题，用 MAPPO 处理动态内容热度。

另一方面，轨迹、功率和信道复用发生在快速时间尺度上，而且动作空间同时包含连续变量（方向角、功率）和离散变量（子信道匹配）。作者于是采用“matching + DRL”联合框架：先用 many-to-one matching 处理离散的子信道复用关系，再用 DDPG 优化连续的轨迹与功率。

这种设计的关键在于：它不是硬做一个统一的超大混合动作空间 DRL，而是先拆动作空间，再分别求解。

## 4. Key Mechanism

### 4.1 任务/系统建模方式
- 系统采用 `content caching period + content delivery slot` 的双时间尺度模型。
- 每个 UAV 在每个缓存周期基于内容流行度 `ρ_(k,q)^c` 选择缓存内容。
- 用户请求内容后，存在三种获取路径：
- edge retrieving：本 UAV 直接命中
- collaborative retrieving：其他 UAV 命中，经 HAPS 中继
- cloud retrieving：云端经 feeder link + HAPS + UAV 传输

### 4.2 通信模型
- `U-M` 链路：概率 LoS/NLoS 路损模型，路径损耗随 UAV 与用户距离、飞行高度变化。
- `NOMA` 模型：
- 每个正交子信道可被多个 UAV 复用。
- 同一 UAV 服务同一簇用户时，用户按信道增益排序做 SIC。
- SINR 同时包含 intra-cell interference 与 inter-cell interference。
- 每个 UAV 在每个时隙最多占用一个正交信道，但每个信道可被至多 `ω_i^max` 个 UAV 复用。
- 平均投递速率由各时隙传输速率求平均后进入 delay model。

### 4.3 计算/缓存模型
- 这篇论文没有建立计算资源模型，也没有 CPU cycle、队列、能量-计算耦合项。
- 它真正建模的是缓存资源：二元缓存决策 `f_(k,q)(t_c)`，并受缓存容量 `σ_k` 约束。
- 因此，这篇文章在“资源分配”上的重点是 `cache + power + subchannel + trajectory`，不是 `compute + communication` 联合。

### 4.4 目标函数与约束
- 原问题 `P1` 的目标：最小化所有用户总内容获取时延。
- 关键约束包括：
- 缓存决策二元化与缓存容量约束
- 内容获取模式 one-hot 约束
- UAV 方向角与飞行高度约束
- UAV 发射功率上限约束
- 子信道分配二元约束
- 每 UAV 仅占用一个正交信道
- 每个正交信道复用数不超过阈值
- QoS 约束：三种获取方式的时延满足 `τ^Ed < τ^Co < τ^Cl < T_c`

### 4.5 多约束不等式的处理方式
- 原问题 `P1` 被分解为两个子问题：
- `SP1`：UAV collaborative caching
- `SP2`：joint trajectory + power + subchannel allocation
- `SP1` 不是直接最小化时延，而是转成最大化加权内容命中率 `Γ(t_c)`，用 MAPPO 做分布式缓存决策。
- `SP2` 则转成最大化 U-M 链路总传输速率。
- 对 `SP2` 中的离散子信道复用变量，作者采用带 peer effect 的 many-to-one matching，定义 UAV 与信道的效用函数，并通过 swap blocking pair 迭代得到稳定匹配。
- 对连续变量（轨迹方向角、功率），作者采用 DDPG，在给定子信道匹配结果后进行更新。

### 4.6 路径规划如何与资源分配结合
- UAV 轨迹通过改变 UAV-MU 距离，直接影响概率 LoS/NLoS 路损、SINR 和传输速率。
- 功率控制与子信道复用进一步影响 NOMA 干扰水平。
- 因此，轨迹规划并不是独立模块，而是通过 `rate -> delay` 链条与功率、信道复用一起作用于总获取时延。
- 但它的结合点主要发生在通信层，没有进入计算或任务执行层。

## 5. Experiments
- 缓存决策部分与 `Independent PPO`、`Distributed D3QN`、`Independent D3QN`、`QMIX`、`VDN`、`Greedy caching` 比较，验证 weighted hit ratio。
- 轨迹/资源分配部分与以下方法比较：
- 基于 `SCA` 的近似最优资源分配
- 不做资源分配优化的 DDPG
- 只优化 matching、不优化功率的 DDPG
- 不做轨迹规划的 DDPG
- 指标包括：
- average weighted content hit ratio
- average content retrieving delay
- system throughput
- 训练收敛
- 结果显示：
- 所提方法在 retrieving delay 上明显优于若干 DDPG 变体和 greedy caching。
- 与 SCA 基线相比，性能接近，但决策速度更快，更适合动态场景。
- 还可视化了不同用户移动模式下的 UAV 轨迹。

实验能够支撑“分解混合动作空间有助于学习效率”的结论，但因为没有计算任务执行模型，它对“通信-计算联合资源分配”的支撑是缺位的。

## 6. Strength
- NOMA 通信模型写得比较完整，干扰项、SIC 顺序和复用约束都较清晰。
- 双时间尺度拆分较自然，适合动态内容热度场景。
- 对混合动作空间的处理思路有参考价值：matching 负责离散部分，DDPG 负责连续部分。
- 路径规划与通信资源分配之间的耦合关系比较明确。

## 7. Weakness
- 没有计算模型，因此并不回答“通信与计算如何协同分配”。
- 研究目标仍是内容获取时延，不是任务完成效果，更不是任务语义保持。
- 强依赖 HAPS + cloud 的分层架构，系统假设较理想化。
- 轨迹规划虽然是 3D，但速度被固定，动作空间仍做了明显简化。
- 多 UAV 协同主要体现在缓存共享与信道复用，不涉及协同感知、协同推理或异构算力执行。

## 8. Reusable Part
- NOMA SINR 与子信道复用建模方式可直接借鉴。
- “双时间尺度分解”很适合写 resource allocation 类工作。
- many-to-one matching 处理离散信道复用变量的思路可复用。
- 把轨迹规划与通信速率/时延挂钩的建模逻辑可以迁移到其他 UAV 网络问题。

## 9. Attack Point
- 将“内容缓存/获取”替换成“任务执行/任务语义完成”，构造更任务导向的目标。
- 在现有通信模型上补入计算模型、排队模型和 CPU 资源约束。
- 从 NOMA 通信收益进一步扩展到“感知-通信-推理”全链路优化。
- 引入异构 UAV 算力与多边缘节点，而不是只做缓存协作。
- 将当前以 hit ratio 和 retrieving delay 为核心的代理指标，扩展为任务完成率、任务收益或语义保持度。

## 10. Relation to My Topic
这篇论文补的是“多 UAV 通信侧资源分配与轨迹规划”这一环，特别适合支撑你后续关于 `NOMA/子信道复用/功率控制/轨迹耦合` 的 related work 或 baseline 选择。

但它忽略了当前主线最关键的几项：
- 没有任务导向优化
- 没有计算资源建模
- 没有异构算力协同
- 没有多模态语义

因此，这篇论文更适合作为“通信导向资源分配基线”，而不是“多无人机任务导向通信”的直接方法参考。

## 证据完整性说明
- 本卡片基于 PDF 正文整理，不是摘要复述。
- 已直接使用正文中的双时间尺度、NOMA 通信模型、delay 表达、分解策略和 DRL/Matching 机制。
- 仓库中未发现该论文对应的 `notes/` 或 annotation notes，因此“notes 联合核验”当前无法完成。
