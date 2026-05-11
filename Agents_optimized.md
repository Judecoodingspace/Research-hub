# AGENTS.md

## 目标
本仓库用于支持以下科研任务：

1. 面向多无人机协同场景的文献筛选与精读
2. 面向任务导向 / 语义导向通信的研究问题提炼
3. 面向“感知-传输-协同推理”全链路的论文比较与研究空白分析
4. 面向异构无人机-边缘协同场景的实验设计、结果整理与论文写作支撑

本仓库服务的核心研究方向包括但不限于：

- 多无人机协同感知与协同推理
- 任务导向通信 / 语义通信
- 多模态语义表征与传输
- 分割计算 / 模型切分 / 边缘协同推理
- 资源分配、调度与路径规划联合优化
- 条件触发式语义协作 / 协作动作选择
- 面向真实部署约束的通信-计算-决策联合优化

---

## 当前论文主线锚点（重要）

当前论文的核心问题不是“是否进行语义通信”的一般性讨论，而是：

**在多无人机协同感知场景中，系统是否应当触发某一种语义协作动作，并在考虑感知增益、A2A 链路时延、前后端排队时延、载荷开销、精度-召回-F1 权衡的条件下，选择合适的协作动作与后端接收节点。**

当前论文的工作定位应优先理解为：

- one-step contextual selector / contextual decision baseline
- conditional semantic collaboration
- trigger-and-select mechanism
- pair-level / queue-aware / link-aware / payload-aware decision
- multi-action communication selector
- image-level gain prediction as an extension direction
- label-free online selector still not fully solved

不是：

- always-on semantic communication
- full MARL policy
- long-horizon control / trajectory policy
- robust unseen-regime online selector already solved
- 已经完备解决的端到端自适应协同系统

在分析文献、提炼 gap、生成 paper card、生成 compare 时，必须以这个锚点为第一优先级，避免把工作主线误判为：

- 一般性的语义通信综述
- 一般性的多无人机路径规划
- 一般性的模型切分 / 协同推理
- 一般性的强化学习调度

### 主线详细文档（必读）

当前论文的完整主线梳理见 `paper3_main_thread.md`。
生成任何 papercard、compare、gap_map 前，必须已读取该文档。

该文档包含以下可对照细节：
- 场景参数：多 UAV、A2A 链路、Jetson Orin 部署、VisDrone + DroneVehicle 双域
- 三层架构：后端融合验证 → Pair 选择器 → 图像级触发预测器
- 效用公式：`utility = predicted_delta_quality − λ_latency×latency − λ_payload×payload − precision_penalty`
- 特征设计：V (17维像素统计) / D (~45维检测框统计) / H (~1870维 YOLO latent)
- 关键发现：V+Ridge 优于 deep features；B3 在外部域被正确抑制；排队延迟可压倒链路质量

对照其他论文时，优先从上述细节中寻找验证、挑战或补强线索。

---

## 核心工作原则

### 1. 所有分析都要服务于“研究问题”
不要只做论文摘要搬运，不要停留在“这篇论文讲了什么”。

优先回答以下问题：

- 这篇工作试图解决什么核心问题？
- 它解决的问题是否与当前研究主线一致？
- 它采用了什么关键假设？
- 它在哪个环节最有价值：感知、传输、协同推理、资源分配、触发决策，还是路径规划？
- 它与当前研究相比，缺了哪一环，或者忽略了哪种耦合关系？

### 2. 默认从“全链路视角”看问题
分析论文时，优先考虑以下链路：

**任务需求 → 感知采集 → 状态表征 / 语义提取 → 语义 / 特征传输 → 协同推理 → 动作选择 / 决策执行**

如果论文只覆盖其中一个局部环节，必须明确指出它忽略了哪些关键耦合。

### 3. 默认关注“任务导向”而不是“数据导向”
在相关论文中，要优先识别：

- 研究目标是否由任务驱动，而不是只追求数据重建质量
- 优化目标是否真正体现任务完成效果、推理性能、语义保持或系统收益
- 是否存在“表面上谈语义，实质仍以比特级传输或传统指标为中心”的情况

### 4. 默认关注“多无人机协同”而不是单节点优化
如果论文只讨论单 UAV、单用户、单链路场景，要明确标注其局限：

