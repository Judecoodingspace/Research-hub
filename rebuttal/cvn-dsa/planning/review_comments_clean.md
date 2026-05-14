# Reviewer Comments Clean

Note: The raw email text contains several mojibake/encoding artifacts for mathematical symbols. In this cleaned file, symbols are normalized according to the notation in `main.tex`, e.g., DQI as `\Phi`, interference/penalty as `\Omega`, and PU threshold as `\Psi`.

## Reviewer 1

### R1-C1

Reviewer concern:

The paper addresses an important problem and the architecture is plausible, but key elements are under-specified or internally inconsistent. The reviewer asks for major revision focusing on DQI learning, reward formulation, practical underlay interference estimation/control, stronger experiments, baselines, and statistical reporting.

Author note:

- Type: Overall major-revision diagnosis.
- Location: Whole paper, especially Sections III-V.
- Core action: Treat as the umbrella comment for the high-priority revision plan.

### R1-C2

Reviewer concern:

The Transformer-based DQI module lacks a defined training objective, targets, loss function, and training data. If unsupervised/self-supervised, the objective must explain why DQI correlates with achievable link quality.

Author note:

- Type: Method specification / model validity.
- Location: Section III-B, lines around 189-232.
- Core action: Define DQI target, data construction, normalization, loss, training procedure, and validation metric.

### R1-C3

Reviewer concern:

The reward in Eq. (12) is ambiguous or possibly erroneous. Clarify whether overlay uses a quality-emphasized term such as `\Phi_t = \Phi_t^\Gamma`, the exact reward used in code, and whether rewards are normalized or clipped.

Author note:

- Type: Formula correctness / reproducibility.
- Location: Section IV-B, lines around 267-331.
- Core action: Rewrite reward equations and make overlay/underlay reward definitions unambiguous.

### R1-C4

Reviewer concern:

The underlay feasibility assumes access to `|h_t^{i,PU}|^2` and `\Psi_t^{j,PU}` in high-mobility CVNs. Clarify whether these are obtained by BS-side estimation, PU cooperation, or model-based pathloss proxies, and evaluate sensitivity to estimation errors.

Author note:

- Type: Practical feasibility / robustness.
- Location: Sections III-A, IV-B, and V.
- Core action: Add acquisition assumptions and an estimation-error robustness experiment or limitation discussion.

### R1-C5

Reviewer concern:

Full ESN details are missing: reservoir size, spectral radius, input scaling, leak rate, activation, readout regularization, initialization, why ReLU rather than tanh, and how echo-state property is ensured.

Author note:

- Type: Reproducibility / algorithm detail.
- Location: Section IV-C and Table II.
- Core action: Add ESN hyperparameter table and justify activation/echo-state property.

### R1-C6

Reviewer concern:

The attention-LSTM predictor lacks architectural and training details, including layers, hidden sizes, attention formulation, optimizer, window length, and comparison to simpler predictors such as Markov, RF, and XGBoost in accuracy and compute.

Author note:

- Type: Reproducibility / baseline comparison.
- Location: Section III-C and Section V.
- Core action: Specify predictor architecture and add or justify predictor-level baselines.

### R1-C7

Reviewer concern:

The simulation model is under-specified: SNR/RSS/bandwidth generation, path loss, fading, mobility trajectories, queue sizes, traffic arrival rates, and sensing error models are missing.

Author note:

- Type: Experimental methodology.
- Location: Section V, lines around 420-433, and Table II.
- Core action: Add a simulation environment subsection/table with all assumptions and parameter values.

### R1-C8

Reviewer concern:

Underlay power control is unclear. Explain how `P_t^{i,j}` is selected to meet `\Psi_t^{j,PU}`, whether there is a control loop, discrete power levels, closed-form update, adaptation frequency, and latency.

Author note:

- Type: Underlay mechanism / practical deployment.
- Location: Section IV-B and possibly Section III-A.
- Core action: Define power control rule and timing model.

### R1-C9

Reviewer concern:

Report interference violation rates to PUs and robustness when occupancy predictions are wrong, e.g., controlled false-alarm or miss-detection scenarios.

Author note:

- Type: New evaluation.
- Location: Section V.
- Core action: Add PU interference violation metric and prediction-error robustness experiment if TVT resubmission is pursued.

### R1-C10

Reviewer concern:

Add standard deviations/confidence intervals and expand evaluations to larger `M,N`, varied `p01/p10`, and harsher mobility to demonstrate scalability and generality.

Author note:

- Type: Statistical reporting / scalability.
- Location: Section V.
- Core action: Add error bars or confidence intervals and larger/varied simulation settings.

