# Codex 任务说明：高重合度文献对当前小论文 idea 的冲击评估（实验主线版）

## 0. 使用方式

本文档是一个 **可直接附加给 Codex 的任务说明文件**。  
使用时不需要把本文档内容复制到 Codex 聊天框中。

推荐使用方式：

1. 在 VS Code / Codex 中打开 `research-hub` 工作区。
2. 附加或确保工作区中存在以下文件：
   - `Agents_optimized.md`
   - 当前论文主线文件，如 `paper3_scope.md`、`session_handoff.md`、`current_tasks.md`
   - 高重合度文献对应的 `papercard`
   - 已有相关 `compare` 文件，如存在则一并读取
3. 在 Codex 聊天框中只输入一句：
   ```text
   请按照附件中的高重合度文献冲击评估任务说明执行。
   ```
4. Codex 应根据本文档完成分析，并将结果保存为独立 Markdown 文件。

---

## 1. 任务性质

本任务不是普通文献总结，也不是重新生成 `papercard`。  
本任务是：

**高重合度文献冲击评估 / Similar-work impact assessment**

目标是判断一篇与当前小论文高度相似的文献对当前 idea 的影响，包括：

- 是否威胁当前论文创新性；
- 与当前工作真正重合在哪里；
- 哪些差异只是表面差异；
- 哪些差异可以支撑创新性边界；
- 当前论文哪些 claim 需要收缩或改写；
- 当前论文还缺哪些实验、对比、建模说明和写作支撑；
- 这篇相似论文应该如何进入 Related Work；
- 当前论文应如何重新定位，才能避开正面重叠。

---

## 2. Codex 必须读取的文件

执行任务前，Codex 必须优先读取以下文件。

### 2.1 必读文件

- `Agents_optimized.md`
- 高重合度文献对应的 `papercard`

### 2.2 可选文件

如果存在以下文件，应一并读取：

- `compare/` 下与该主题相关的已有比较文件
- `gap_map/` 下与当前主题相关的 gap 文件
- `writing_support/` 下与 Introduction / Related Work 相关的材料
- `metadata/` 下该文献的元数据文件
- `notes/` 下该文献的阅读笔记
- `papercard/` 下同类文献的其他卡片

### 2.3 如果缺少文件

如果缺少当前论文主线文件或高重合度文献 `papercard`，不要强行编造分析。  
应在输出文件开头明确写：

```text
信息不足：缺少 xxx 文件，因此本评估只能基于已有材料进行。
```

---

## 3. 当前小论文研究主线（必须作为对比锚点）

Codex 在分析任何高重合度文献时，必须以本节为当前小论文主线锚点。

### 3.1 当前论文的一句话定位

当前论文不是泛泛讨论“UAV 语义通信”，而是研究：

**在无人机场景下，面向车辆/目标检测任务，是否触发语义协作动作、触发哪一种协作动作，以及如何在任务收益、精度-召回权衡、A2A/队列/载荷/时延代价和在线状态不确定性之间做条件式选择。**

更具体地说，当前论文围绕：

- `none / local_only`
- `B2_RECALL`
- `B3_TUNED`

这类多动作语义协作选择展开，并进一步探索从场景级查表到图像级在线预测的演进。

---

### 3.2 当前论文不应被误写成什么

当前论文目前不应被描述为：

- 完整 MARL 策略；
- 长时域轨迹规划或路径控制；
- 完整端到端语义通信系统；
- 已经解决 unseen-regime / OOD 泛化的在线选择器；
- 已经完成真实多 UAV 闭环部署的系统；
- 单纯的模型切分或协同推理论文；
- 单纯的图像增强 / 检测后处理论文。

当前论文更稳妥的定位是：

- **one-step contextual semantic-collaboration selector**
- **task-utility-aware collaboration trigger**
- **multi-action semantic collaboration selector**
- **cost-aware and safety-aware image-level trigger predictor**
- **UAV vehicle-detection task 中的 conditional semantic collaboration baseline**

---

## 4. 当前实验链条与主线证据

本节是 Codex 做高重合度文献对比时必须优先调用的“当前工作事实”。

### 4.1 从单动作协作到多动作 selector

当前工作最初从 `B3_TUNED` 单一协作动作扩展为多动作语义通信 selector：

```text
none / local_only
B3_TUNED   balanced proposal-rich backend augment
B2_RECALL  recall-first proposal-rich backend review
```

多动作 utility 的基本形式是：

