# 2025 Zhang - Resource Allocation and Trajectory Optimization in Multi-UAV Collaborative Vehicular Networks: An Extended Multiagent DRL Approach

## 基本信息
- 标题：Resource Allocation and Trajectory Optimization in Multi-UAV Collaborative Vehicular Networks: An Extended Multiagent DRL Approach
- 作者：Wenqian Zhang, Lu Tan, Tao Huang, Xiaowen Huang, Mengting Huang, Guanglin Zhang
- 年份：2025
- 来源：IEEE Internet of Things Journal, vol. 12, no. 8, pp. 9391-9402
- DOI：10.1109/JIOT.2024.3492953
- 本地 PDF：`papers/UAV-Resource-Alloaction/Zhang 等 - 2025 - Resource Allocation and Trajectory Optimization in Multi-UAV Collaborative Vehicular Networks An Ex.pdf`

## 相关性 / 标签
- 相关性等级：高相关
- 子方向标签：资源分配与调度；路径规划；边缘智能 / 空地协同
- 判断理由：论文围绕多 UAV 车辆网络中的轨迹、带宽资源和任务卸载做联合设计，还显式建立了通信、排队和外部服务器卸载模型。它比纯通信类工作更接近“通信-计算耦合”，但仍不涉及任务语义和多模态协同。

## 1. Problem
论文研究道路 RSU 不可用或受损时，多 UAV 如何为车辆提供接入和边缘计算服务。核心问题是：在车辆高速移动、任务动态到达、UAV 计算资源有限且可借助外部服务器辅助计算的条件下，如何通过 UAV 轨迹规划、频谱资源分配和动态数据卸载，最小化车辆任务平均完成时间并满足 QoS。

按当前主线分类，这篇论文更偏向：
- 资源分配不合理
- 传输效率不足
- 推理实时性不足

## 2. Setting / Assumptions
- 场景为三层架构：vehicles + multiple UAVs + accessible servers。
- 场景是一段单向道路，RSU 不可用，多架 UAV 沿道路部署。
- UAV 以固定高度飞行，只在道路方向的一维水平位置上移动。
- 车辆与 UAV 间主要采用 LoS 通信。
- 频谱接入采用 OFDMA，上行多信道，UAV 对服务车辆正交分配带宽，无同信道干扰建模。
- 每架 UAV 每个时隙最多服务 `N` 辆车。
- 车辆把任务数据上传到 UAV 后，UAV 一部分本地处理，一部分可继续转发给其他 accessible servers。
- UAV 本地队列遵循 FIFO。
- 外部服务器的处理时间 `τ_c` 与往返传输时间 `τ_r` 被视为常数。
- 多 UAV 之间的协同主要体现在空间协作与共享奖励，而不是显式的 UAV-UAV 任务交换链路。

## 3. Core Idea
论文的核心思想是把“多 UAV 连续运动 + 连续卸载 + 离散资源分配”的混合优化问题拆成可执行的多智能体学习框架。

其中，UAV 的移动动作和对外部服务器的卸载比例是连续变量，适合由 MADDPG 学习；而车辆归属与带宽分配带有更强的离散结构，则通过启发式 clustering 和 DBA（dynamic bandwidth allocation）算法实现。也就是说，作者没有把全部变量都塞进一个统一优化器，而是用“RL 学连续决策 + 规则法做离散资源编排”的组合方式控制复杂度。

## 4. Key Mechanism

### 4.1 通信模型
- 第 `j` 架 UAV 与第 `i` 辆车的距离：
- `d_(i,j)(t) = sqrt((x_i^u(t) - x_j(t))^2 + H^2)`
- 信道增益：
- `g_(i,j)(t) = h0 / d_(i,j)(t)^2`
- UAV 使用 OFDMA 上行接入，对服务车辆正交分配带宽。
- 若第 `j` 架 UAV 当前服务 `|ξ_(i,j)(t)|` 辆车，则每辆车分得的带宽是 `b_(i,j)(t) = B_j^max / |ξ_(i,j)(t)|`。
- 速率模型：
- `R_(i,j)(t) = b_(i,j)(t) log2(1 + g_(i,j)(t) p_i / (b_(i,j)(t) N0))`
- 因此，轨迹位置 `x_j(t)` 会通过距离直接影响信道增益与上行速率。

### 4.2 计算模型
- 车辆 `i` 在时隙 `t` 的待上传任务大小记为 `D_i^u(t)`。
- UAV `j` 接收到的总数据量：
- `D_j^r(t) = Σ_i ρ_(i,j)(t) min(R_(i,j)(t)δt, D_i^u(t))`
- UAV `j` 将比例 `β_j(t)` 的新到达数据卸载给 accessible servers，剩余 `1-β_j(t)` 保留本地处理。
- 本地未处理队列 `D_j^c(t)` 更新：
- `D_j^c(t+1) = D_j^c(t) + [1-β_j(t)]D_j^r(t) - δt C_j / Z`
- 其中 `C_j` 是 UAV 计算能力，`Z` 是每比特所需 CPU cycles。
- 计算完成时间：
- 本地处理时间 `D_j^c(t) / C_j`
- 外部服务器处理时间 `(τ_c + τ_r) β_j(t) D_j^r(t)`
- 实际计算时间取二者最大值 `T_j^c(t) = max(本地时间, 外部时间)`
- 最终平均完成时间：
- `T_ave(t) = (1/I) Σ_i T_i^up(t) + (1/J) Σ_j T_j^c(t)`

