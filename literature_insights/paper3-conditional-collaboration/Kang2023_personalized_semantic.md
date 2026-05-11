# Kang 2023 Personalized Saliency → Paper 3 启发

> 来源：`papercard/UAV-Task-Oriented-Communication/2023_Kang_Personalized_Saliency_Task_Oriented_Semantic_Comm.md`

## 核心启发：个性化 → Per-Image Utility

Kang 2023的核心逻辑链：不同用户兴趣不同 → 同一语义对不同用户价值不同 → 需要个性化权重。

**同构平移**：不同图像退化程度不同 → 同一协作动作(B2/B3)对不同图像效用不同 → 需要per-image utility prediction。

## 写作复用

可直接在论文中写：
> "Kang et al. [2023] showed that uniform semantic encoding is suboptimal when receivers have heterogeneous interests. Our work extends this insight from the user dimension to the image dimension: just as different users benefit differently from the same semantic content, different images benefit differently from the same collaboration action."

## 多Pair竞争建模（Future Work方向）

Kang 2023的NBS博弈论（max Π(sk/˜sk)）可改造为多pair选择方案：
- 原始：max Π(用户匹配得分) — 分配功率给不同用户
- 改造：max Π(utility_i) — 分配协作"名额"给不同(front, back) pair
- 含义：不是均分协作机会，而是按utility贡献比例公平分配

## 应避免

- Kang 2023的Scene Graph选择缺乏替代方案排除（CLIP embedding更简单但未讨论）——当前论文已通过V/D/H/HC对比避免了类似缺陷
- Kang 2023的计算代价（Scene Graph需GPU）反衬当前论文V-feature（<1ms, 仅OpenCV）的部署优势——可在论文中强调