### R1-C11

Reviewer concern:

Quantify communication overhead for broadcasting DQI and prediction summaries, and evaluate sensitivity to `T_upd/T_stat` and descriptor staleness.

Author note:

- Type: Practical overhead / sensitivity.
- Location: Section III-A, Section IV-D, and Section V.
- Core action: Add overhead formula and staleness sensitivity discussion or experiment.

## Reviewer 2

### R2-C1

Reviewer concern:

The motivation is clear, but the need for combining quality evaluation, prediction, and ESN-DDQN is qualitative. Provide quantitative evidence showing why existing RL-based DSA methods such as DQN/LSTM-DDQN are insufficient without the proposed multi-module design.

Author note:

- Type: Motivation / empirical justification.
- Location: Introduction and Section V.
- Core action: Add quantitative motivation and cross-reference ablation/convergence results.

### R2-C2

Reviewer concern:

The work integrates existing techniques, including Transformer, LSTM, ESN, and DDQN. The fundamental novelty is not fully articulated.

Author note:

- Type: Novelty.
- Location: Abstract, Introduction, Related Work, Conclusion.
- Core action: Reframe novelty around task-specific integration, reward/access-mode design, and CVN constraints, but avoid overstating fundamental algorithmic novelty.

### R2-C3

Reviewer concern:

The contributions are listed, but the distinction between incremental improvement and substantial advancement is weak. Quantify which component contributes most under different spectrum regimes using the ablation results.

Author note:

- Type: Contribution clarity / ablation analysis.
- Location: Introduction and Section V.
- Core action: Add a compact contribution-impact summary and regime-dependent ablation interpretation.

### R2-C4

Reviewer concern:

Related work lacks recent DRL-based wireless optimization or precoding works in RIS-enabled systems. Consider citing and discussing the provided 2025 IEEE WCL work in the context of DRL-based wireless optimization.

Author note:

- Type: Literature coverage.
- Location: Section II-C and bibliography.
- Core action: Add a short paragraph/citation after verifying bibliographic details.

### R2-C5

Reviewer concern:

The two-state Markov PU model with fixed transition probabilities is simplified. Discuss sensitivity to different PU traffic models or more realistic mobility/channel dynamics.

Author note:

- Type: Model realism / sensitivity.
- Location: Section V and limitations.
- Core action: Add varied `p01/p10` experiment or discussion.

### R2-C6

Reviewer concern:

The interaction among Transformer, LSTM, and ESN-DDQN modules is complex and difficult to follow.

Author note:

- Type: Organization / clarity.
- Location: Sections III-IV and Fig. 2.
- Core action: Add a pipeline overview, signal flow table, and clearer module input/output definitions.

### R2-C7

Reviewer concern:

Comparisons with other DRL baselines such as DQN, PPO, and DDPG are limited. Include at least one additional DRL baseline or justify why current baselines are sufficient.

Author note:

- Type: Baseline adequacy.
- Location: Section V.
- Core action: Add one DRL baseline, preferably DQN/DDQN/PPO depending on action-space compatibility, or give a strong justification.

### R2-C8

Reviewer concern:

The limitations of the proposed framework are not explicitly discussed, especially computational overhead, centralized processing dependence, scalability, and the trade-off between performance gain and model complexity. Provide quantitative comparisons if possible.

Author note:

- Type: Limitations / complexity.
- Location: Section IV-D, Section V, Conclusion.
- Core action: Add limitations subsection and complexity-performance trade-off discussion.

### R2-C9

Reviewer concern:

The centralized server assumption needs practical deployment discussion, including latency, signaling overhead, and compatibility with 5G NR-V2X or 6G architectures.

Author note:

- Type: Practical deployment.
- Location: Section III-A and limitations.
- Core action: Add architecture mapping to BS/edge server/RSU and discuss signaling/update latency.

### R2-C10

Reviewer concern:

Future work is underdeveloped. Discuss decentralized learning, multi-agent coordination, and more realistic vehicular deployments.

Author note:

- Type: Conclusion / future work.
- Location: Conclusion.
- Core action: Add a future-work paragraph.

### R2-C11

Reviewer concern:

Some sentences, especially in the Introduction and System Model, are too long and affect readability.

Author note:

- Type: Writing clarity.
- Location: Sections I and III.
- Core action: Split long sentences and improve readability after technical revisions.

## Reviewer 3

### R3-C1

Reviewer concern:

The use of ESN in RL is not fundamentally new. Clarify how ESN-DDQN differs from prior reservoir-computing-based DRL, and justify DDQN rather than DDPG, SAC, or TD3.

Author note:

- Type: Novelty / algorithm choice.
- Location: Introduction, Related Work, Section IV-C.
- Core action: Add comparison to reservoir-computing RL and explain discrete action-space suitability of DDQN.

### R3-C2

Reviewer concern:

The Transformer + LSTM + ESN-DDQN combination is complex. Explain feasibility because marginal gains over simpler unified architectures may not justify the complexity.

Author note:

- Type: Complexity-performance trade-off.
- Location: Sections III-IV and V.
- Core action: Add complexity comparison and ablation-based justification.

### R3-C3

Reviewer concern:

Transformer-based DQI is applied to low-dimensional features (SNR, RSS, bandwidth), which may not require attention and may be over-engineered.

Author note:

- Type: Model choice / over-engineering.
- Location: Section III-B and Section V.
- Core action: Justify cross-channel/temporal attention or add a simpler DQI baseline.

### R3-C4

Reviewer concern:

Channel quality modeling only uses SNR, RSS, and bandwidth; it should include critical CVN factors such as Doppler effects or latency constraints.

Author note:

- Type: Model completeness.
- Location: Section III-B and limitations.
- Core action: Add Doppler/latency discussion, possibly as extended features or limitation/future work.

### R3-C5

Reviewer concern:

The state vector includes sensing outcome, DQI, and prediction simultaneously, possibly introducing correlated or redundant information without feature-selection analysis.

Author note:

- Type: State design / redundancy.
- Location: Section IV-A and Section V.
- Core action: Justify complementary roles and use ablation/correlation discussion.

### R3-C6

Reviewer concern:

Under underlay mode, rewards can remain positive under interference constraints, which may bias the agent toward underlay access without explicit fairness constraints.

Author note:

- Type: Reward design / fairness.
- Location: Section IV-B.
- Core action: Add interference violation penalty/fairness term or clarify threshold-compliant reward logic.

### R3-C7

Reviewer concern:

Experiments use small configurations such as `M=3,5` and `N=3,5`, limiting scalability validation for dense vehicular scenarios.

Author note:

- Type: Scalability experiment.
- Location: Section V.
- Core action: Add larger settings if pursuing TVT; otherwise acknowledge as limitation for transfer submission.

### R3-C8

Reviewer concern:

Baselines include Q-learning, MLP-DDQN, and LSTM-DDQN, but not recent advanced DRL methods such as PPO, SAC, or multi-agent RL.

Author note:

- Type: Baseline adequacy.
- Location: Section V-C/convergence section.
- Core action: Add/justify advanced DRL baseline; coordinate with R2-C7.

### R3-C9

Reviewer concern:

The problem and solution are well known, definitions are inconsistent, modeling is simplified, and novelty is unclear. Without significant algorithmic enhancement and comprehensive V2X evaluation, e.g., real devices or USRP, the work remains early-stage.

Author note:

- Type: Fundamental suitability / high risk.
- Location: Whole paper.
- Core action: Use this as a strategic warning. TVT resubmission requires substantial experiments and stronger novelty framing; low-effort revision is unlikely to satisfy this reviewer.

## Reviewer 4

### R4-C1

Reviewer concern:

The contribution is not fully convincing. The paper appears to stack well-known AI techniques rather than developing a conceptual or methodological advance for DSA or vehicular networks.

Author note:

- Type: Novelty / contribution framing.
- Location: Abstract, Introduction, Related Work, Conclusion.
- Core action: Reframe as a CVN-specific quality-prediction-aware access framework and clarify what is new beyond module stacking.

### R4-C2

Reviewer concern:

The paper relies almost entirely on simulation results. There is no theoretical analysis explaining why the method should work better, no optimality/convergence guarantee, and limited deeper system insight.

Author note:

- Type: Analytical grounding.
- Location: Section IV-D and Section V.
- Core action: Add qualitative theoretical rationale, complexity/convergence discussion, and avoid unsupported optimality claims.

### R4-C3

Reviewer concern:

Practicality is insufficiently discussed. The framework uses heavy components but lacks analysis of computational cost, communication overhead, latency, and deployment feasibility in vehicular environments.

Author note:

- Type: Practical deployment / overhead.
- Location: Sections III-A, IV-D, V, Conclusion.
- Core action: Add overhead and latency analysis; coordinate with R1-C11, R2-C8, R2-C9.

### R4-C4

Reviewer concern:

Overall, the contribution feels incremental and lacks enough new insight, theoretical depth, or system-level impact for publication in the current form.

Author note:

- Type: Overall suitability.
- Location: Whole paper.
- Core action: Decide whether to invest in a TVT-level overhaul or redirect to a more suitable venue after moderate revision.

