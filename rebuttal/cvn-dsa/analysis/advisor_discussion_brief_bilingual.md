# TVT Resubmission Revision Direction Discussion Brief

## 中文版：给博导讨论用

### 1. 当前决定与总体判断

编辑决定为拒稿，但允许在 120 天内作为新稿件重投，并要求引用原稿件编号 `VT-2026-02444`，同时提交针对 AE 和审稿人意见的修改总结。重投后会进入新的审稿流程。

从 4 位审稿人的意见看，本次拒稿不是格式或语言问题，而是实质性技术问题。审稿人集中质疑本文的创新性、方法严谨性、实验充分性和工程可部署性。若按 TVT 重投标准修改，不能只做文字润色，需要进行一次较完整的大修。

### 2. 审稿人意见的共性问题

#### 问题一：创新性表达不足

多位审稿人认为本文目前更像是把 Transformer、LSTM、ESN 和 DDQN 组合到一个 CVN/DSA 场景中，而不是提出了足够清晰的概念创新或方法创新。尤其是 Reviewer 3 和 Reviewer 4 明确指出，ESN-RL 并非全新，整体框架存在“堆叠 AI 模块”的印象。

建议讨论点：

- 本文的核心贡献是否应从“提出新算法”改为“面向 CVN 的质量感知、预测辅助、overlay/underlay 自适应接入框架”。
- 是否需要弱化“fundamentally new”的表达，改为强调场景适配、模块协同、奖励机制和 PU 保护。
- 是否有能力补充更强实验来证明各模块不是简单堆叠，而是对不同频谱状态有明确贡献。

#### 问题二：DQI 模块定义不严谨

Reviewer 1 明确追问 Transformer-based DQI 如何训练，包括 target、loss function、training data。Reviewer 3 进一步质疑只有 SNR、RSS、bandwidth 三个低维特征时是否需要 Transformer，是否存在过度设计。

建议讨论点：

- DQI 是否有真实标签，还是根据可达速率、链路成功率、SNR/RSS/B 的加权指标构造伪标签。
- 是否可以给出明确的 DQI 训练目标，例如让 DQI 拟合 normalized achievable link quality。
- 是否需要增加一个简单 DQI baseline，例如 weighted-sum DQI、MLP-DQI 或 no-attention model，来证明 Transformer 的必要性。
- 是否应扩展 DQI 特征，加入 Doppler、latency、vehicle speed 或 channel coherence indicators。

#### 问题三：Reward 与 underlay 模型存在硬伤风险

Reviewer 1 指出 reward 公式可能有歧义甚至错误，尤其是 overlay 中 DQI 强调项的表达不清楚。Reviewer 1 和 Reviewer 3 都关注 underlay 场景下 SU-PU channel gain、PU interference threshold 和 power control 的现实可获得性。Reviewer 3 还指出 underlay reward 可能让智能体偏向 underlay access，缺少公平性或 PU 保护约束。

建议讨论点：

- 是否需要重写 overlay/underlay reward，使公式和仿真代码完全一致。
- underlay power 是否应采用闭式约束，例如 `P_t^{i,j} <= Psi_t^{j,PU} / |h_t^{i,PU}|^2`。
- 是否应加入 interference violation penalty，避免只要 underlay 成功就给正奖励。
- SU-PU channel gain 和 PU threshold 的获得方式应如何解释，是 BS/RSU 估计、PU 协作、路径损耗代理，还是仿真假设。
- 是否需要增加 estimation error robustness 实验。

#### 问题四：实验强度不足以支撑 TVT

当前实验主要是 `M=3,N=5` 和 `M=5,N=3` 两类小规模配置。Reviewer 1 和 Reviewer 3 都要求更大规模网络、不同 `p01/p10`、更严苛 mobility、置信区间或标准差。Reviewer 2 和 Reviewer 3 都要求增加更强的 DRL baseline，例如 DQN、PPO、SAC、DDPG 或 multi-agent RL。

建议讨论点：

- 是否有时间补充至少一个强 DRL baseline。考虑到动作空间是离散的，DQN/DDQN/PPO 可能比 DDPG/SAC/TD3 更容易解释。
- 是否可以补充大规模设置，例如 `M=10,N=20`、`M=20,N=50` 或至少比当前更密集的 CVN 场景。
- 是否可以补充 multiple random seeds，报告 mean ± std 或 confidence interval。
- 是否可以补充 PU interference violation rate、prediction error robustness、sensing error robustness。
- 是否需要补充 varied PU traffic，例如不同 `p01/p10`，或非 Markov traffic 的讨论。

