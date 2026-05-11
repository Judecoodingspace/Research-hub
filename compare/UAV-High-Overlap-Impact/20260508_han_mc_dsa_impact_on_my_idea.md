# Han 2026 MC-DSA 对当前 idea 的冲击评估

## 1. 评估对象

- 相似论文：Design of Multi-UAV Cooperative Deep Semantic Autoencoders for Communication Networks
- 对应 papercard：papercard/UAV-Semantic-Communication/2026_Han_MC_DSA_Multi_UAV_Cooperative_Deep_Semantic_Autoencoders.md
- 当前论文主线文件：codex_high_overlap_impact_task_experiment_mainline.md
- 已读取的 compare / gap / writing_support 文件：
  - compare/UAV-High-Overlap-Impact/：目录存在，但当前未发现既有比较文件
  - gap_map/UAV-Multi-Model/task_oriented_comm_gap.md
  - writing_support/：当前仅发现 UAV-Fire-Detection 主题材料，未纳入本评估
- 其他已读取文件：
  - Agents_optimized.md
  - metadata/2026-5-7_UAV-Semantic-Communication.csv
  - papercard/UAV-Semantic-Communication/index.md
- notes 状态：仓库中未发现 notes/ 目录；本评估主要基于 papercard、metadata 与已完成 PDF 正文分析
- 评估日期：2026-05-08

## 2. 执行摘要

- Han 2026 对当前 idea 构成真实高相关威胁，但不是完全撞题。它已经覆盖了多 UAV、任务导向语义通信、按需协作、语义源选择、特征传输以及带宽 / 时延 / 能耗评价。
- 最大重合点是：两者都反对 all-to-one / always-on 协作，都强调协作应由任务收益与通信代价共同约束，并允许在不需要协作时保持本地执行。
- 最关键的实质差异是：Han 2026 的动作主要是“选择哪些 S-UAV 上传语义特征”，而当前工作是 `none / B2_RECALL / B3_TUNED` 多动作语义协作 selector，并显式建模 precision-recall-F1 trade-off、latency / payload / queue / pair cost 和 image-level gain prediction。
- Han 2026 的 source selection 是 image-dependent 的 query-key 语义匹配，但不是当前意义上的 action-specific utility prediction；它没有区分 recall-first 与 balanced action，也没有显式处理 false trigger、safe guard、LOSO unseen degradation 或 DroneVehicle 外部验证。
- 当前论文不能再强说“首次提出多 UAV 任务导向语义协作”或“首次实现按需语义通信”；这些应让位给 Han 2026 等前置工作。
- 当前论文最稳的核心卖点应收缩为：面向 UAV 车辆检测任务的代价感知多动作条件式语义协作选择，以及从场景级查表推进到图像级增益预测时暴露出的收益 / 安全边界。
- 最需要补强的是：把 Han 2026 作为核心 Related Work，增加 MC-DSA-style source selection / always-on / random collaboration 的对比定位，并把 latency、payload、queue、false-trigger、unseen blur/fog、external DroneVehicle 的证据链补完整。

## 3. 真正重合点

### 3.1 问题定义重合

Han 2026 与当前工作都不是纯链路层通信优化，而是把通信选择放到下游视觉任务中评估。Han 2026 的目标是提升 T-UAV 端语义分割性能并减少冗余传输；当前工作的目标是提升 UAV 车辆检测任务中的检测效用，并判断是否触发语义协作动作。

真实重合点在于：二者都把“是否协作”从默认开启的系统模块，转化为任务相关的条件决策。Han 2026 通过 task query 与 S-UAV key 的语义相似度决定通信链路是否建立；当前工作通过 predicted quality gain、precision penalty、latency 和 payload cost 决定是否从 `none` 转向某个协作动作。

但两者的问题粒度不同。Han 2026 更像“多 UAV 语义源选择与特征上传框架”；当前工作更像“车辆检测任务中的多动作协作触发与效用选择器”。因此，关键词高度重合，但研究问题没有完全重叠。

### 3.2 系统设定重合

Han 2026 采用 1 个 Task UAV 与多个 Support UAV 的多 UAV 协同结构，S-UAV 向 T-UAV 上传语义特征，T-UAV 端完成分割。当前工作同样处在 UAV 语义协作与后端辅助推理语境中，并关心 A2A 链路、pair-level receiver selection、queue delay、payload 和时延代价。

重合处包括：

