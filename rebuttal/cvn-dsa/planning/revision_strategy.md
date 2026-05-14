# Revision Strategy

## Quick Diagnosis

This is not a simple language/format rejection. The reviewers are converging on four substantive weaknesses:

1. Novelty is perceived as insufficient because the method appears to stack Transformer, LSTM, ESN, and DDQN.
2. Key technical definitions are under-specified, especially DQI training, reward formulation, ESN settings, and underlay power control.
3. Experiments are considered too limited for TVT: small `M,N`, limited baselines, no confidence intervals, no robustness to prediction/estimation errors, and no PU violation metric.
4. Practical deployment is not convincing enough: centralized computation, signaling overhead, latency, descriptor staleness, and V2X compatibility need more analysis.

## TVT Resubmission Feasibility

TVT resubmission is possible but high risk unless the revision is substantial. A text-only revision is unlikely to satisfy Reviewers 3 and 4, because their concerns target novelty, methodological depth, and system-level impact.

For a serious TVT resubmission, the minimum technical upgrade should include:

1. A corrected and reproducible reward/underlay model.
2. A formal DQI training or construction objective.
3. At least one additional strong DRL baseline.
4. Larger-scale experiments with statistical reporting.
5. Robustness tests for PU interference violation, prediction errors, and possibly channel-estimation errors.
6. A practical overhead/latency analysis.

If you want this paper mainly as a learning project and do not want to invest substantial new experiments, a moderate revision followed by transfer to a more suitable venue may be more rational.

## Recommended Low-To-High Investment Paths

### Path A: Learning-Oriented Moderate Revision

Goal: Make the paper technically clearer and more complete without turning it into a months-long project.

Actions:

1. Fix reward equations and notation.
2. Add missing model/hyperparameter details.
3. Add limitations and future work.
4. Improve related work and contribution framing.
5. Strengthen existing experimental explanations.
6. Draft a full response letter as training.

Expected outcome:

- Good for learning English revision and response-letter writing.
- Better suited for transfer submission than TVT resubmission.

### Path B: Serious TVT Resubmission

Goal: Address the rejection as a major technical overhaul.

Actions:

1. Complete all Path A actions.
2. Add new experiments for larger `M,N`, varied `p01/p10`, CI/std, PU violation rates, prediction-error robustness, and one advanced DRL baseline.
3. Add DQI/predictor baseline comparisons or a strong justification.
4. Add deployment overhead and latency analysis.
5. Rewrite the novelty story to avoid the "AI stacking" impression.

Expected outcome:

- Much stronger paper.
- Still not guaranteed because novelty concerns are fundamental, but it becomes a credible resubmission.

## Suggested Next Step

Start with WP3: reward and underlay feasibility.

Reason:

- It is a real technical correctness issue.
- It affects reviewer trust immediately.
- It can be fixed before deciding how many new experiments to run.
- It will also clarify whether the simulation code and manuscript equations match.

After WP3, proceed to WP2: DQI formalization.