```text
utility =
    predicted_delta_quality
  - precision_penalty_weight * max(0, -delta_precision)
  - lambda_latency * pair_extra_latency_ms
  - lambda_payload * extra_payload_bytes
```

其中：

- `B3_TUNED` 主要使用 `delta_f1` 作为预测质量；
- `B2_RECALL` 主要使用 `0.5 * delta_recall + 0.5 * delta_small_recall` 作为 recall-first 质量；
- `precision_penalty_weight = 0.5` 是当前中间 operating point；
- `lambda_latency = 0.0002`；
- `lambda_payload = 0.0000005`。

在比较相似论文时，必须检查它是否也支持：

- 多动作协作；
- local-only / none abstention；
- recall-first 与 balanced action 的区分；
- precision penalty；
- 成本感知 utility；
- 根据不同状态选择不同动作。

---

### 4.2 precision penalty 与 operating region

当前实验已经表明：`precision_penalty_weight` 会平滑地改变 selector 的动作区间。

典型趋势：

- 低 precision penalty 时，selector 倾向 `B2_RECALL`；
- 高 precision penalty 时，selector 转向 `B3_TUNED` 或 `none`；
- `0.5` 是一个中间 operating point，使 `B2_RECALL`、`B3_TUNED` 和 `none` 均有非退化角色。

Codex 对比文献时必须检查：

- 该文献是否显式讨论 precision / recall / F1 trade-off；
- 是否存在不同 operating region；
- 是否只报告单一 accuracy/mAP/F1，而没有分析何时该协作、何时不该协作；
- 是否有 action-level trade-off，而不是单一协作模式。

---

### 4.3 latency / payload cost sensitivity

当前实验继续验证：当 latency 和 payload cost 增大时，collaboration trigger rate 会降低，边界场景更容易从 `B2_RECALL` 或 `B3_TUNED` 转为 `none`。

需要重点保留的当前结论：

- `downscale_0.25`、`occlusion` 等强收益场景更稳定；
- `clean`、`dark_heavy`、`fog` 等弱收益或边界场景更 cost-sensitive；
- 代价不是附加说明，而是决定是否触发协作的重要变量。

Codex 对比文献时必须检查：

- 该文献是否考虑 latency；
- 是否考虑 payload / bandwidth；
- 是否考虑 queue delay；
- 是否考虑 pair-level receiver selection；
- 是否只做 quality gain，而忽略系统代价；
- 是否能解释强收益、稳定拒绝、边界区域。

---

### 4.4 从 scenario-level lookup 到 image-level gain prediction

当前论文的重要演进是：从每个 `degradation_scenario` 一行平均语义增益，推进到 **image-level communication gain prediction**。

图像级预测的动机是：

- 同一退化场景内部，不同图像的协作收益可能不同；
- scenario-level lookup 依赖人工场景标签，不适合真实在线部署；
- online UAV selector 更需要从当前图像状态、检测统计或 latent feature 中预测协作收益。

当前工作已经尝试：

- B0/B1 detection statistics；
- hand-crafted visual-state features；
- estimated / learned degradation-state probabilities；
- action-specific calibration；
- direct action classifier；
- YOLO latent features；
- visual + latent hybrid predictors；
- safety guards。

Codex 对比文献时必须检查：

- 该文献是否依赖 oracle scenario label；
- 是否做 image-level / sample-level decision；
- 是否能在没有人工 degradation label 的情况下运行；
- 是否只做 scenario-level 平均增益；
- 是否分析同一场景内部的 useful / harmful collaboration 差异。

---

### 4.5 visual-state features 的负结果与边界

当前实验表明，简单 hand-crafted visual-state features 并不能稳定替代场景标签：

- 单纯加入 blur / brightness / contrast / haze / occlusion proxy 等视觉特征，并不一定提升 no-scenario selector；
- scenario-aware model 仍然更强；
- LOSO 下 label-free policies 暴露出明显泛化问题；
- `blur_heavy` 是持续存在的高风险 held-out failure mode。

Codex 对比文献时必须警惕：

- 如果相似论文声称用简单 image quality 特征即可做 robust online selection，必须检查其实验是否有 unseen degradation / LOSO / OOD 验证；
- 不要把当前工作写成“hand-crafted visual features 已解决状态估计”；
- 如果文献没有做 unseen-regime 验证，其贡献不能直接压制当前工作关于泛化边界的分析。

---

