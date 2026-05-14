# Reviewer Comments Raw

Paste all reviewer comments here exactly as received.

Suggested layout:

```text
Reviewer 1
Comment 1:
The paper addresses an important and timely problem, adaptive overlay/underlay access in cognitive vehicular networks, with a thoughtful, modular architecture and a plausible motivation for ESN-based acceleration. The ablations and convergence comparisons are directionally encouraging, and the offloading design is aligned with IoT/CVN constraints. However, key elements are under-specified or internally inconsistent: the DQI module lacks a defined training objective, the reward definitions are ambiguous and possibly erroneous, the underlay feasibility hinges on unrealistic SU-PU channel knowledge, and the experimental methodology omits critical details and strong baselines. As written, the evidence does not yet substantiate the central claims to the rigor expected for this journal. I recommend a major revision, with emphasis on: (i) formalizing and validating the DQI learning, (ii) correcting and justifying reward formulations, (iii) providing practical underlay interference estimation/control, and (iv) substantially strengthening experimental design, baselines, and statistical reporting. With these addressed, the work could offer a valuable contribution to adaptive DSA in CVNs.
Comment 2:
How is the Transformer-based DQI trained? What are the targets, loss function, and training data? If unsupervised/self-supervised, what objective ensures DQI correlates with achievable link quality?
In Eq. (12), do you intend Φ_t^{i,j} = Γ·Φ'_t^{i,j} for overlay (quality emphasis) rather than Φ_t^{i,j} = Γ? Please clarify the exact reward used in code and whether rewards are normalized/clipped.
How are |h_t^{i,PU}|^2 and Ψ_t^{j,PU} obtained in practice in a high-mobility CVN? Do you assume BS-side estimation, PU cooperation, or a model-based pathloss proxy? What is the sensitivity of results to estimation errors?
Please provide full ESN details: reservoir size R, spectral radius, input scaling, leak rate, activation function, regularization of readout, and initialization. Why ReLU rather than tanh, and how do you ensure the echo-state property?
What are the exact architectures and hyperparameters for the attention-LSTM predictor (layers, hidden sizes, attention formulation, optimizer, window length T)? How does it compare empirically to simpler predictors (Markov, RF, XGBoost) in accuracy and compute?
How are SNR/RSS/B simulated over time and across VTs/channels (path loss, fading distributions, mobility trajectories)? What are the queue sizes, traffic arrival rates, and sensing error models?
Underlay power control: how is P_t^{i,j} selected to meet Ψ_t^{j,PU}? Is there a control loop, discrete power levels, or a closed-form update? How often is power adapted and with what latency?
Can you report interference violation rates to PUs under each scheme and show robustness when occupancy predictions are wrong (e.g., controlled false-alarm/miss scenarios)?
Please include standard deviations/confidence intervals and expand evaluations to larger M,N, varied p01/p10, and harsher mobility to demonstrate scalability and generality.
What is the communication overhead of broadcasting DQI/θ summaries, and how sensitive is performance to Tupd/Tstat and descriptor staleness?

Reviewer 2
comment 1:
The motivation is generally clear, especially regarding spectrum scarcity and sensing uncertainty. However, the necessity of combining quality evaluation + prediction + ESN-DDQN is still primarily argued qualitatively rather than quantitatively.

Please provide quantitative or empirical evidence demonstrating why existing RL-based DSA methods (DQN/LSTM-DDQN) are insufficient without the proposed multi-module design.

comment 2:
The work integrates multiple existing techniques (Transformer, LSTM, ESN, DDQN). While the integration is meaningful, the level of fundamental novelty is not fully articulated.

comment3:
The contributions are well-listed, but the distinction between incremental improvement and substantial advancement is not sufficiently emphasized.
Please further quantify and summarize which component contributes the most under different spectrum regimes, based on the existing ablation results.

comment4:
The related work is well-structured (MDP, game theory, RL), but it lacks coverage of recent DRL-based resource allocation or precoding works in RIS-enabled systems, which are related to adaptive wireless decision-making.

Please consider citing and discussing the following work in the context of DRL-based wireless optimization:

[R1] P. -H. Chou, B. -R. Zheng, W. -J. Huang, W. Saad, Y. Tsao and R. Y. Chang, "Deep Reinforcement Learning-Based Precoding for Multi-RIS-Aided Multiuser Downlink Systems With Practical Phase Shift," in IEEE Wireless Communications Letters, vol. 14, no. 1, pp. 23-27, Jan. 2025, doi: 10.1109/LWC.2024.3482720.

comment5:
The simulation setup (two-state Markov PU model, fixed transition probabilities) is reasonable but somewhat simplified.

Please discuss how sensitive the results are to different PU traffic models or more realistic mobility/channel dynamics.

comment6:
The framework is comprehensive, but the interaction among modules (Transformer, LSTM, ESN-DDQN) is relatively complex and may be difficult to follow.

comment7:
The comparisons include overlay/underlay and ablation models, which are appropriate. However, comparisons with other DRL-based baselines (DQN, PPO, DDPG) are limited.
Please include at least one additional DRL-based baseline or justify why the current baselines are sufficient for fair comparison.

comment8：
The manuscript does not explicitly discuss the limitations of the proposed framework, particularly in terms of computational complexity and practical deployment.

(1) Please include a discussion on the limitations of the proposed approach, including computational overhead, dependency on centralized server processing, scalability in large-scale networks, and the trade-off between performance gain and model complexity.

(2) If possible, please provide quantitative analysis or comparisons to justify whether the performance improvement is commensurate with the increased system complexity.

comment9:
 The paper assumes a centralized server for DQI and prediction computation.
However, practical deployment constraints (latency, signaling overhead, standard compatibility) are not fully discussed.

Please clarify how the proposed framework can be implemented in practical systems (5G NR-V2X or 6G architectures), including signaling and latency considerations.

comment10:
Future work is not sufficiently elaborated in the conclusion.
Please briefly discuss possible future extensions, such as decentralized learning, multi-agent coordination, or deployment in more realistic vehicular environments.

comment11:
Some sentences, particularly in the introduction and system model, are overly long and contain multiple clauses, which may affect readability.Please revise long sentences into shorter and clearer structures to improve readability.


Reviewer 3:

comment1:
The use of ESN in RL is not fundamentally new, and the paper does not clearly distinguish how this ESN-DDQN differs from prior reservoir computing-based DRL approaches. Why is it DDQN, not DDPG, SAC, or TD3?

comment2:
The combination of Transformer + LSTM + ESN-DDQN introduces high system complexity. The authors may like explaning the feasibility since marginal gains versus simpler unified architectures seem not good.

comment3:
The Transformer-based DQI model is applied to low-dimensional features (SNR, RSS, bandwidth), which may not require attention mechanisms, leading to potential over-engineering.

comment4:
Channel quality modeling only considers SNR, RSS, and bandwidth (page 7) should include some critical factors like Doppler effects, or latency constraints in CVNs.

comment5:
The state vector includes sensing outcome, DQI, and prediction simultaneously (page 10), which may introduce correlated or redundant information without feature selection analysis.

comment6:
Under underlay mode, rewards can remain positive under interference constraints (page 11), which may bias the agent toward underlay access without explicit fairness constraints.

comment7:
Experiments use only small configurations (e.g., M=3,5 channels; N=3,5 VTs) (page 12), limiting scalability validation for dense vehicular scenarios.

comment8:
 Baselines include Q-learning, MLP-DDQN, and LSTM-DDQN (page 15), but what about recent advanced DRL methods (e.g., PPO, SAC, multi-agent RL)?

 comment9:
Overall, the problem and solution are well known. Many definitions are not concistent and the modelling is simplified. The novelty is unclear. Except there are significant enhancements with core algorithms are updated and comprehensive evaluations for V2X, e.g., with real devices or USRP, the work is still at the early stage.

reviewer4:
ADDITIONAL COMMENTS TO THE AUTHOR:
The paper proposes an adaptive access framework for cognitive vehicular networks that combines a Transformer-based channel quality evaluation module, an attention-enhanced LSTM for channel prediction, and an ESN-DDQN reinforcement learning algorithm for decision-making. The goal is to enable vehicles to dynamically select channels and switch between overlay and underlay access modes. The authors claim that this integrated design improves packet loss rate, throughput, and convergence speed compared to several baselines, while maintaining protection for primary users.

The reviewer is not fully convinced by the contribution here. The paper mainly combines a set of well-known AI techniques—Transformer, LSTM with attention, and DDQN/ESN—on top of a fairly standard cognitive vehicular network model. Each of these components is already widely used, and putting them together in this way feels more like engineering integration than a real conceptual or methodological advance. It gives the impression of stacking powerful AI tools rather than developing something fundamentally new for DSA or vehicular networks.

Another concern is that the paper leans almost entirely on simulation results to justify its value. While the performance improvements look good on paper, there’s no theoretical analysis to explain why the method should work better, nor any discussion of optimality, convergence guarantees, or deeper system insights. At this point, simulation gains alone are not very convincing. Without stronger analytical grounding or real-world validation, the work feels a bit superficial.

The reviewer is also missing a serious discussion of practicality. The proposed framework introduces multiple heavy components—Transformer-based evaluation, attention-based prediction, and ESN-DDQN—yet there is very little discussion about computational cost, communication overhead, latency, or deployment feasibility in vehicular environments. These are critical issues in DSA and V2X systems, and the paper doesn’t really engage with them. It’s unclear whether the observed gains would still hold once these constraints are taken into account.

Overall, while the paper is clearly written and the idea is technically sound, the contribution feels incremental. It follows a common trend of applying advanced AI models to classical problems, but without delivering enough new insight, theoretical depth, or system-level impact. For these reasons, the reviewer does not consider the paper strong enough for publication in its current form.