### 4.3 优化变量与约束
- `x_j(t)`：UAV 水平位置 / 轨迹状态
- `β_j(t)`：卸载到 accessible servers 的比例
- `b_(i,j)(t)`：给车辆的带宽
- `ρ_(i,j)(t)`：是否为车辆分配子信道
- 目标：最小化长期平均 `T_ave(t)`
- 关键约束：
- `β_j(t) ∈ [0,1]`
- `ρ_(i,j)(t)` 为二元变量
- UAV 间距离不小于 `d_min`
- 单时隙位移不超过 `V_j^max δt`
- 每 UAV 最多服务 `N` 辆车
- 所有已分配子信道带宽之和等于 UAV 可用总带宽 `B_j^max`

### 4.4 多约束不等式的处理方式
- 原问题被识别为 mixed integer nonlinear program。
- 作者认为若把离散与连续变量全部统一离散化后交给 DRL，会带来维度爆炸和性能问题。
- 因此，采用“问题分治”：
- `MADDPG`：学习连续变量 `α_j(t)`（运动）和 `β_j(t)`（卸载）
- `Clustering Algorithm`：基于空间距离为每个 UAV 确定服务车辆集合
- `DBA Algorithm`：按车辆待上传数据大小排序，决定哪些车获得服务，以及如何分配带宽
- 奖励函数同时考虑平均传输/计算时延和安全/越界惩罚，借此把约束软化进学习过程。

### 4.5 路径规划如何与资源分配结合
- UAV 轨迹变化后，车辆到 UAV 的距离改变，信道增益和上行速率随之变化。
- 轨迹变化还会改变车辆归属集合 `ξ_(i,j)(t)`，进而影响每辆车可分得的带宽 `b_(i,j)(t)`。
- 带宽和速率又影响新数据到达量 `D_j^r(t)`，进而影响本地队列与是否需要向外部服务器卸载。
- 所以，它把轨迹、带宽分配、卸载决策通过 `distance -> rate -> received load -> queue/computation delay` 这一链条串联起来。

## 5. Experiments
- 与单智能体 `DDPG` 比较累计奖励与收敛性，MADDPG 收敛更快、稳定值更优。
- 轨迹规划效用实验：与 `Random Move UAV`、`Static UAV`、`DDPG-based` 策略比较。
- 带宽分配效用实验：比较带/不带 `DBA` 的方法。
- 卸载效用实验：比较 `Executing All at UAVs`、`Executing All at Accessible Servers` 与动态卸载策略。
- 指标主要包括：
- 平均完成时间 `T_ave(t)`
- 任务完成率
- 收敛曲线
- 不同车流密度、带宽资源、算力资源下的鲁棒性
- 结果上：
- 在车辆密度增大时，MADDPG 方案比静态 UAV 可最多降低约 `50%` 的平均完成时间。
- DBA 在子信道稀缺时显著改善完成时间与完成率。
- 动态卸载在算力受限时优于“全本地”或“全外部”两种极端策略。

实验较完整地支撑了“轨迹 + 通信 + 外部卸载”联合设计的必要性，但仍停留在仿真级验证。

## 6. Strength
- 明确建立了通信、排队、计算和外部服务器卸载之间的耦合关系。
- 对轨迹规划、DBA、外部卸载三部分都做了独立效用实验，实验结构清晰。
- 多 UAV 协同体现在共享奖励和空间协作上，较单 UAV 方案更接近系统级问题。
- 用 `MADDPG + clustering + DBA` 的组合控制了混合动作空间复杂度。

## 7. Weakness
- 资源分配并非统一最优求解：车辆聚类和 DBA 属于启发式规则，而不是与轨迹/卸载共同优化。
- 场景被简化为单向道路、一维轨迹、固定飞行高度，泛化到更复杂 2D/3D 空域还需验证。
- 通信模型采用 OFDMA 且基本忽略干扰协同，比 NOMA 类建模更简单。
- 多 UAV 之间没有显式的空空链路与任务转发模型，协同强度有限。
- 目标仍是平均完成时间和 QoS，不涉及任务语义或更高层任务收益。

## 8. Reusable Part
- `distance -> rate -> queue -> completion time` 这条建模链条可以直接借鉴。
- UAV 本地队列与外部服务器辅助计算的耦合模型很适合作为资源约束写法参考。
- 将混合问题拆成 RL 与启发式模块的方式，对复杂系统设计有现实参考价值。
- 不同资源瓶颈下分开展示实验效应的写法可用于后续实验设计。

## 9. Attack Point
- 从启发式 DBA 升级到真正的联合优化或可学习离散资源分配。
- 从一维道路场景扩展到更一般的二维/三维多 UAV 协同采集与服务。
- 引入显式 UAV-UAV 协作链路与异构边缘节点建模。
- 用任务成功率、语义价值或下游任务完成效果替代单纯平均时延目标。
- 把车辆任务从“数据大小驱动”升级为“任务语义驱动”的建模范式。

## 10. Relation to My Topic
这篇论文补的是“多 UAV 场景下，路径规划如何通过通信速率和队列负载影响任务完成时间”这一环。对于你后续研究里需要写“轨迹-通信-计算耦合”的建模部分，它是很有参考价值的前置工作。

但它没有覆盖你当前主线里更关键的任务：
- 没有任务导向/语义导向目标
- 没有多模态语义
- 没有多视角协同感知
- 多 UAV 之间缺少显式协同推理与异构执行机制

因此，它适合做“车辆网络中的多 UAV 资源调度基线”和“路径规划如何嵌入资源分配”的参考，而不是你主线问题的终点。

## 证据完整性说明
- 本卡片基于 PDF 正文整理，不是摘要复述。
- 已直接使用正文中的通信模型、队列更新、计算时间模型、优化问题和 MADDPG/DBA 机制。
- 仓库中未发现该论文对应的 `notes/` 或 annotation notes，因此“notes 联合核验”当前无法完成。