### 4.6 calibration / guard / hybrid selector

当前实验探索了多类安全机制：

- per-action calibration；
- learned-state none veto；
- OOD guard；
- blur/fog guard；
- B2-to-B3 downgrade；
- safe-ridge veto；
- hybrid visual + latent guard。

当前结论较保守：

- per-action calibration 对 learned-state 有小幅帮助，但不足以成为主线；
- visual calibrated + learned-none veto 可以减少 held-out blur failure，但提升很小；
- guard 机制主要是 safety mechanism，不是强 utility-improvement mechanism；
- 过于保守的 guard 会损失 `downscale_0.25`、`mixed`、`occlusion` 等协作机会；
- safety 与 utility capture 之间存在明显张力。

Codex 对比文献时必须检查：

- 该文献是否考虑 false trigger / over-trigger；
- 是否提供 abstention / veto / guard；
- 是否讨论保守策略带来的机会损失；
- 是否区分安全型策略和高收益型策略；
- 是否有 calibration 或 uncertainty-aware selection。

---

### 4.7 YOLO latent features：任务感知状态信号

当前工作的重要进展之一是引入 **YOLO intermediate latent features** 作为 task-aware image-level state。

当前实验使用：

- YOLO layer `15`
- YOLO layer `18`
- YOLO layer `21`

的 latent statistics，并发现：

- YOLO latent features 相比 hand-crafted visual proxies 提供了更强的任务相关信号；
- latent predictor 提升 LOSO aggregate utility 和 oracle capture；
- 但 unguarded latent predictor 仍会在 held-out `blur_heavy` 和弱 `fog` 中过触发；
- 因此 latent features 应与 action-specific guard 或 safety guard 配合使用；
- 当前 latent 表示仍是简单统计，不是端到端训练的 latent policy head。

Codex 对比文献时必须检查：

- 该文献是否使用 detector-internal representation；
- 是否使用 task-aware latent state；
- 是否只是使用原始图像质量特征；
- 是否有 latent-feature OOD / risk / confidence guard；
- 是否区分 utility prediction 与 degradation classification；
- 是否能解释 latent useful but unsafe 的边界。

---

### 4.8 visual + YOLO latent hybrid：当前最强方向

当前实验表明，visual + YOLO latent + learned-state 的 hybrid predictor 是目前最有潜力的方向之一。

当前保守结论是：

- hybrid action classifier 有最强 aggregate LOSO utility；
- hybrid ridge + blur guard 有更好的 blur/fog safety；
- high-utility hybrid action learner 不能直接作为最终在线 trigger，因为它仍会在 held-out `blur_heavy` 上过触发；
- 更稳妥的 paper-facing 表述是：  
  **visual and YOLO-latent signals are complementary; hybrid policies improve image-level fusion prediction, but high-utility policies still require safety guards.**

Codex 对比文献时必须检查：

- 相似论文是否同时结合 visual cue 和 task-aware latent cue；
- 是否只追求 aggregate utility 而忽略 safety；
- 是否有 guard 后的 hybrid policy；
- 是否有 false-trigger analysis；
- 是否在 blur/fog-like adverse regimes 下验证安全性。

---

### 4.9 continuous blur/fog validation

当前后续实验已开始验证：

- continuous-strength blur；
- continuous-strength fog；
- high-risk veto；
- moderate-risk B2-to-B3 downgrade。

对比文献时必须关注：

- 文献是否只在离散退化标签上验证；
- 是否有连续强度退化验证；
- 是否能证明 guard 不只是对固定 scenario label 过拟合；
- 是否分析 blur/fog strength 与 trigger behavior 的关系。

---

### 4.10 DroneVehicle 外部验证

当前工作已经开始引入 DroneVehicle RGB 作为外部 real-UAV vehicle dataset，用来检查：

- VisDrone-trained detector 在外部 UAV 数据集上的 domain gap；
- category mapping 是否影响 recall；
- B2/B3 是否仍能在外部数据集上 recover recall；
- backend augmentation 是否在 external-domain 中仍有价值。

当前注意事项：

- DroneVehicle 初始 n=20 是 smoke / calibration，不是最终正式结论；
- fair all-vehicle evaluation 应使用 merged vehicle prediction：
  ```text
  --gt-category-id 0
  --pred-class-id 3
  --target-class-ids 3 4 5 8
  ```