- 是否无法自然扩展到多 UAV 协同
- 是否没有考虑视角互补、任务分工、时空协同
- 是否没有考虑多节点间算力异构、带宽竞争和协同调度

### 5. 默认关注“真实部署约束”
优先识别论文是否考虑了以下真实因素：

- 算力受限
- 带宽受限
- 中间特征或 proposal / metadata 传输开销
- 特征压缩与失真
- 时延约束
- 能耗约束
- 无人机轨迹与通信耦合
- 多视角冗余与互补关系
- 模型切分后前后端负载不平衡
- A2A 链路质量变化
- queue delay / occupancy state / back-end busy state

如果没有考虑，需明确指出。

### 6. 默认关注“条件触发式协作”而不是 always-on 协作
分析相关论文时，优先识别：

- 是否存在 trigger / no-trigger / reject 机制
- 是否把协作动作视为 optional action，而不是总是启用的默认模块
- 是否显式建模“协作收益 < 协作代价”时应保持 local-only / none

### 7. 默认关注“动作空间与 operating region”
对于当前论文方向，仅仅识别“是否协作”不够，还要识别：

- 动作空间是否只有单一协作动作，还是多动作选择
- 不同动作是否对应不同质量侧重（如 F1 / precision / recall）
- 是否存在 stable trigger / stable reject / cost-sensitive borderline regime

---

## 文献初筛规则

当任务是“筛选论文”时，优先基于标题、摘要、关键词、作者、年份、期刊 / 会议等元数据进行判断，不要一开始就通读全文。

### 对当前研究方向的高相关论文，通常应满足以下至少两类特征：

#### A. 场景相关
- UAV / drone / multi-UAV / UAV swarm
- aerial sensing / aerial network / UAV-assisted
- edge-assisted UAV inference
- collaborative aerial perception
- air-ground collaborative computing

#### B. 问题相关
- task-oriented communication
- semantic communication
- mission-aware transmission
- collaborative inference
- split computing / split inference
- resource allocation / scheduling
- multi-UAV path planning
- perception-communication-computing co-design
- conditional collaboration / trigger policy / selective communication
- utility prediction / gain prediction / action selection

#### C. 系统相关
- 感知-通信-计算联合优化
- 多节点协作与任务分工
- 异构算力环境下的推理 / 传输决策
- 与真实部署相关的时延、能耗、带宽、精度权衡
- queue-aware / link-aware / payload-aware decision

### 当前论文优先关注的问题类型

对于当前这篇论文，优先关注以下文献类型：

#### A. 条件触发型协作 / 通信决策
- 是否触发协作
- 是否存在 reject / abstain / local-only 动作
- 是否强调 conditional trigger 而不是 always-on

#### B. 多动作选择而非单动作开关
- 动作空间是否包含多个协作模式
- 不同动作是否对应不同质量侧重（如 F1 / recall / precision trade-off）
- 是否存在 cost-aware operating region

#### C. 队列 / 链路 / 载荷联合代价建模
- A2A link
- queue delay
- payload cost
- compute latency
- receiver selection / pair selection

#### D. 在线增益预测 / utility prediction
- scenario-level lookup
- image-level gain prediction
- state-aware prediction
- utility calibration
- OOD / unseen-regime robustness

#### E. 不应误判为核心相关的论文
以下文献即使表面相关，也通常不应判为当前论文的核心相关：
- 只做 always-on 协作推理，不含 trigger 机制
- 只做模型切分，不含动作选择与代价权衡
- 只做路径规划，不含协作通信选择
- 直接建模 MARL / long-horizon control，但与当前 one-step selector 断层较大

### 对每篇论文统一输出以下字段：
- 研究问题
- 场景设定
- 核心方法
- 相关度（高 / 中 / 低）
- 属于哪个研究子方向
- 与当前研究的关系
- 可能的价值
- 可能的局限
- 建议动作（精读 / 略读 / 跳过）

### 默认子方向标签
筛选时优先归类到以下一个或多个方向：

- 多无人机协同感知
- 任务导向通信
- 语义通信
- 协同推理
- 分割计算 / 模型切分
- 资源分配与调度
- 路径规划
- 多模态语义融合
- 边缘智能 / 空地协同
- 条件触发式协作决策
- 多动作 selector / action selection
- utility prediction / gain prediction
- queue-aware / link-aware communication selection

---

## 精读规则

