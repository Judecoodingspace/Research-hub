# Revision Matrix

Decision context: The editor rejected the current version but allows a new submission within 120 days, referencing manuscript `VT-2026-02444`. The resubmitted manuscript will undergo a new review process.

Severity scale:

- Critical: Must be addressed for any serious TVT resubmission.
- Major: Important for technical credibility and reviewer confidence.
- Minor: Writing, formatting, or localized clarification.

| ID | Reviewer concern | Problem type | Severity | Manuscript location | Required action | Need new experiment? | Response strategy | Status |
|---|---|---|---|---|---|---|---|---|
| R1-C1 | Overall: under-specified DQI, ambiguous reward, unrealistic underlay knowledge, weak experiments/baselines/statistics | Overall technical rigor | Critical | Whole paper | Use as umbrella for full revision plan | Yes | Acknowledge and summarize major changes across method and experiments | Todo |
| R1-C2 | DQI lacks target, loss, data, and validation | Method validity | Critical | Section III-B | Define DQI learning objective, targets, training data, normalization, loss, and validation | Preferably yes | Explain DQI is trained/constructed to correlate with achievable link quality | Todo |
| R1-C3 | Reward equations ambiguous or possibly wrong | Formula correctness | Critical | Section IV-B | Rewrite overlay/underlay rewards, normalize notation, state code-consistent reward and clipping/normalization | No, unless reward rerun needed | Admit ambiguity and provide corrected equations | Todo |
| R1-C4 | Underlay requires hard-to-obtain SU-PU channel and PU threshold | Practical feasibility | Critical | Sections III-A, IV-B, V | Clarify estimation source and add estimation-error robustness or limitation | Yes for TVT | State practical acquisition model and quantify sensitivity | Todo |
| R1-C5 | Missing ESN details and echo-state justification | Reproducibility | Major | Section IV-C, Table II | Add ESN hyperparameters and explain activation/echo-state property | No | Provide complete configuration table | Todo |
| R1-C6 | Missing attention-LSTM architecture and predictor baselines | Reproducibility / baseline | Major | Section III-C, V | Specify architecture and compare/justify simpler predictors | Preferably yes | Show predictor module is not a black box | Todo |
| R1-C7 | Simulation environment under-specified | Experimental methodology | Critical | Section V | Add path loss, fading, mobility, queue, arrival, sensing error, SNR/RSS/B details | No if parameters exist; yes if missing | Provide full simulation setup table | Todo |
| R1-C8 | Underlay power control unclear | Mechanism design | Critical | Section IV-B | Define closed-form/discrete power selection and adaptation timing | No, if model-based | Clarify how PU threshold is enforced | Todo |
| R1-C9 | Need PU interference violation and prediction-error robustness | Robustness evaluation | Critical | Section V | Add violation-rate metric and false-alarm/miss robustness | Yes | Demonstrate PU protection under imperfect prediction | Todo |
| R1-C10 | Need std/CI and larger/varied settings | Statistical/scalability evaluation | Critical | Section V | Add confidence intervals, larger `M,N`, varied `p01/p10`, harsher mobility | Yes | Show generality beyond two small settings | Todo |
| R1-C11 | Need communication overhead and staleness sensitivity | Practical overhead | Major | Sections III-A, IV-D, V | Quantify broadcast payload and test/discuss `T_upd/T_stat` sensitivity | Preferably yes | Show offloading overhead is controlled | Todo |
| R2-C1 | Motivation for multi-module design is qualitative | Motivation / evidence | Major | Introduction, V | Add quantitative motivation from ablations/convergence | No if using existing results | Explain why single-module RL is insufficient | Todo |
| R2-C2 | Fundamental novelty not articulated | Novelty framing | Critical | Abstract, I, II, VI | Rewrite novelty claims to emphasize CVN-specific joint design and reward/access-mode coupling | No | Avoid overclaiming; state actual contribution precisely | Todo |
| R2-C3 | Incremental vs substantial advancement unclear | Contribution clarity | Major | Introduction, V | Add component-impact summary by spectrum regime | No | Use ablation results to quantify component roles | Todo |
| R2-C4 | Missing recent DRL wireless/RIS work | Literature coverage | Minor/Major | Section II-C | Add and discuss the provided 2025 IEEE WCL citation after verification | No | Position it as related DRL wireless optimization, not direct DSA baseline | Todo |
| R2-C5 | PU model is simplified | Model realism | Major | Section V, limitations | Add sensitivity to `p01/p10` or discuss alternate traffic/mobility | Preferably yes | State scope and robustness across traffic dynamics | Todo |
| R2-C6 | Module interaction difficult to follow | Organization clarity | Major | Sections III-IV, Fig. 2 | Add pipeline overview/table with inputs/outputs/update rates | No | Reduce cognitive load for reviewers | Todo |
| R2-C7 | Need additional DRL baseline or justification | Baseline adequacy | Critical | Section V | Add at least DQN/DDQN/PPO-style baseline or justify action-space constraints | Yes for TVT | Show fair comparison against modern RL | Todo |
| R2-C8 | Limitations and complexity trade-off missing | Limitations/practicality | Major | IV-D, V, VI | Add limitation subsection and quantitative complexity-performance trade-off | Preferably yes | Acknowledge deployment costs honestly | Todo |
| R2-C9 | Centralized server deployment not discussed | Practical deployment | Major | III-A, limitations | Map to BS/RSU/edge/5G NR-V2X/6G and discuss latency/signaling | No | Clarify architecture is implementable as edge-assisted control | Todo |
| R2-C10 | Future work insufficient | Conclusion | Minor | VI | Add future work on decentralized learning, multi-agent coordination, realistic deployment | No | Concise future-work paragraph | Todo |
| R2-C11 | Long sentences hurt readability | Writing | Minor | I, III | Split long sentences and polish after technical edits | No | Mention manuscript was edited for clarity | Todo |
| R3-C1 | ESN-RL not new; justify DDQN vs DDPG/SAC/TD3 | Novelty/algorithm choice | Critical | I, II-C, IV-C | Add reservoir-RL distinction and explain discrete action suitability of DDQN | No | Position DDQN as appropriate for discrete channel/mode action | Todo |
| R3-C2 | Complexity may outweigh marginal gains | Complexity-performance | Critical | III-V | Add complexity/performance trade-off and simpler baseline comparison | Preferably yes | Use ablation/convergence to justify modules | Todo |
| R3-C3 | Transformer for low-dimensional features may be over-engineered | Model choice | Critical | III-B, V | Justify attention over cross-channel temporal descriptors or add simple DQI baseline | Preferably yes | Show Transformer is not just model stacking | Todo |
| R3-C4 | DQI lacks Doppler/latency factors | Model completeness | Major | III-B, limitations | Add discussion or extended feature formulation for Doppler/latency | Optional | Acknowledge current feature scope and extensibility | Todo |
| R3-C5 | State may contain correlated/redundant features | State design | Major | IV-A, V | Explain complementarity and use ablation/correlation discussion | Optional | Argue sensing/DQI/prediction carry different time-scale information | Todo |
| R3-C6 | Underlay reward may bias agent without fairness | Reward/fairness | Critical | IV-B | Add fairness/interference penalty or clarify threshold-compliant positive reward | Possibly yes if metric added | Show PU protection is explicit, not incidental | Todo |
| R3-C7 | Small `M,N` settings limit scalability | Scalability | Critical | V | Add larger dense settings | Yes for TVT | Demonstrate dense CVN behavior | Todo |
| R3-C8 | Need advanced DRL baselines | Baseline adequacy | Critical | V | Coordinate with R2-C7 baseline addition | Yes for TVT | Explain why chosen baseline is fair for discrete action setting | Todo |
| R3-C9 | Novelty unclear; modeling simplified; early stage without major enhancement | Fundamental suitability | Critical | Whole paper | Strategic decision: TVT overhaul requires new experiments and stronger story | Yes | If resubmitting TVT, address directly with major enhancements | Todo |
| R4-C1 | Contribution appears like stacking known AI tools | Novelty/story | Critical | Abstract, I, II, VI | Reframe around problem-specific access control insight and module necessity | No, but evidence helps | Avoid "tool stacking" perception | Todo |
| R4-C2 | Simulation-only evidence lacks theory/insight | Analytical grounding | Critical | IV-D, V | Add convergence/complexity rationale and deeper system insight; avoid optimality claims | Optional | Explain why method should help beyond plots | Todo |
| R4-C3 | Practicality, overhead, latency, deployment missing | Practical deployment | Critical | III-A, IV-D, V, VI | Add overhead/latency/deployment feasibility analysis | Preferably yes | Coordinate with R1-C11/R2-C8/R2-C9 | Todo |
| R4-C4 | Incremental, insufficient system-level impact | Overall suitability | Critical | Whole paper | Decide TVT-level overhaul vs transfer strategy | Yes for TVT | Make a conscious venue strategy decision | Todo |

## Cross-Cutting Work Packages

| Package | Covers | Priority | Suggested action |
|---|---|---|---|
| WP1: Novelty and story rebuild | R2-C2, R2-C3, R3-C1, R3-C9, R4-C1, R4-C4 | Critical | Rewrite abstract/introduction/related work/conclusion around a modest but precise contribution. |
| WP2: DQI formalization | R1-C2, R3-C3, R3-C4 | Critical | Define the DQI target/loss/training and justify Transformer or add simpler DQI comparison. |
| WP3: Reward and underlay feasibility | R1-C3, R1-C4, R1-C8, R3-C6 | Critical | Correct reward equations and define practical interference estimation/power control. |
| WP4: Experimental strengthening | R1-C6, R1-C9, R1-C10, R2-C5, R2-C7, R3-C7, R3-C8 | Critical | Add stronger baselines, larger settings, CI/std, sensitivity, violation rates. |
| WP5: Practical deployment and overhead | R1-C11, R2-C8, R2-C9, R4-C3 | Major/Critical | Quantify computation, signaling, latency, central-server dependency, and staleness. |
| WP6: Readability and response package | R2-C6, R2-C10, R2-C11 | Minor/Major | Add module flow table, future work, and sentence-level polishing. |