- DroneVehicle polygon / bndbox 被转换为 axis-aligned YOLO labels；
- external-domain sensitivity 是当前论文需要谨慎呈现的重要现象；
- B2_RECALL / B3_TUNED 在 DroneVehicle raw RGB n=100 上需要作为外部验证证据，而不是只依赖 VisDrone synthetic degradation。

Codex 对比文献时必须检查：

- 该文献是否只有单数据集验证；
- 是否有 external real-UAV dataset；
- 是否分析 detector domain gap；
- 是否只用 synthetic degradation；
- 是否评估 action 在外部数据集上的 recall / precision / F1 trade-off。

---

## 5. 当前论文最稳妥的贡献边界

Codex 在对比相似文献时，应优先保护以下贡献边界。

### 5.1 可保留的核心卖点

当前论文仍可保留的卖点包括：

1. **将语义协作建模为条件触发问题，而不是 always-on communication。**
2. **将语义协作从单动作扩展到 `none / B2_RECALL / B3_TUNED` 多动作 selector。**
3. **显式建模 precision-recall-F1 trade-off 与系统代价。**
4. **考虑 latency / payload / queue / pair-level cost 对协作触发的影响。**
5. **从 scenario-level lookup 走向 image-level gain prediction。**
6. **系统性比较 visual features、learned state、YOLO latent features 与 hybrid predictors。**
7. **明确揭示 high-utility predictor 与 safe trigger 之间的张力。**
8. **使用 LOSO 和 continuous blur/fog 验证 unseen-regime / safety boundary。**
9. **引入 DroneVehicle 作为外部 real-UAV vehicle validation，检查 domain gap 与 recall recovery。**

---

### 5.2 必须避免过度声称的内容

当前论文不应强声称：

- 已经解决 online degradation recognition；
- 已经实现 robust OOD selector；
- YOLO latent features alone 足以支持安全触发；
- guard 机制已经无损保留所有有益协作机会；
- 当前方法是完整 MARL；
- 当前方法覆盖 long-horizon trajectory planning；
- 当前方法已完成真实多 UAV 部署；
- 当前 selector 已经在所有 external datasets 上验证充分。

---

### 5.3 更稳妥的论文定位表述

Codex 在输出冲击评估时，可以优先参考以下定位：

> This work studies conditional semantic collaboration for UAV-based vehicle detection. Instead of treating backend semantic fusion as an always-on operation, we formulate a cost-aware multi-action selector that decides whether to remain local, trigger a recall-first backend review, or trigger a balanced backend augmentation. The selector explicitly accounts for task-level utility, precision-recall trade-off, latency and payload costs, and further explores image-level online gain prediction with visual, detector-latent, and hybrid state signals. The results highlight both the benefit and the safety boundary of online semantic collaboration, especially under unseen blur/fog regimes and external DroneVehicle validation.

中文可写为：

> 本文研究面向无人机车辆检测任务的条件式语义协作机制。不同于将后端语义融合视为始终开启的固定流程，本文将其建模为一个代价感知的多动作选择问题：系统需要在本地检测、召回优先的后端复核以及平衡型后端增强之间进行选择。该选择过程显式考虑任务级收益、精度-召回权衡、时延与载荷代价，并进一步探索基于图像状态、检测器中间特征和混合状态表征的在线增益预测。实验重点揭示在线语义协作的收益边界与安全边界，尤其关注未见 blur/fog 退化以及 DroneVehicle 外部数据集上的泛化风险。

---

## 6. 高重合度文献冲击评估任务

Codex 必须围绕以下 6 个问题展开分析。

---

### 6.1 真正重合点

分析这篇高重合度论文与当前工作的真实重合点。

必须覆盖：

- 问题定义是否重合；
- 系统设定是否重合；
- 是否都是 UAV / multi-UAV / edge-assisted / collaborative inference 场景；
- 是否都有 semantic communication / task-oriented communication / collaboration trigger；
- 动作空间是否相似；
- 是否都有 `none / local-only / collaboration` 选择；
- 是否涉及多动作选择；
- 是否考虑 queue delay、link delay、payload cost、latency cost；
- 是否都使用 utility / reward / cost-aware decision；
- 是否从 scenario-level 决策走向 image-level decision；
- 是否使用 visual / latent / hybrid state representation；
- 实验目标是否相似；
- 评价指标是否相似。

要求：

- 不要只说“高度相关”；
- 必须指出具体重合在哪个层面；
- 区分“关键词重合”和“研究问题重合”。

---

### 6.2 关键差异