当任务是“精读论文”时，必须结合 PDF 与 notes 一起分析，不要只复述摘要。

### PDF 处理规则
- 不要直接基于 raw PDF 生成 paper card。
- 优先检查是否存在可读的文本提取结果（如 `papers/.../*.md`、`papers/.../*.txt`、OCR 结果）。
- 若正文提取失败，必须明确说明“分析主要基于 metadata / notes”，不得伪装成全文精读。
- 若 PDF 可读，但图表 / 表格 / 附录明显影响结论，应明确指出正文提取的边界。

### 场景-实验双重合理化（重要补充规则）
精读论文时，除以下提炼条目外，必须同步执行 `Agents.md` 中第 11 项 "Scenario-Experiment Justification（场景-实验双重合理化）" 分析。核心目标：从他人论文中提取"场景约束→技术需求→算法选择→实验验证"的完整因果链，反哺自身论文的防御性写作，回应审稿人对"技术堆砌"的质疑。

### 精读对照检查清单（每次生成 papercard 前执行）

- [ ] 已读取 `paper3_main_thread.md`
- [ ] 被分析论文的**场景**与当前论文是否可比？（多 UAV？带宽受限？边缘部署？）
- [ ] 被分析论文的**效用函数/目标函数**与当前论文的 utility formula 有何异同？
- [ ] 被分析论文的**特征设计**是否支持 V-feature 的极简路线？或提供了更优替代？
- [ ] 被分析论文的**实验矩阵**是否覆盖当前论文未探索的维度（退化类型/指标/budget/baseline）？
- [ ] 被分析论文是否提供了可用的**消融策略**或**"why not simpler"论证**？
- [ ] 被分析论文是否包含可支撑当前论文**防御性写作**的外部证据？
- [ ] 被分析论文是否暴露了当前论文的**薄弱环节**（如 one-step selector 过于简单、线性效用不适应硬 deadline、缺少 sequential control？）——参见 Agents.md Critical Self-Review Rule
- [ ] 对照结果是否已写入 papercard 对应条目（§2/§3/§5/§7/§8/§10/§11）？

### 每篇精读论文统一提炼以下内容：

#### 1. Problem
论文试图解决什么问题？
这个问题更偏向以下哪一类：

- 感知质量不足
- 传输效率不足
- 推理实时性不足
- 协同机制不足
- 资源分配不合理
- 路径规划与下游任务脱节
- 多模态语义没有统一建模
- 协作是否触发的问题没有被显式建模
- 多动作选择 / 接收端选择没有被显式建模

#### 2. Setting / Assumptions
论文采用了哪些关键假设？

优先识别：
- 单 UAV 还是多 UAV
- 是否有边缘服务器
- 是否存在异构算力
- 是否默认完美信道 / 完美感知
- 是否固定路径或固定任务
- 是否默认模型切分点固定
- 是否忽略多视角同步与冗余
- 是否只做单模态图像语义
- 是否默认 always-on 协作
- 是否默认 oracle state / oracle degradation label
- 是否忽略 queue delay / receiver busy state / payload cost

#### 3. Core Idea
论文最核心的思想是什么？
用简洁语言说明“它为什么这样设计”。

#### 4. Key Mechanism
重点提取：
- 任务建模方式
- 语义表征方式
- 分割推理机制
- 特征 / proposal / metadata 压缩方式
- 资源调度方法
- 路径规划方法
- 联合优化目标与变量
- 奖励函数 / 目标函数 / 约束条件
- trigger rule / selector rule / utility function
- receiver / pair selection mechanism
- calibration / threshold / safeguard

#### 5. Experiments
重点关注：
- 实验是否真正支撑论文结论
- 是否有合理 baseline
- 是否覆盖时延、精度、能耗、带宽、鲁棒性等维度
- 是否只在理想仿真中成立
- 是否缺少与真实部署有关的验证
- 是否分析不同工况下的 operating region
- 是否区分 seen-regime 与 unseen-regime
- 是否包含消融实验以证明各组件必要性（参见 Agents.md 第 11 项场景-实验双重合理化）

#### 6. Strength
论文最值得借鉴的地方是什么？

#### 7. Weakness
论文最明显的局限是什么？
优先寻找以下类型的问题：