- 多 UAV / UAV collaboration 场景；
- 任务导向语义通信，而不是单纯原始数据传输；
- local-only / no-support 情况具有明确意义；
- 协作对象或协作动作不是越多越好；
- 语义特征 / proposal-rich backend augmentation 的传输代价会影响是否协作。

差异在于：Han 2026 的 receiver 是固定 T-UAV，S-UAV 是候选 source；当前主线更强调前后端 pair、接收节点状态、队列占用和不同 backend action 的条件选择。Han 2026 还假设轨迹固定、同步多视角数据可得，未展开真实空空链路调度和异构算力。

### 3.3 动作空间重合

Han 2026 存在隐式 `standalone` 与 `cooperative` 两类状态：当没有 S-UAV 被选中时，T-UAV 单独分割；当一个或多个 S-UAV 被选中时，上传语义特征并融合。因此它确实覆盖了 trigger / no-trigger 的一部分。

但它的动作空间主要是：

- 选择哪些 S-UAV 参与；
- 由阈值 `sth` 控制协作组规模；
- 对选中 source 的特征加权融合。

当前工作的动作空间是：

- `none / local_only`；
- `B2_RECALL`；
- `B3_TUNED`。

这里的核心差异是：当前工作不是只决定“谁上传”，而是决定“是否协作以及采用哪种语义协作动作”。`B2_RECALL` 与 `B3_TUNED` 对应不同的任务收益偏好，分别服务 recall-first 与 balanced operating region。Han 2026 没有等价的多动作质量偏好建模。

### 3.4 代价建模重合

Han 2026 显式统计 payload、带宽需求、计算时延、传输时延和能耗，并在实验中报告不同协作规模与信道条件下的资源开销。这与当前工作中的 latency / payload cost sensitivity 有明显重合。

但 Han 2026 的资源模型更接近后验评价和阈值控制，而不是把代价直接写入每帧动作 utility。当前工作将代价放入 selector：

```text
utility =
    predicted_delta_quality
  - precision_penalty_weight * max(0, -delta_precision)
  - lambda_latency * pair_extra_latency_ms
  - lambda_payload * extra_payload_bytes
```

因此，当前工作可以声称更强调 cost-aware decision boundary，但不能声称 Han 2026 没有考虑通信代价。更准确的区别是：Han 2026 有资源开销建模与阈值敏感性，当前工作把代价嵌入 action-level utility 与 trigger decision。

### 3.5 决策机制重合

Han 2026 使用 query-key 语义匹配和阈值门控，是一种 learned semantic source selector。它与当前工作中的 image-level state / gain prediction 有相似外观：二者都试图根据当前输入状态决定是否协作。

关键差异在于：

- Han 2026 预测的是 task query 与 candidate source 的语义相关性；
- 当前工作预测的是某个协作动作相对 local-only 的任务效用增益；
- Han 2026 的阈值主要控制 source participation；
- 当前工作需要在多个动作之间比较 utility，并允许因为 precision penalty、payload 或 latency 转为 `none`。

因此，Han 2026 是当前工作强相关的前置机制，但不能直接覆盖当前的 action-specific gain predictor、hybrid visual + YOLO latent selector 和 safety guard。

### 3.6 实验目标重合

两者都关注任务精度与系统效率的共同评价。Han 2026 报告 OAcc、mAcc、FWIoU、mIoU、带宽、时延、能耗和信道鲁棒性；当前工作关注 precision、recall、F1、small-object recall、trigger rate、latency、payload、queue / pair cost、LOSO 与外部数据集表现。

真正重合的是“任务效果 + 传输代价”这一评价逻辑。差异在于 Han 2026 的视觉任务是语义分割，当前工作是车辆检测；Han 2026 的鲁棒性更偏信道条件和协作规模，当前工作更偏 degradation regime、false trigger、unseen blur/fog 与 external-domain validation。

## 4. 关键差异

### 4.1 表面差异

以下差异存在，但单独不足以支撑创新性：

- Han 2026 做语义分割，当前工作做车辆 / 目标检测。
- Han 2026 使用 MC-DSA、Swin Transformer / RSTB 与 semantic autoencoder，当前工作使用 YOLO 检测统计、YOLO latent 和 backend action。
- Han 2026 使用 AirSim-SRMS 仿真多视角分割数据，当前工作使用 VisDrone synthetic degradation 与 DroneVehicle 外部验证。
- Han 2026 通过 query-key 相似度阈值控制协作，当前工作通过 utility 或 classifier 选择动作。
- Han 2026 更像通信网络论文，当前工作更像任务效用驱动的检测协作 selector。