分析当前工作与该论文的差异，并区分两类。

#### A. 表面差异

例如：

- 数据集不同；
- 场景名字不同；
- 模型名称不同；
- 任务表述略有不同；
- 使用的算法外壳不同，但本质决策问题相近；
- 是否使用 YOLO、Transformer、RL 等技术名称的差别。

这些差异通常不足以单独支撑创新性。

#### B. 实质差异

重点识别是否存在以下实质差异：

- 当前工作是否更强调 conditional trigger，而不是 always-on collaboration；
- 当前工作是否有更明确的多动作选择；
- 当前工作是否显式考虑 precision / recall / F1 trade-off；
- 当前工作是否有 queue-aware / link-aware / payload-aware pair-level selection；
- 当前工作是否关注 image-level gain prediction；
- 当前工作是否分析 stable trigger / stable reject / cost-sensitive borderline regime；
- 当前工作是否有 learned / latent / hybrid state representation；
- 当前工作是否有 safety guard / false-trigger analysis；
- 当前工作是否做 LOSO / unseen degradation / continuous blur-fog / external dataset 验证；
- 当前工作是否更适合被定位为 contextual selector baseline，而不是传统通信优化或 MARL。

要求：

- 不要硬找差异；
- 不要把工程实现差异夸大成研究贡献；
- 只把真正能支撑创新性边界的差异列为“实质差异”。

---

### 6.3 对当前论文创新性的威胁

从审稿人视角分析这篇论文可能如何威胁当前论文。

必须回答：

- 如果审稿人拿这篇论文攻击当前工作，最可能怎么说；
- 当前论文哪些 claim 不能再强说；
- 哪些贡献表述需要降级；
- 哪些动机需要重写；
- 哪些 Related Work 段落必须补入这篇论文；
- 哪些实验如果不补，容易被认为不充分；
- 是否需要重新定义当前论文的创新边界。

要求：

- 不要为了安慰而弱化威胁；
- 不要把真实威胁说成“只是相关工作”；
- 但也不要把表面相似夸大成完全撞题。

---

### 6.4 可直接利用的信息

从该论文中提取对当前 idea 有实际价值的信息。

必须覆盖：

- 可借鉴的问题定义方式；
- 可借鉴的系统模型；
- 可借鉴的变量设计；
- 可借鉴的 utility / reward / objective / constraint 写法；
- 可借鉴的 baseline；
- 可借鉴的实验组织方式；
- 可借鉴的 ablation 设计；
- 可借鉴的图表组织方式；
- 可借鉴的 Related Work 分类方式；
- 可借鉴的 Introduction 动机展开方式。

同时必须标注：

- 哪些可以直接借鉴；
- 哪些只能参考，不能照搬；
- 哪些如果借鉴过多，会导致当前论文更像该论文，从而增加撞题风险。

---

### 6.5 当前工作暴露出的缺口

分析这篇相似论文暴露出当前工作还缺什么。

必须覆盖：

- 缺少哪些实验；
- 缺少哪些 baseline；
- 缺少哪些 ablation；
- 缺少哪些 cost sensitivity / parameter sensitivity；
- 缺少哪些 unseen-regime / OOD / external dataset 验证；
- 缺少哪些 continuous degradation 验证；
- 缺少哪些 false trigger / over-trigger 诊断；
- 缺少哪些 theory / modeling explanation；
- 缺少哪些 Related Work 文献支撑；
- 缺少哪些 Introduction 动机支撑。

要求：

- 每个缺口都要说明为什么重要；
- 区分“必须补”和“可以补”；
- 不要列无关扩展。

---

### 6.6 当前论文定位调整建议

基于上述分析，给出当前论文继续推进的建议。

必须回答：

- 当前论文是否需要收缩 claim；
- 是否需要换创新重心；
- 是否需要补强实验；
- 是否需要把该论文作为前置工作；
- 是否需要重写 Related Work 中与它的区分；
- 当前论文最稳的重新定位是什么。

输出时必须给出：

1. 当前论文还能保留的核心卖点；
2. 当前论文必须立即修改或降级的部分；
3. 接下来最值得补的 3 个动作。

---

## 7. 输出文件要求

Codex 必须将结果保存为一个独立 Markdown 文件。

### 7.1 推荐保存目录

优先保存到：

```text
compare/UAV-High-Overlap-Impact/
```

如果该目录不存在，应先创建该目录。

### 7.2 推荐文件命名

