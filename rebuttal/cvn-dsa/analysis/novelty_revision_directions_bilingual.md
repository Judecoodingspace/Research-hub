# Novelty Revision Directions

## 中文版：创新性表达不足的可推进修改方向

### 1. 当前稿件为什么容易被读成“AI 模块堆叠”

结合 `main.tex` 当前内容，创新性表达不足主要不是因为完全没有贡献，而是因为贡献的呈现方式过于“模型中心化”。

在摘要中，当前表述依次强调 Transformer-based DQI、attention-enhanced LSTM、ESN-assisted DDQN。这会让审稿人首先看到三个现成 AI 模型，而不是看到 CVN/DSA 问题中的机制性矛盾。

在引言贡献列表中，当前贡献 1 强调 Transformer self-attention，贡献 2 强调 novel ESN-DDQN，贡献 3 强调实验性能。这个结构容易被理解为“把已有模型拼起来后做了仿真比较”。

在 Related Work 中，现稿按 MDP、game theory、RL 分类，但没有充分提炼出本文相对已有工作的“缺口矩阵”。例如没有明确说明哪些已有工作只考虑 occupancy，哪些没有 prediction，哪些不支持 overlay/underlay adaptive switching，哪些没有 PU-protection-aware reward，哪些没有 fast convergence design。

在实验部分，已有 ablation 其实能支持一个不错的创新故事：在 `M<N` 时 DQI 更影响 VT throughput，在 `M>N` 时 prediction 更影响 PLR 和 PU protection。但目前这些 insight 主要散落在结果描述里，没有被提升为“系统规律”或“设计原则”。

### 2. 方向一：把论文定位从“新型 ESN-DDQN 算法”改成“CVN 约束下的质量-预测-保护协同接入框架”

这是最推荐的主线。

当前标题和贡献容易让审稿人期待一个 fundamentally new RL algorithm，但 ESN、DDQN、LSTM、Transformer 都不是新东西。因此更稳的策略是承认基础模型来自已有技术，但强调本文的新意在于 CVN 动态接入约束下的系统级协同设计。

可修改位置：

- `main.tex` 标题。
- Abstract。
- Introduction 最后一段和 contributions。
- Related Work 的 summary paragraph。
- Conclusion。

可推进写法：

- 不再主打 “a novel ESN-DDQN algorithm”。
- 改为 “a quality- and prediction-aware adaptive overlay/underlay access framework”。
- 强调本文解决的是三个同时存在的矛盾：idle does not imply usable, prediction does not imply quality, underlay opportunity does not imply PU-safe access。
- 把 Transformer/LSTM/ESN-DDQN 降级为实现该框架的技术组件，而不是论文新意本身。

建议的新贡献表达：

1. We formulate a multi-timescale pre-access state representation that combines instantaneous sensing, medium-term channel quality, and short-horizon occupancy prediction for CVN DSA.
2. We design an interference-aware adaptive overlay/underlay access mechanism with differentiated reward modeling and PU-protection constraints.
3. We develop an ESN-assisted DDQN implementation for fast discrete channel-mode decision making under the proposed state and reward design.
4. We quantify regime-dependent module contributions, showing that quality awareness is more important under spectrum scarcity while prediction dominates interruption avoidance and PU protection under spectrum abundance.

### 3. 方向二：在 Related Work 中增加“缺口矩阵”，让创新点可视化

现在 Related Work 的问题是分类清楚，但 gap 不够锋利。TVT 审稿人会问：既然已有 RL、DRL、ESN-RL、LSTM access，为什么还需要这篇？

建议增加一个表或扩展现有 Table I，把已有工作按能力维度比较。

建议维度：

- CVN-oriented DSA。
- Quality-aware channel evaluation。
- Occupancy prediction。
- Adaptive overlay/underlay switching。
- PU interference protection。
- Fast convergence or low training overhead。
- Deployment/overhead discussion。

这样可以把本文的新意从“用了哪些模型”转成“同时覆盖哪些设计需求”。

可推进方式：

- 将 Table I 从三类方法优缺点表，改成 “Feature comparison with representative DSA studies”。
- 保留 MDP/game/RL 分类，但增加一张 feature matrix。
- 在表后用一段话明确：现有工作通常只覆盖其中一到两个维度，而本文关注这些维度在 CVN 高移动性场景中的联合满足。

### 4. 方向三：把已有消融结果升级成“频谱状态依赖的设计 insight”

这是你当前稿子里比较有潜力的点。现稿在实验部分已经写到：

- `M<N` 时，DQI 对 VT throughput 更关键。
- `M>N` 时，prediction 对 PLR 和 PU protection 更关键。
- No-Prediction 在 PU throughput 上接近 Fixed Underlay，说明 prediction 对 PU protection 有显著作用。