#### 问题五：工程部署和开销分析不足

Reviewer 2 和 Reviewer 4 都指出 centralized server、communication overhead、latency、descriptor staleness、5G NR-V2X/6G compatibility 没有充分讨论。Reviewer 1 也要求量化 DQI/prediction summary 的广播开销，以及 `T_upd/T_stat` 敏感性。

建议讨论点：

- 是否将 centralized server 解释为 MEC/edge server 或 RSU-assisted architecture。
- 是否增加通信开销公式，例如每次广播 `M` 个 DQI 和 `M` 个 prediction probability，量化 payload size。
- 是否分析 `T_upd` 增大时 performance degradation。
- 是否加入 computation complexity vs performance gain 的对比表。

### 3. 建议的 TVT 重投级修改路线

若目标是按 TVT 重投标准修改，建议采用以下顺序：

1. WP3：先修 reward 与 underlay feasibility。这是技术正确性问题，会直接影响审稿人对结果的信任。
2. WP2：形式化 DQI 模块。明确 target、loss、training data，并解释 Transformer 的必要性。
3. WP4：补充实验。优先补强 baseline、大规模场景、统计结果、PU violation、prediction/sensing error robustness。
4. WP5：补充部署、复杂度、通信开销和时延分析。
5. WP1：最后重写 Abstract、Introduction、Related Work 和 Conclusion，把创新性故事重新讲清楚。
6. WP6：全文语言精修，并准备 response letter。

### 4. 需要导师拍板的问题

1. 是否继续以 TVT 为目标重投，接受较大实验和重写工作量。
2. 是否允许将本文定位从“新型 ESN-DDQN 算法”调整为“面向 CVN 的质量感知与预测辅助自适应接入框架”。
3. 是否有条件补充新的仿真实验，包括强 DRL baseline、大规模场景和鲁棒性分析。
4. 是否需要引入新的理论分析，还是以复杂度分析、消融实验和系统级 insight 为主。
5. 是否接受将部分限制写入 manuscript，例如 centralized architecture、DQI 特征范围、simulation-only validation。

### 5. 我的建议

建议按“求上得中”的策略修改，即先按 TVT 重投标准做一轮实质性增强。即使最终不重投 TVT，这些修改也会显著提升论文质量，后续转投其他英文期刊时也更稳。

但需要注意：如果不补新实验，只做文字解释，Reviewer 3 和 Reviewer 4 的核心质疑很难被说服。因此，若决定重投 TVT，至少应补充一个强 DRL baseline、一组更大规模场景、统计置信结果、PU interference violation rate 和 prediction/sensing error robustness。

## English Version: For Later Technical Planning

### 1. Current Decision and Overall Assessment

The editor rejected the current manuscript but allows resubmission as a new submission within 120 days. The resubmission should refer to the original manuscript number `VT-2026-02444` and include a summary of changes made in response to the AE and reviewers. The manuscript will undergo a new review process.

Based on the comments from the four reviewers, this rejection is not mainly about formatting or language. The major concerns are technical: novelty, methodological rigor, experimental sufficiency, and deployment feasibility. If the target remains TVT, the manuscript requires a substantive revision rather than a light polishing pass.

### 2. Common Concerns Across Reviewers

#### Concern 1: Insufficiently Articulated Novelty

Several reviewers considered the current manuscript as an integration of Transformer, LSTM, ESN, and DDQN rather than a clearly novel conceptual or methodological contribution. Reviewers 3 and 4 explicitly stated that ESN-RL is not fundamentally new and that the framework may look like stacked AI modules.

Discussion points:

- Should the core contribution be reframed from a new algorithm to a CVN-specific quality-aware, prediction-assisted, overlay/underlay adaptive access framework?
- Should the manuscript avoid claiming fundamental algorithmic novelty and instead emphasize scenario-specific design, module coordination, reward design, and PU protection?
- Can we add stronger experiments to show that the modules are necessary and contribute differently under different spectrum regimes?

#### Concern 2: Under-Specified DQI Module

Reviewer 1 asked how the Transformer-based DQI is trained, including targets, loss function, and training data. Reviewer 3 further questioned whether attention is necessary for low-dimensional features such as SNR, RSS, and bandwidth.

Discussion points:

- Does DQI have ground-truth labels, or should pseudo-labels be constructed from achievable rate, link success probability, or weighted normalized SNR/RSS/bandwidth?
- Can we define a clear DQI objective, such as fitting normalized achievable link quality?
- Should we add a simple DQI baseline, such as weighted-sum DQI, MLP-DQI, or a no-attention model, to justify the Transformer module?
- Should we extend the DQI features to include Doppler, latency, vehicle speed, or channel coherence indicators?