- 只做局部优化，没有全链路视角
- 强调通信但没有体现任务完成效果
- 强调推理但忽略特征 / proposal 传输成本
- 强调路径规划但没有联动下游推理 / 通信
- 只考虑单模态，缺少任务语义融合
- 只在理想条件下成立，难以部署
- 方法复杂但实验支撑不足
- 算法/模型选择缺乏场景必要性论证，存在技术堆砌嫌疑（参见 Agents.md 第 11 项）
- 没有 trigger / reject 机制
- 没有多动作选择，只是 always-on 模块
- 严重依赖 oracle label / seen regime
- 无法解释边界工况或 cost-sensitive regime

#### 8. Reusable Part
哪些内容可直接复用到当前研究中？

例如：
- 系统建模方式
- 问题定义方式
- 指标体系
- 奖励函数设计
- 特征压缩思路
- 协同推理框架
- 路径规划约束建模方式
- related work 的叙述逻辑
- trigger / utility / calibration 的写法
- 多动作 selector 的组织方式

#### 9. Attack Point
哪些点可以作为后续改进或切入点？

优先识别：
- 缺少任务导向优化
- 缺少多 UAV 协同
- 缺少异构算力建模
- 缺少感知-通信-推理联合优化
- 缺少多模态语义
- 缺少多视角路径规划与下游任务联动
- 缺少 trigger / reject 机制
- 缺少 pair-level / receiver-level action selection
- 缺少 online gain prediction
- 缺少 unseen-regime robustness

#### 10. Relation to My Topic
必须明确说明这篇论文与当前研究主线之间的关系，不能只说“相关”。

优先回答：
- 它补的是哪一环？
- 它忽略了哪一环？
- 它是可直接借鉴的前置工作，还是可作为对比基线？
- 它能否支撑当前研究中的某一部分论证？

#### 11. Action-Space Relevance
该论文是：
- single action
- trigger vs no-trigger
- multi-action selector
- pair / receiver selection
- scheduling over multiple candidates

#### 12. Cost Model Relevance
该论文是否显式考虑以下代价：
- link delay
- queue delay
- payload size
- compute latency
- precision penalty / utility calibration

#### 13. Selector Type
该方法更接近：
- rule-based selector
- contextual selector
- learned utility predictor
- state estimator + selector
- bandit / RL / MARL
- optimization solver

#### 14. Regime Behavior
该论文是否分析不同退化 / 场景 / 状态下的 operating region？
是否区分：
- robust trigger regime
- stable reject regime
- cost-sensitive borderline regime

#### 15. Deployability
该方法在真实部署上是否可信？
尤其关注：
- 是否依赖 oracle state / perfect labels
- 是否依赖强监督场景标签
- 是否具备 unseen-regime generalization 分析
- 是否存在过触发 / 误触发风险

#### 16. Paper-Facing Use
这篇论文更适合用于：
- Introduction 动机
- Related Work 分类
- 方法设计支撑
- baseline 选择
- 负例对比 / 局限论证

---

## 多篇论文比较规则

当任务是“比较多篇论文”时，不要按“每篇一段摘要”重复堆叠。
要围绕当前研究主线比较它们的差异和缺口。

### 比较时优先使用以下维度：

#### 1. 问题定义
- 是任务导向还是数据导向？
- 是面向感知、传输、推理、动作选择还是联合优化？
- 是优化局部性能还是系统级目标？

#### 2. 场景设定
- 单 UAV / 多 UAV
- 单边缘节点 / 多边缘节点
- 同构 / 异构算力
- 单模态 / 多模态
- 固定任务 / 动态任务
- 是否存在 front-back pair / receiver selection

#### 3. 方法机制
- 传统通信优化
- 语义通信
- 分割推理
- 多智能体协同
- 强化学习调度
- 联合优化
- 路径规划
- 多模态融合
- trigger / abstain / reject
- contextual selector
- gain prediction / utility prediction

#### 4. 评价指标
- 精度
- 召回
- F1
- 时延
- 能耗
- 带宽占用
- payload overhead
- 任务成功率
- 语义保持程度
- 协同收益

#### 5. 局限与空白
重点提炼：
- 哪些论文都忽略了任务语义
- 哪些论文都没有真正把路径规划与下游推理结合
- 哪些论文都没有处理异构算力下的切分决策
- 哪些论文都停留在单模态图像特征层面
- 哪些论文没有考虑多视角互补关系
- 哪些论文没有 trigger / reject 机制
- 哪些论文没有 pair-level / receiver-level selection
- 哪些论文没有分析 operating region
- 哪些论文没有讨论 seen / unseen regime 差异

