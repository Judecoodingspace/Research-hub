# UAV-Multi-Model 文献索引

## 使用说明
- 研究主线：多无人机任务导向通信。
- 当前轮次为“现有材料版”分析：以 `metadata/2026-04-09_uav-multi-model_zotero-weekly_raw.csv` 为主证据，以本地 PDF 可确认的题名、关键词和少量可抽取文本为辅。
- 仓库中未发现 `notes/`；凡无法从 metadata 或 PDF 直接确认的机制、实验和约束，统一标为 `待确认`。

## 对齐结果

| 年份 | 第一作者 | 文献题目 | PDF 对齐 | 相关性等级 | 子方向标签 | 初筛理由 | 证据完整性 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2024 | Ren | Multimodal virtual semantic communication for tiny-machine-learning-based UAV task execution | 已与 `papers/UAV-Multi-Model/Ren 等 - 2024 - Multimodal Virtual Semantic Communication for Tiny-Machine-Learning-Based UAV Task Execution.pdf` 对齐 | 高相关 | 任务导向通信；语义通信；多模态语义融合 | 直接讨论 UAV 任务执行、多模态语义通信与资源受限 TinyML 执行，和任务导向通信主线高度贴近；但多 UAV 协同与资源竞争建模不明确。 | 中等偏低：metadata 摘要完整，PDF 仅确认题名和关键词，正文方法/实验细节提取不足。 |
| 2026 | Guo | Perception enhanced multimodal multitask semantic communication and resource management for UAV-assisted ISAC systems | 已与 `papers/UAV-Multi-Model/Guo 等 - 2026 - Perception Enhanced Multimodal Multitask Semantic Communication and Resource Management for UAV-Assi.pdf` 对齐 | 高相关 | 任务导向通信；语义通信；资源分配与调度 | 明确以任务导向 QoE 为目标，将多模态语义通信、轨迹规划与资源管理联动，和当前主线更接近。 | 中等：metadata 摘要信息较充足，PDF 可确认题名与关键词，但精确模型和约束仍待确认。 |

## 索引备注
- Ren 2024 更偏“任务语义建模 + TinyML 端侧执行”的前置工作，可支撑研究背景、问题定义和 related work。
- Guo 2026 更偏“语义增强 + 轨迹/资源联合优化”的方法性前置工作，可作为更接近系统优化链路的比较对象。
- 两篇论文都与“多无人机任务导向通信”有关，但都不足以直接覆盖“多 UAV 协同 + 异构算力 + 感知-通信-推理全链路耦合”这一完整问题。