这些差异有助于说明应用边界，但如果当前论文只停留在“换任务、换模型、换数据集”，审稿人仍可能认为本质上只是 MC-DSA-style selective semantic collaboration 的变体。

### 4.2 实质差异

真正能支撑创新性边界的差异主要有六个。

第一，当前工作有明确的多动作协作空间。Han 2026 选择的是协作 source 集合，而当前工作在 `none / B2_RECALL / B3_TUNED` 中选择，每个动作对应不同任务收益偏好。

第二，当前工作显式建模 precision-recall-F1 trade-off。Han 2026 主要报告分割精度指标，没有 action-level precision penalty，也没有讨论 recall-first action 与 balanced action 的 operating region。

第三，当前工作把 latency、payload、queue、pair-level receiver state 放进动作效用。Han 2026 有带宽、时延、能耗统计，但未形成 queue-aware / pair-aware 的 per-action utility selector。

第四，当前工作强调 image-level gain prediction，而不是只做语义相关性 source selection。Han 2026 的 query-key 匹配能做图像依赖选择，但它没有预测每个协作动作对当前图像的 delta F1、delta recall 或 harmful collaboration 风险。

第五，当前工作系统分析 high-utility predictor 与 safe trigger 的张力。Han 2026 没有展开 false trigger、over-trigger、abstention guard、B2-to-B3 downgrade 或 conservative policy 的机会损失。

第六，当前工作把 unseen-regime / external-domain 作为论文边界的一部分。Han 2026 评估 AWGN、Rician、Rayleigh 与 SNR，但未验证 held-out degradation、continuous blur/fog 或 DroneVehicle 这类真实 UAV 外部数据集。

### 4.3 哪些差异可以支撑创新性边界

可以支撑创新性边界的差异包括：

- 从 semantic source selection 推进到 multi-action semantic collaboration selector；
- 从 query-key relevance 推进到 action-specific task utility prediction；
- 从“协作能提升分割”推进到“何时 B2_RECALL、何时 B3_TUNED、何时 none”；
- 从资源开销统计推进到 cost-sensitive trigger boundary；
- 从 aggregate task gain 推进到 false-trigger / safe guard / opportunity loss 的安全边界分析；
- 从 seen simulation / channel robustness 推进到 LOSO degradation、continuous blur/fog 与 external DroneVehicle validation。

这些差异都能与当前实验主线直接对应，因而比模型结构或数据集差异更稳。

### 4.4 哪些差异不足以支撑创新性

不足以单独支撑创新性的差异包括：

- 仅强调当前任务是 vehicle detection，Han 是 semantic segmentation；
- 仅强调当前用 YOLO，Han 用 semantic autoencoder；
- 仅强调当前数据集不同；
- 仅强调当前有 degradation scenario，而 Han 有 channel condition；
- 仅强调当前不使用 query-key 网络。

这些差异如果没有连接到多动作 utility、precision-recall trade-off、cost-sensitive selector、image-level gain prediction 和 safety boundary，会被审稿人视为工程迁移，而不是研究贡献。

## 5. 对当前论文创新性的威胁

### 5.1 审稿人可能的攻击方式

审稿人最可能提出以下攻击：

- Han 2026 已经提出多 UAV 任务导向语义通信框架，并通过 task query 与 source selection 实现 when2com / who2com / what-to-transmit；当前论文是否只是把类似选择机制换到车辆检测？
- Han 2026 已经证明无关多视角信息会浪费带宽甚至损害任务性能；当前论文关于“不是 always-on、需要选择协作”的动机是否已经被充分覆盖？
- Han 2026 已经评估带宽、时延、能耗与分割性能；当前论文的 cost-aware claim 是否只是同类指标的重新组合？
- Han 2026 已经有 standalone 与 cooperative 对比、random select 与 random fusion baseline；当前论文是否缺少与这类 selective semantic communication baseline 的直接区分？
- 如果当前论文声称“任务导向多 UAV 语义协作选择”是主要创新，Han 2026 会构成强前置工作，迫使当前论文把创新重心转到多动作 selector、utility calibration 和安全边界。

### 5.2 不能再强说的 claim

当前论文不应再强说：