这个不是单纯结果描述，可以提升成一条贡献：不同频谱供需关系下，quality awareness 与 prediction awareness 的主导作用不同。

可修改位置：

- Introduction contributions。
- Performance Evaluation 开头。
- 每组结果后的 discussion。
- Conclusion。

建议新增一个小节：

`\subsection{Regime-Dependent Contribution Analysis}`

建议核心表述：

- Under spectrum scarcity, channel quality becomes the bottleneck because VTs have limited idle choices; therefore, DQI-aware ranking contributes more to VT throughput.
- Under spectrum abundance, access failures are dominated by PU returns and sensing uncertainty; therefore, prediction contributes more to PLR reduction and PU protection.
- This observation explains why the proposed framework uses both modules instead of relying on quality evaluation or prediction alone.

这条路线的好处是：它不需要你声称模型本身全新，而是强调你发现并验证了 CVN DSA 中一个设计规律。

### 5. 方向四：把 ESN-DDQN 的新意从“算法新”改成“动作空间匹配和快速决策适配”

Reviewer 3 明确问：为什么 DDQN，不是 DDPG、SAC、TD3？这里不能硬说 DDQN 比所有方法先进，而要从动作空间性质解释。

当前动作由 channel selection 和 access mode selection 组成，本质是离散或组合离散动作。DDPG、TD3、SAC 更常用于连续动作控制，若直接用于本文问题，需要额外的离散化或 action mapping。DDQN 对离散 channel-mode action 更自然。

ESN 的定位也要调整。不要说 ESN-RL 全新，而要说：

- Reservoir computing reduces recurrent training overhead because only readout weights are trained.
- This is suitable for frequently updated access policies in high-mobility CVNs.
- The novelty is not the ESN itself, but its integration with the proposed quality-prediction state and differentiated overlay/underlay reward.

可推进修改：

- 在 Section IV-C 前增加一段 “Rationale for ESN-DDQN”。
- 在 Related Work 中补充 reservoir-computing RL 的已有工作，并明确本文区别。
- 在实验中加入 DDQN、PPO 或 no-ESN DDQN baseline，避免只和 Q-learning/MLP/LSTM 比。

### 6. 方向五：把 DQI 从“Transformer 模块”改成“有目标的 link-quality estimator”

Reviewer 1 和 Reviewer 3 对 DQI 的质疑会直接影响创新性，因为如果 DQI 只是一个 Transformer 输出分数，就很像过度设计。

建议把 DQI 的创新点从 “we use Transformer” 改成 “we define and learn a normalized link-quality indicator for pre-access decision making”。

可推进修改：

- 定义 DQI target，例如 normalized achievable rate、packet success probability、或综合 SNR/RSS/B 的 pseudo-label。
- 给出 loss function，例如 MSE 或 binary/categorical cross entropy，取决于 DQI target。
- 增加 DQI validation，例如 DQI 与 achievable throughput 的 correlation，或 DQI-ranking accuracy。
- 增加 simple DQI baseline，例如 weighted-sum DQI 或 MLP-DQI。
- 如果暂时不增加 Doppler/latency，可以在模型扩展中说明 DQI feature vector 可扩展为 `[SNR, RSS, bandwidth, Doppler, latency]`。

这条路线会同时回应创新性和方法严谨性问题。

### 7. 方向六：增加“约束式 underlay 接入”作为系统创新点

当前 underlay reward 被审稿人抓得很重。如果后续 WP3 能把 underlay power control、PU threshold、interference violation penalty 写清楚，它可以反过来成为创新点的一部分。

可推进表述：

- 本文不是简单让 agent 在 overlay/underlay 之间切换，而是在 PU protection constraint 下进行 channel-mode-power-aware access。
- Underlay access is rewarded only when the interference constraint is satisfied; violation is explicitly penalized.
- This makes the adaptive policy PU-protection-aware rather than purely VT-throughput-driven.

需要配套修改：

- 重写 reward equations。
- 增加 interference violation rate 指标。
- 增加 underlay power-control rule。
- 增加 estimation error robustness。

如果这条做好，创新性会从“模型组合”转向“受约束接入机制设计”。

### 8. 建议优先级

建议优先推进以下组合：

1. 主线定位重写：从 model-centric 改为 problem-centric。
2. Related Work 缺口矩阵：让创新点有证据地站出来。
3. Regime-dependent insight：把已有 ablation 变成设计规律。
4. ESN-DDQN rationale：解释为什么是 DDQN 和 ESN，而不是泛泛堆模型。
5. DQI objective 和 underlay constraint：把两个最被质疑的模块变成可 defend 的技术贡献。