### 当前论文专用 compare 维度
比较时，除通用维度外，必须额外比较：

1. 是否有 trigger / reject 机制
2. 是否支持多动作而非单一协作模式
3. 是否显式讨论不同场景 / 状态下的动作分区
4. 是否有 cost-sensitive / borderline regime 分析
5. 是否考虑 queue / link / payload 联合影响
6. 是否把 scenario lookup 与 image-level prediction 区分开
7. 是否分析 seen-regime 与 unseen-regime 差异
8. 是否讨论 calibration / safeguard / conservative policy 的收益与代价

### Compare 输出要求
每份 compare 文档最后必须包含：

#### Current Paper Position
- 本文当前更接近哪一类
- 本文与这些工作的最关键差异是什么
- 本文当前不应声称覆盖什么
- 本文下一步最需要补的文献支撑是什么

---

## 研究空白（Gap）提炼规则

寻找研究空白时，必须立足于多篇论文的共性缺陷与系统性遗漏，不能凭空编造“创新点”。

### 当前研究方向下，优先关注以下潜在空白：

#### 1. 从“单环节优化”到“全链路联合优化”
很多工作只做：
- 感知
- 通信
- 推理
- 路径规划
- 动作选择
中的一个局部环节，而没有统一考虑全链路耦合。

#### 2. 从“数据传输导向”到“任务导向 / 语义导向”
很多工作仍默认追求更多数据、更高重建质量，而不是围绕任务目标保留关键语义。

#### 3. 从“单节点 / 单机”到“多无人机协同”
很多工作缺少：
- 多视角协同
- 多 UAV 任务分工
- 协同采集与协同推理
- 跨节点资源竞争与调度

#### 4. 从“单模态语义”到“多模态任务语义”
很多工作只处理图像特征，而没有把图像、文本、语音等任务信息映射到统一语义空间。

#### 5. 从“固定切分”到“动态切分与协同执行”
很多分割推理工作没有联合考虑：
- 切分点
- 特征尺寸
- 前后端负载
- 特征传输开销
- 任务时延与精度收益

#### 6. 从“静态轨迹”到“采集-传输-推理耦合路径规划”
很多路径规划工作没有真正把多视角采集质量、特征传输负担、协同推理需求统一建模。

#### 7. 从“always-on 协作”到“条件触发式协作”
很多工作默认协作始终启用，而没有回答：
- 何时不应协作
- 协作收益何时被代价抵消
- 是否应显式引入 none / local-only 动作

#### 8. 从“单动作协作”到“多动作选择”
很多工作没有讨论：
- 不同协作动作在不同工况下的适用区间
- 不同动作之间的 precision / recall / F1 trade-off
- operating region 的边界

#### 9. 从“场景级查表”到“图像级在线增益预测”
很多工作没有讨论：
- 细粒度 frame-level / image-level gain prediction
- 无标签在线 state estimation
- calibration / safeguard
- unseen-regime 下的稳定性

### 输出研究空白时，优先使用以下结构：
- 当前已有工作主要覆盖了什么
- 它们共同忽略了什么
- 为什么这个忽略在多无人机任务导向通信中是关键问题
- 这个空白为什么具有“有意义、可建模、可实验验证”的特征
- 当前论文已经覆盖到哪一步，尚未覆盖到哪一步

---

## 写作支撑规则

当任务是为开题、综述或论文写作服务时，所有输出都应围绕当前研究方向展开，不要生成泛化模板式空话。

### 优先支持的写作任务
- 研究背景与意义
- 研究现状与趋势
- 关键科学问题提炼
- 研究内容梳理
- Related Work
- 方法设计逻辑说明
- 实验设计说明
- 论文贡献表达优化
- 审稿意见回复支撑

### 写作时的偏好
- 强调低空经济、智能无人系统、空地协同等应用背景时，要服务于研究问题，不要堆政策口号
- 强调多无人机协同感知、任务导向传输、协同推理、条件触发决策之间的逻辑闭环
- 避免“本文首次”“显著优于所有工作”这类空泛夸大
- 所有贡献表达都应能在模型、算法或实验中找到支撑
- 明确区分“当前论文已完成的 baseline / selector”与“未来可扩展方向”