- 首次提出多 UAV 任务导向语义通信；
- 首次提出多 UAV 按需协作 / when2com；
- 首次证明多视角协作不应 always-on；
- 首次将语义特征传输与任务效果联合评价；
- 首次考虑语义通信中的带宽、时延和能耗；
- 已经覆盖完整多 UAV source selection 问题；
- 当前 selector 已经解决真实在线部署中的所有状态估计和 OOD 泛化问题。

### 5.3 需要降级或改写的表述

建议将强 claim 改写为更窄、更稳的表述：

- 将“多 UAV 语义通信选择机制”改为“面向 UAV 车辆检测任务的多动作条件式语义协作 selector”。
- 将“按需协作”改为“在已有 selective semantic collaboration 思路基础上，进一步区分 recall-first、balanced 与 local-only action 的任务效用边界”。
- 将“代价感知语义通信”改为“将 latency、payload、queue / pair state 与 precision-recall-F1 trade-off 显式纳入 action utility”。
- 将“在线自适应协作”改为“从 scenario-level lookup 迈向 image-level gain prediction，并揭示 high-utility predictor 与 safe trigger 之间的张力”。
- 将“鲁棒在线选择器”改为“在 LOSO、continuous blur/fog 与外部 DroneVehicle 中评估 selector 的泛化风险和安全边界”。

### 5.4 Related Work 中必须补入的位置

Han 2026 应进入 Related Work 的核心段落，而不是放在外围通信背景中。建议位置如下：

- 在“Task-oriented / semantic communication for UAV networks”段落中，用它说明多 UAV 语义通信已经开始通过 task query 与 source selection 抑制冗余传输。
- 在“Selective collaboration / when-to-communicate”段落中，用它作为正面前置工作，说明选择谁通信与传语义特征已经被研究。
- 在当前方法引出段中明确区别：Han 2026 主要解决 task-query-driven source selection for semantic segmentation，而本文关注 cost-aware multi-action collaboration selection for UAV vehicle detection。
- 在实验对比段中把 Han 2026 启发的 baseline 写成一类：standalone、always-on / all-support、random support、threshold-based semantic/source selection、current multi-action selector。

## 6. 可直接利用的信息

### 6.1 问题定义方式

可以直接借鉴 Han 2026 的三段式问题拆解：

- 单 UAV 视角可能不足，需要多视角互补；
- all-to-one / all-support 上传会带来冗余和噪声；
- 协作应由下游任务语义决定，而不是由链路可用性或节点数量直接决定。

但不能照搬为当前论文主问题。当前论文应在此基础上进一步强调：即便确定存在可协作后端，也仍需要选择何种协作动作，并在 recall、precision、F1 与系统代价之间做条件式取舍。

### 6.2 系统模型 / 变量 / 目标函数

可借鉴内容：

- Task UAV / Support UAV 的角色划分；
- task query 与 candidate source representation 的思想；
- 被选中节点数量决定 payload、带宽、时延和能耗的建模方式；
- standalone 与 cooperative 分支的系统图组织；
- 阈值 `sth` 作为协作强度控制变量。

只能参考、不能直接照搬的内容：

- query-key 网络结构。如果当前工作直接采用类似 query-key source selector，却不加入多动作 utility 和 safety analysis，会增加撞题风险。
- semantic autoencoder + segmentation decoder 的端到端结构。当前工作更适合作为 detection collaboration selector，不应被改写成完整语义通信 autoencoder。
- 固定 T-UAV receiver 假设。当前主线若强调 pair-level / queue-aware receiver selection，应保持这一差异。

### 6.3 Baseline 设计

Han 2026 中值得借鉴的 baseline 组织包括：

- standalone / local-only；
- cooperative / selected support；
- random select；
- random fusion / all-support；
- 不同 encoder 或不同协作规模对比；
- 不同阈值下的性能与资源变化。

当前工作可以对应设计为：

- `none / local_only`；
- always-on `B2_RECALL`；
- always-on `B3_TUNED`；
- random action selector；
- oracle scenario-level selector；
- threshold-based gain selector；
- learned visual / latent / hybrid selector；
- guard 后的 safe selector。

其中，random source / all-support 的思想可以借鉴，但如果当前数据结构不是严格多视角 source selection，应写成“MC-DSA-style selective collaboration baseline”，不要伪装成完全复现 Han 2026。

### 6.4 实验组织方式

可借鉴的实验组织：

- 同时报告任务指标与系统指标；
- 做阈值敏感性分析，展示协作强度从保守到激进的变化；
- 做协作规模分析，证明更多协作者不必然更好；
- 加入随机选择 / 随机融合负例，支撑“选择机制必要”；
- 使用可视化展示何时 local-only、何时触发 support。