如果只改文字，不补实验，最多只能缓解 Reviewer 2 的意见，很难说服 Reviewer 3 和 Reviewer 4。若目标是按 TVT 重投，创新性重写必须和新增实验绑定推进。

### 9. 可以和导师讨论的具体选项

选项 A：保守重写。

保持现有方法基本不变，主要重写 title、abstract、introduction、related work、conclusion，弱化算法新意，强调系统框架和消融 insight。

适合情况：不想投入太多新实验，后续可能转投。

选项 B：TVT 标准重写。

在选项 A 基础上，补充 DQI objective、underlay constraint、strong DRL baseline、larger-scale experiments、PU violation rate 和 robustness tests。

适合情况：继续冲 TVT。

选项 C：方法升级重写。

不仅补实验，还将方法从 “Transformer + LSTM + ESN-DDQN” 改造成更统一的 constrained RL 或 multi-agent RL 框架。

适合情况：准备投入较长时间，但风险是工作量大，可能偏离你博士主线。

## English Version: Actionable Directions for Improving Novelty Framing

### 1. Why the Current Manuscript Looks Like AI-Module Stacking

Based on the current `main.tex`, the novelty issue is not that the manuscript has no contribution. The main problem is that the contribution is presented in a model-centric way.

In the abstract, the manuscript sequentially emphasizes Transformer-based DQI, attention-enhanced LSTM, and ESN-assisted DDQN. This makes reviewers first notice a sequence of existing AI models rather than the underlying CVN/DSA design problem.

In the contribution list, Contribution 1 emphasizes Transformer self-attention, Contribution 2 emphasizes a novel ESN-DDQN network, and Contribution 3 emphasizes performance results. This structure can easily be interpreted as combining existing models and reporting simulation gains.

In the Related Work section, the manuscript is organized by MDP, game theory, and RL, but it does not provide a sharp gap matrix. It does not clearly show which prior studies lack quality awareness, prediction, adaptive overlay/underlay switching, PU-protection-aware reward design, fast convergence, or deployment consideration.

In the experiments, the current ablation results actually support a potentially valuable insight: DQI is more influential under `M<N`, while prediction is more influential under `M>N`. However, this insight is currently scattered in figure-level descriptions rather than elevated into a system-level design principle.

### 2. Direction 1: Reposition the Paper as a CVN-Constrained Quality-Prediction-Protection Framework

This is the most recommended main direction.

The current title and contribution framing may lead reviewers to expect a fundamentally new RL algorithm. Since ESN, DDQN, LSTM, and Transformer are all existing techniques, a safer strategy is to acknowledge that these are implementation components and emphasize the CVN-specific system design.

Target locations:

- Title.
- Abstract.
- Final paragraphs of Introduction and contribution list.
- Related Work summary.
- Conclusion.

Actionable framing:

- Avoid leading with “a novel ESN-DDQN algorithm”.
- Use “a quality- and prediction-aware adaptive overlay/underlay access framework”.
- Emphasize three coupled conflicts: idle does not imply usable, prediction does not imply quality, and underlay opportunity does not imply PU-safe access.
- Present Transformer/LSTM/ESN-DDQN as technical components used to realize the framework, not as the novelty itself.

Possible contribution wording:

1. We formulate a multi-timescale pre-access state representation that combines instantaneous sensing, medium-term channel quality, and short-horizon occupancy prediction for CVN DSA.
2. We design an interference-aware adaptive overlay/underlay access mechanism with differentiated reward modeling and PU-protection constraints.
3. We develop an ESN-assisted DDQN implementation for fast discrete channel-mode decision making under the proposed state and reward design.
4. We quantify regime-dependent module contributions, showing that quality awareness is more important under spectrum scarcity while prediction dominates interruption avoidance and PU protection under spectrum abundance.

### 3. Direction 2: Add a Gap Matrix to Related Work

The current Related Work is organized clearly, but the gap is not sharp enough. TVT reviewers will naturally ask why this paper is needed if RL, DRL, ESN-RL, and LSTM-based access have already been studied.

Suggested comparison dimensions:

- CVN-oriented DSA.
- Quality-aware channel evaluation.
- Occupancy prediction.
- Adaptive overlay/underlay switching.
- PU interference protection.
- Fast convergence or low training overhead.
- Deployment/overhead discussion.

Actionable revision:

- Convert or complement Table I with a feature comparison table.
- Keep the MDP/game/RL taxonomy, but add a feature matrix.
- After the table, explicitly state that existing work usually covers only part of these dimensions, while this paper targets their joint satisfaction under high-mobility CVN constraints.

### 4. Direction 3: Promote Existing Ablation Results Into Regime-Dependent Design Insights

This is one of the strongest existing seeds in the manuscript.

The current evaluation already suggests:

- Under `M<N`, DQI has a stronger impact on VT throughput.
- Under `M>N`, prediction has a stronger impact on PLR and PU protection.
- No-Prediction approaches Fixed Underlay in PU throughput, indicating that prediction is critical for incumbent protection.

This can be elevated from result description to a contribution.

Target locations:

- Contribution list in Introduction.
- Opening of Performance Evaluation.
- Discussion after result groups.
- Conclusion.

Suggested new subsection:

`\subsection{Regime-Dependent Contribution Analysis}`

Core message:

- Under spectrum scarcity, channel quality becomes the bottleneck because VTs have limited idle choices; DQI-aware ranking contributes more to VT throughput.
- Under spectrum abundance, access failures are dominated by PU returns and sensing uncertainty; prediction contributes more to PLR reduction and PU protection.
- This explains why the proposed framework uses both quality evaluation and prediction instead of either one alone.

### 5. Direction 4: Reframe ESN-DDQN as Action-Space-Matched Fast Decision Implementation

Reviewer 3 asked why DDQN is used instead of DDPG, SAC, or TD3. The answer should not be that DDQN is universally better. It should be based on action-space structure.

The action consists of channel selection and access-mode selection, which is naturally discrete or combinatorial-discrete. DDPG, TD3, and SAC are often used for continuous control and would require additional action discretization or mapping for this problem. DDQN is more natural for discrete channel-mode decisions.

ESN should also be reframed. Do not claim ESN-RL itself is new. Instead, state that:

- Reservoir computing reduces recurrent training overhead because only readout weights are trained.
- This is suitable for frequently updated access policies in high-mobility CVNs.
- The contribution lies in integrating ESN-DDQN with the proposed quality-prediction state and differentiated overlay/underlay reward.

Actionable revision:

- Add a “Rationale for ESN-DDQN” paragraph before Section IV-C.
- Discuss reservoir-computing RL in Related Work and clarify the difference.
- Add a DDQN, PPO, or no-ESN DDQN baseline in experiments.

### 6. Direction 5: Turn DQI From a Transformer Module Into a Link-Quality Estimator With an Objective

The DQI issue directly affects novelty because an undefined Transformer-generated score looks like over-engineering.

Suggested repositioning:

- From “we use Transformer” to “we define and learn a normalized link-quality indicator for pre-access decision making”.

Actionable revision:

- Define a DQI target, such as normalized achievable rate, packet success probability, or a pseudo-label from normalized SNR/RSS/bandwidth.
- Provide a loss function, such as MSE or cross entropy depending on the target.
- Add DQI validation, such as correlation with achievable throughput or DQI-ranking accuracy.
- Add a simple DQI baseline, such as weighted-sum DQI or MLP-DQI.
- If Doppler/latency cannot be added immediately, state that the feature vector can be extended to `[SNR, RSS, bandwidth, Doppler, latency]`.

### 7. Direction 6: Use Constrained Underlay Access as a System-Level Contribution

The underlay reward is currently a reviewer concern, but if WP3 is revised well, it can become part of the novelty story.

Actionable framing:

- The paper does not simply let the agent switch between overlay and underlay.
- It performs channel-mode-power-aware access under PU-protection constraints.
- Underlay access is rewarded only when the interference constraint is satisfied, and violations are explicitly penalized.
- This makes the adaptive policy PU-protection-aware rather than purely VT-throughput-driven.

Required supporting changes:

- Rewrite reward equations.
- Add interference violation rate.
- Add an underlay power-control rule.
- Add estimation-error robustness.

### 8. Recommended Priority

Recommended order:

1. Reframe the main story from model-centric to problem-centric.
2. Add a Related Work gap matrix.
3. Promote ablation results into regime-dependent design insights.
4. Add ESN-DDQN rationale based on discrete action-space matching.
5. Formalize DQI and constrained underlay access so that the two most questioned modules become defensible technical contributions.

If only the writing is changed without new experiments, the revision may partially address Reviewer 2 but is unlikely to convince Reviewers 3 and 4. If TVT resubmission remains the goal, the novelty reframing must be coupled with experimental strengthening.

### 9. Advisor Discussion Options

Option A: Conservative reframing.

Keep the current method mostly unchanged. Rewrite the title, abstract, introduction, related work, and conclusion. De-emphasize algorithmic novelty and emphasize system framework and ablation insights.

Suitable if the goal is mainly transfer submission.

Option B: TVT-level reframing.

Build on Option A and add DQI objective, constrained underlay access, a strong DRL baseline, larger-scale experiments, PU violation rate, and robustness tests.

Suitable if the goal is still TVT.

Option C: Method-level upgrade.

Go beyond additional experiments and redesign the method toward constrained RL or multi-agent RL.

Suitable only if substantial time can be invested, but it may deviate from the current PhD research focus.