#### Concern 3: Reward and Underlay Feasibility Risks

Reviewer 1 pointed out ambiguity and possible errors in the reward definitions. Reviewers 1 and 3 questioned the practicality of obtaining SU-PU channel gain, PU interference thresholds, and underlay power control. Reviewer 3 also noted that positive underlay rewards may bias the agent toward underlay access without explicit fairness or PU-protection constraints.

Discussion points:

- Should the overlay and underlay rewards be rewritten to exactly match the simulation code?
- Should underlay power be constrained in closed form, for example `P_t^{i,j} <= Psi_t^{j,PU} / |h_t^{i,PU}|^2`?
- Should an interference violation penalty be added to avoid rewarding underlay access whenever it succeeds?
- How should the acquisition of SU-PU channel gain and PU thresholds be explained: BS/RSU estimation, PU cooperation, path-loss proxy, or simulation assumption?
- Should an estimation-error robustness experiment be added?

#### Concern 4: Experimental Evidence Below TVT Expectations

The current experiments mainly use two small settings, `M=3,N=5` and `M=5,N=3`. Reviewers 1 and 3 requested larger networks, different `p01/p10`, harsher mobility, and standard deviations or confidence intervals. Reviewers 2 and 3 requested stronger DRL baselines such as DQN, PPO, SAC, DDPG, or multi-agent RL.

Discussion points:

- Can we add at least one stronger DRL baseline? Given the discrete action space, DQN/DDQN/PPO may be easier to justify than DDPG/SAC/TD3.
- Can we add larger settings such as `M=10,N=20`, `M=20,N=50`, or at least denser CVN scenarios than the current setup?
- Can we run multiple random seeds and report mean ± standard deviation or confidence intervals?
- Can we add PU interference violation rate, prediction-error robustness, and sensing-error robustness?
- Should we test varied PU traffic with different `p01/p10`, or discuss non-Markov traffic models?

#### Concern 5: Insufficient Deployment and Overhead Analysis

Reviewers 2 and 4 raised concerns about centralized processing, communication overhead, latency, descriptor staleness, and compatibility with 5G NR-V2X or 6G architectures. Reviewer 1 also requested overhead quantification for DQI/prediction broadcasting and sensitivity to `T_upd/T_stat`.

Discussion points:

- Should the centralized server be interpreted as an MEC/edge server or RSU-assisted architecture?
- Should we add a communication overhead formula, e.g., broadcasting `M` DQI values and `M` prediction probabilities per update?
- Should we analyze performance degradation as `T_upd` increases?
- Should we add a computation-complexity versus performance-gain table?

### 3. Recommended TVT-Level Revision Route

If the goal is to revise toward TVT resubmission, the following order is recommended:

1. WP3: Fix reward and underlay feasibility first. This is a technical correctness issue and directly affects reviewer trust.
2. WP2: Formalize the DQI module by defining targets, loss, training data, and the necessity of Transformer attention.
3. WP4: Strengthen experiments with stronger baselines, larger settings, statistical reporting, PU violation metrics, and prediction/sensing robustness.
4. WP5: Add deployment, complexity, communication overhead, and latency analysis.
5. WP1: Rewrite the abstract, introduction, related work, and conclusion to rebuild the novelty story.
6. WP6: Polish the full manuscript and prepare the response letter.

### 4. Decisions Needed From the Advisor

1. Whether to continue targeting TVT and accept the workload of substantial experiments and rewriting.
2. Whether to reposition the paper from a new ESN-DDQN algorithm to a CVN-oriented quality-aware and prediction-assisted adaptive access framework.
3. Whether new simulations can be added, including stronger DRL baselines, larger-scale settings, and robustness analysis.
4. Whether theoretical analysis should be added, or whether complexity analysis, ablation evidence, and system-level insights are sufficient.
5. Whether to explicitly acknowledge limitations such as centralized architecture, limited DQI features, and simulation-only validation.

### 5. Recommendation

I recommend revising according to a high-standard TVT resubmission target first. Even if the paper is later transferred to another English journal, these revisions will substantially improve its technical credibility.

However, a text-only revision is unlikely to satisfy the core concerns of Reviewers 3 and 4. If TVT resubmission is pursued, the manuscript should at least add one strong DRL baseline, larger-scale settings, statistical confidence results, PU interference violation rate, and prediction/sensing error robustness.

