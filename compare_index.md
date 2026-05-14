# 多篇论文比较总索引

## 使用说明
- 本文件用于跨主题追踪 `compare/` 下的横向比较结果。
- 比较文件应围绕当前研究主线提炼差异、共性缺口与可复用内容，不堆叠摘要。
- 比较时使用的专属维度来自 `paper_specs/<paper_id>/spec.md`。

## 主题索引

| 主题 | 比较文件 | 主要用途 | 状态 |
| --- | --- | --- | --- |
| UAV-Fire-Detection | `compare/UAV-Fire-Detection/overview.md` | 支撑重庆山地高温山火感知与火险预警项目指南修改 | 已生成 |
| UAV-Multi-Model | `compare/UAV-Multi-Model/overview.md` | 多模态任务语义通信与资源优化比较 | 已有 |
| UAV-LLM | `compare/UAV-LLM/overview.md` | UAV 多模态推理和 LLM 相关比较 | 已有 |
| UAV-Resouce-Alloaction | `compare/UAV-Resouce-Alloaction/overview.md` | 多 UAV 资源分配与轨迹优化比较 | 已有 |
| UAV-High-Overlap-Impact | `compare/UAV-High-Overlap-Impact/20260508_han_mc_dsa_impact_on_my_idea.md` | 高重合度文献对当前 conditional semantic collaboration / multi-action selector idea 的冲击评估 | 已生成 |
| UAV-Task-Oriented-Communication | `compare/UAV-Task-Oriented-Communication/overview.md` | 三篇任务导向语义通信论文横向比较：块选择→个性化语义→多UAV多模态资源分配演进及其与当前论文的对照 | 已生成 |
| CVN-DSA | `compare/CVN-DSA/overview.md` | 认知车联网频谱接入算法横向比较，支撑审稿意见回复 | 目录已建立，待填充 |

## CVN-DSA 相关衍生成果
- 研究空白与定位：`gap_map/CVN-DSA/cvn_dsa_gap_and_positioning.md`（待填充）
- 审稿意见管理：`rebuttal/cvn-dsa/`（reviewer_comments / revision_plan / lit_support_matrix）

## UAV-Fire-Detection 相关衍生成果
- 研究空白与定位：`gap_map/UAV-Fire-Detection/project_gap_and_positioning.md`
- 项目指南核心文本：`writing_support/UAV-Fire-Detection/project_guide_core.md`
- 可展示模拟场景：`writing_support/UAV-Fire-Detection/simulation_scenario.md`

## UAV-High-Overlap-Impact 相关衍生成果
- `compare/UAV-High-Overlap-Impact/20260508_han_mc_dsa_impact_on_my_idea.md`
  - 类型：高重合度文献冲击评估
  - 相似论文：Han 2026, Design of Multi-UAV Cooperative Deep Semantic Autoencoders for Communication Networks
  - 当前论文主线：conditional semantic collaboration / multi-action semantic selector
  - 结论：真实威胁，但主要威胁 selective semantic source communication claim；当前工作需收缩到多动作、代价感知、图像级增益预测与安全边界

## UAV-Task-Oriented-Communication 相关衍生成果
- `compare/UAV-Task-Oriented-Communication/overview.md`
  - 类型：三篇论文横向比较
  - 涵盖论文：Kang 2022, Kang 2023, Hu 2025
  - 与当前论文对照：三篇均无 trigger/reject 机制，当前论文恰填补这一空白
  - 可复用素材：Hu 2025 的 5 baseline 消融范式、Kang 2023 的个性化 weight 思想