当前工作应对应强化：

- `precision_penalty_weight` 对 action region 的影响；
- `lambda_latency`、`lambda_payload`、queue delay 对 trigger rate 的影响；
- `B2_RECALL` 与 `B3_TUNED` 在不同 degradation / external domain 下的分工；
- false trigger / harmful collaboration case study；
- continuous blur/fog 下 guard 是否过拟合固定 scenario；
- DroneVehicle 上 recall recovery 与 precision 损失。

### 6.5 Related Work 叙述逻辑

Han 2026 可用于组织如下 related work 逻辑：

1. 传统 UAV 通信关注链路可靠性和吞吐，不直接面向视觉任务。
2. 语义通信把传输对象从比特推进到任务相关特征。
3. 多 UAV 协同进一步要求区分有用 source 与冗余 source，Han 2026 代表了 task-query-driven selective semantic collaboration。
4. 现有 source selection 工作仍主要回答“谁传特征”，而当前论文关注“是否触发以及触发哪种协作动作”，并把 precision-recall-F1、latency、payload、queue 和 image-level gain prediction 放进同一选择问题。

这一逻辑能保护当前论文的边界，也能避免把 Han 2026 写成普通背景文献。

## 7. 当前工作暴露出的缺口

### 7.1 缺少的实验

必须补或必须在论文中明确呈现的实验：

- Han-style baseline 定位实验：至少需要把 standalone、always-on collaboration、random action / random support、oracle selector、learned selector 放在同一张表或同一组曲线中，说明当前方法不是简单 selective collaboration。
- action region 实验：需要展示 `B2_RECALL`、`B3_TUNED`、`none` 在不同 precision penalty、latency、payload 下的转移，而不只报告最终 F1。
- false-trigger 诊断：需要列出当前 selector 在 `blur_heavy`、weak `fog` 等高风险场景中过触发的比例、损失和 guard 后变化。
- continuous blur/fog 验证：需要证明 guard 不是对离散 scenario label 的过拟合。
- DroneVehicle 外部验证：需要把 n=20 smoke 与 n=100 或更大规模正式验证区分清楚，避免把校准实验写成最终结论。

可以补强但不一定作为主线的实验：

- threshold-based source / action selector，与 learned utility predictor 对比；
- queue delay 与 pair-level receiver state 的单独消融；
- payload 压缩率或 proposal size 对 utility boundary 的影响；
- backend busy / link quality 的 stress test。

### 7.2 缺少的对比

当前论文需要补清楚三类对比：

- 与 Han 2026 这类 selective semantic source communication 的概念对比：它解决 who-to-communicate，当前解决 multi-action trigger-and-select。
- 与 always-on backend augmentation 的效果对比：证明当前 selector 的价值来自条件选择，而不是 backend 本身。
- 与 scenario-level oracle / lookup 的对比：证明 image-level predictor 的必要性，同时承认 label-free selector 在 unseen regime 下仍有风险。

如果这些对比缺失，审稿人容易把当前论文理解为“在 Han 2026 的选择协作框架上换了检测任务和特征类型”。

### 7.3 缺少的建模说明

需要补强的建模说明包括：

- 为什么 `B2_RECALL` 与 `B3_TUNED` 是两个实质不同的协作动作，而不是同一 backend 的参数变体。
- 为什么 precision penalty 应进入 utility，尤其是 recall-first action 可能带来 false positive 的风险。
- latency、payload、queue delay 和 pair-level receiver state 如何进入同一动作效用，而不是只作为后验指标。
- image-level gain prediction 与 degradation classification 的区别：当前目标不是识别退化类型，而是预测某个动作是否会带来正 utility。
- guard 的定位：它是 safety mechanism，不是无损 utility improvement mechanism。

### 7.4 缺少的写作支撑文献

除 Han 2026 外，还需要继续补的文献类型包括：

- UAV / autonomous driving collaborative perception 中的 when2com / who2com / selective communication 文献；
- task-oriented semantic communication 中直接使用 downstream utility 的文献；
- collaborative inference / split computing 中显式建模 feature payload 与 latency 的文献；
- OOD / uncertainty / calibration for selective prediction 或 safe triggering 文献；
- external UAV vehicle detection dataset 与 domain gap 相关文献。

这些文献不是为了堆 related work，而是为了支撑当前论文的四个关键边界：多动作选择、任务 utility、系统代价、安全泛化。