优先使用以下格式：

```text
YYYYMMDD_<short_paper_name>_impact_on_my_idea.md
```

示例：

```text
20260508_tinysplat_impact_on_my_idea.md
20260508_semantic_uav_selector_impact_on_my_idea.md
20260508_collaborative_inference_selector_impact_on_my_idea.md
```

如果已有 citation key，也可以使用：

```text
<citation_key>_impact_on_my_idea.md
```

示例：

```text
cao2026_tinysplat_impact_on_my_idea.md
liu2025_uav_semantic_selector_impact_on_my_idea.md
```

---

## 8. 输出文档结构

生成的评估文档必须使用以下结构。

```markdown
# <paper_name> 对当前 idea 的冲击评估

## 1. 评估对象

- 相似论文：
- 对应 papercard：
- 当前论文主线文件：
- 已读取的 compare / gap / writing_support 文件：
- 评估日期：

## 2. 执行摘要

用 5 到 8 条 bullet 总结最重要结论：

- 这篇论文是否构成真实威胁；
- 最大重合点是什么；
- 最关键的实质差异是什么；
- 当前论文应保留的核心卖点是什么；
- 当前论文最需要补强什么。

## 3. 真正重合点

### 3.1 问题定义重合

### 3.2 系统设定重合

### 3.3 动作空间重合

### 3.4 代价建模重合

### 3.5 决策机制重合

### 3.6 实验目标重合

## 4. 关键差异

### 4.1 表面差异

### 4.2 实质差异

### 4.3 哪些差异可以支撑创新性边界

### 4.4 哪些差异不足以支撑创新性

## 5. 对当前论文创新性的威胁

### 5.1 审稿人可能的攻击方式

### 5.2 不能再强说的 claim

### 5.3 需要降级或改写的表述

### 5.4 Related Work 中必须补入的位置

## 6. 可直接利用的信息

### 6.1 问题定义方式

### 6.2 系统模型 / 变量 / 目标函数

### 6.3 Baseline 设计

### 6.4 实验组织方式

### 6.5 Related Work 叙述逻辑

## 7. 当前工作暴露出的缺口

### 7.1 缺少的实验

### 7.2 缺少的对比

### 7.3 缺少的建模说明

### 7.4 缺少的写作支撑文献

## 8. 当前论文定位调整建议

### 8.1 应收缩的 claim

### 8.2 应保留的核心卖点

### 8.3 应补强的证据链

### 8.4 更稳妥的论文定位表述

## 9. 接下来最值得补的 3 个动作

1.
2.
3.
```

---

## 9. 输出风格要求

- 不要复述 `papercard`；
- 不要泛泛说“有启发”；
- 不要只说“相关”或“不相关”；
- 必须区分“表面相似”和“真实威胁”；
- 必须区分“工程差异”和“研究贡献差异”；
- 必须明确哪些 claim 需要收缩；
- 必须明确哪些实验最值得补；
- 必须明确该相似论文应如何进入 Related Work；
- 如果证据不足，明确写“待确认”，不要猜测。

---

## 10. 额外检查清单

输出前，Codex 必须自查以下问题：

- 是否真的读取了 `Agents_optimized.md`？
- 是否读取了当前论文主线文件？
- 是否读取了相似论文 `papercard`？
- 是否避免了普通摘要式总结？
- 是否指出了真实重合点？
- 是否区分了表面差异和实质差异？
- 是否指出了对创新性的威胁？
- 是否给出了可执行的补实验建议？
- 是否保存到了 `compare/UAV-High-Overlap-Impact/`？
- 是否更新或建议更新 `compare_index.md`？

---

## 11. 可选：更新索引文件

如果工作区中存在 `compare_index.md`，Codex 应在不破坏已有内容的前提下追加一条记录，格式如下：

```markdown
- compare/UAV-High-Overlap-Impact/<output_file>.md
  - 类型：高重合度文献冲击评估
  - 相似论文：<paper_name>
  - 当前论文主线：conditional semantic collaboration / multi-action semantic selector
  - 结论：真实威胁 / 中等威胁 / 表面相似 / 待确认
```

如果工作区中存在 `paper_index.md`，Codex 可追加该相似论文的状态：

```markdown
- <paper_name> | 高重合度文献 | 已生成冲击评估 | compare/UAV-High-Overlap-Impact/<output_file>.md
```

如果索引文件不存在，不需要强行创建，除非用户明确要求。