---

## 输出风格要求

- 优先结构化表达
- 用语准确、克制、学术化
- 不要写成宣传稿
- 不要用空泛术语堆砌创新性
- 不要回避局限与不确定性
- 如果信息不足，明确写“待确认”
- 对研究空白的表述要有逻辑链，不要只列关键词
- 在 VSCode / Codex 对话中引用文件时，优先使用纯文本相对路径或“路径:行号”格式，例如 `compare/UAV-LLM/overview.md`、`papercard/UAV-LLM/index.md:10`，不要使用 Markdown 超链接

---

## 文件使用规则

- `metadata/`：从 Zotero 导出的题目、摘要、作者、年份、来源等信息
- `notes/`：从 Zotero 导出的 item notes 与 annotation notes
- `papercard/`：每篇论文的结构化精读卡片（注意：以当前仓库实际目录名为准）
- `compare/`：同一主题下的多篇论文比较结果
- `gap_map/`：研究空白、切入点与创新方向整理
- `writing_support/`：背景、意义、研究内容、贡献表达等写作支撑材料
- `papers/`：当前项目实际使用的论文 PDF、提取文本、临时阅读材料

### 目录一致性规则
- 以当前仓库的实际目录名为准，不要自动把 `papercard/` 写成 `paper_cards/`
- 如果仓库存在 `compare_index.md`、`paper_index.md`、`paper_index.md` 等索引文件，应优先参考索引组织已有成果

### 新论文并入规则
当有新论文加入时，不要直接从头重写全部比较结果。

优先执行以下流程：
1. 先为新论文生成独立的 paper card。
2. 检查 `compare/` 与 `compare_index.md`，判断该论文属于哪个已有主题。
3. 如果存在匹配主题，则在原比较文件基础上增量更新：
   - 补充该论文的位置
   - 更新问题定义、假设、方法、实验、局限的对比
   - 更新共同空白与潜在切入点
4. 如果不存在匹配主题，则新建比较文件。
5. 更新 `paper_index.md` 和 `compare_index.md`，确保后续任务可追踪。

---

## 禁止事项

- 不要把摘要复述当作精读分析
- 不要把表面关键词重合作为高度相关的依据
- 不要虚构论文中的模型、实验、结果或贡献
- 不要脱离当前研究主线空泛讨论“未来工作”
- 不要忽略任务导向、多 UAV 协同、异构算力和全链路耦合这些关键维度
- 不要修改原始元数据文件，除非用户明确要求
- 不要删除已有笔记、卡片或比较结果，除非用户明确要求

### 当前论文相关的额外禁止事项
- 不要把当前工作写成 MARL，除非文献确实在帮助论证“未来可扩展到 MARL”，而不是当前方法本身
- 不要把 scenario-level lookup baseline 误写成 learned online selector
- 不要把 seen-regime 提升写成 robust unseen-regime generalization
- 不要把 conservative safeguard 写成主方法优势，如果它同时明显压制了有益协作机会
- 不要忽略 precision / recall / F1 之间的权衡，只用单一“精度提升”或“召回提升”概括动作价值
- 不要把 always-on 协作论文误当成当前论文最直接的主对标对象

---

## 默认工作流程

### 阶段 1：初筛
先基于 metadata 判断论文与当前研究主线的相关性，做高 / 中 / 低分类。

### 阶段 2：精读
对高相关论文，结合 PDF 与 notes 生成结构化 paper card。

### 阶段 3：横向比较
对同主题论文进行比较，重点找差异、共性与系统性遗漏。

### 阶段 4：提炼研究空白
从比较结果中提炼真正有研究价值、可建模、可实验验证的切入点。

### 阶段 5：服务论文与实验
将上述结果用于：
- 开题报告
- 综述写作
- Related Work
- 方法设计
- baseline 选择
- 实验方案梳理
- 论文修改与质检

### 当前论文的额外建议流程
1. 先明确该论文属于：Introduction 动机 / Related Work / 方法支撑 / baseline / 负例对比 哪一类用途。
2. 优先生成能服务当前论文的 paper card，而不是泛化读书笔记。
3. compare 文件必须持续维护，不要每次从零重写。
4. 所有分析都应回到“当前论文到底在解决什么问题、当前还没解决什么问题”这一主线。