## 8. 当前论文定位调整建议

### 8.1 应收缩的 claim

建议收缩以下 claim：

- 从“提出多 UAV 语义通信协作框架”收缩为“提出 UAV 车辆检测中的条件式多动作语义协作 selector”。
- 从“解决按需语义通信问题”收缩为“在已有按需语义通信和 source selection 工作基础上，研究多动作协作收益与系统代价之间的选择边界”。
- 从“实现在线鲁棒协作”收缩为“探索 image-level online gain prediction，并揭示其在 unseen blur/fog 与 external domain 下的安全边界”。
- 从“综合优化感知-通信-推理”收缩为“以 one-step contextual decision baseline 形式建模感知收益、传输代价与后端协作动作选择”。

### 8.2 应保留的核心卖点

当前论文仍可保留的核心卖点是：

- 条件触发式语义协作，而不是 always-on backend fusion；
- `none / B2_RECALL / B3_TUNED` 多动作 selector，而不是单一 source selection；
- 显式 precision-recall-F1 trade-off，尤其是 recall-first action 的 precision risk；
- latency / payload / queue / pair-level cost 进入 action utility；
- 从 scenario-level lookup 走向 image-level gain prediction；
- 系统比较 visual features、learned degradation state、YOLO latent 与 hybrid predictors；
- 正视 high-utility predictor 与 safe trigger 的张力；
- 使用 LOSO、continuous blur/fog 和 DroneVehicle 外部验证来定义泛化边界。

### 8.3 应补强的证据链

建议把证据链组织成四层：

第一层：证明协作不是 always useful。用 `none`、always-on `B2_RECALL`、always-on `B3_TUNED`、random action 和 oracle selector 对比，展示 harmful collaboration 与边界场景。

第二层：证明多动作有必要。展示 `B2_RECALL` 与 `B3_TUNED` 在 recall、precision、F1、小目标召回和 cost 下的不同 operating region。

第三层：证明代价会改变选择。用 latency、payload、queue / pair cost sensitivity 展示 action boundary 如何移动。

第四层：证明在线预测有收益但不完全安全。用 visual、latent、hybrid、guard、LOSO、continuous blur/fog 和 DroneVehicle 外部验证呈现“收益与安全边界”。

### 8.4 更稳妥的论文定位表述

更稳妥的中文定位是：

> 本文研究面向 UAV 车辆检测任务的条件式语义协作选择问题。不同于已有多 UAV 语义通信工作主要围绕任务 query 选择相关语义源，本文进一步将协作建模为一个代价感知的多动作选择过程：系统需要在本地检测、召回优先的后端复核以及平衡型后端增强之间进行选择，并显式考虑任务效用、precision-recall-F1 权衡、A2A / 队列 / 载荷 / 时延代价。进一步地，本文从场景级查表推进到图像级增益预测，比较视觉状态、检测器中间特征与混合状态表征，并分析 high-utility policy 与 safe trigger 在未见 blur/fog 及外部 UAV 数据集上的边界。

更稳妥的英文定位是：

> This work studies conditional semantic collaboration for UAV-based vehicle detection. In contrast to prior multi-UAV semantic communication frameworks that mainly select task-relevant semantic sources, we formulate collaboration as a cost-aware multi-action decision problem. The selector decides whether to remain local, invoke a recall-first backend review, or trigger a balanced backend augmentation, while explicitly accounting for task utility, precision-recall-F1 trade-offs, A2A/queue/payload/latency costs, and image-level gain prediction. The experiments further characterize both the utility capture and safety boundary of visual, detector-latent, and hybrid selectors under unseen blur/fog regimes and external UAV-domain validation.

## 9. 接下来最值得补的 3 个动作

1. 补一个“Han 2026 / MC-DSA-style selective semantic communication”对比定位表：按问题定义、动作空间、代价建模、状态表征、实验验证五列比较 Han 2026 与当前方法，放入 Related Work 或 Introduction 后半段。
2. 补强多动作与代价敏感实验：用同一组图表展示 `precision_penalty_weight`、latency、payload、queue / pair cost 如何改变 `none / B2_RECALL / B3_TUNED` 的动作分区，明确当前方法不是单一 trigger 或 source selector。
3. 完成安全与外部验证证据：整理 LOSO、continuous blur/fog、guard false-trigger analysis 和 DroneVehicle n=100 结果，把“latent / hybrid 有效但需要 guard”的结论写成边界，而不是夸成已解决 robust online selection。
