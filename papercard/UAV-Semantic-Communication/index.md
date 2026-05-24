# UAV-Semantic-Communication 文献索引

## 使用说明
- 研究主线：多无人机任务导向通信。
- 当前主题聚焦“多 UAV 协同语义通信 / 任务导向语义源选择 / 冗余传输抑制”。
- 本轮分析以 metadata 与 PDF 正文为主要证据来源。
- 仓库中未发现对应 `notes/`，因此凡无法由 metadata 或 PDF 直接确认的细节，均保守处理为待确认或未展开。

## 对齐结果

| 年份 | 第一作者 | 文献题目 | PDF 对齐 | 相关性等级 | 子方向标签 | 初筛理由 | 证据完整性 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026 | Han | Design of Multi-UAV Cooperative Deep Semantic Autoencoders for Communication Networks | 已与 `papers/UAV-Semantic-Communication/Han 等 - 2026 - Design of Multi-UAV Cooperative Deep Semantic Autoencoders for Communication Networks.pdf` 对齐 | 高相关 | 多无人机协同感知；任务导向通信；语义通信；协同推理；资源分配与调度 | 直接提出 MC-DSA，多 UAV 通过 query-key 语义匹配决定 when2com、who2com 和上传语义特征，适合支撑多 UAV 任务导向语义源选择与冗余传输抑制。 | 中等偏高：metadata 完整，PDF 正文可支撑系统模型、机制和实验；`notes/` 缺失。 |

## 索引备注
- Han 2026 是当前语义通信方向中与“多 UAV 任务导向通信”高度贴近的核心前置文献。
- 它的主要贡献在于把多 UAV 协同通信从“全量上传”推进到“任务 query 驱动的语义源选择”。
- 它的主要不足是仍采用固定轨迹和单模态 RGB 图像分割，未覆盖异构算力、动态切分、路径规划与协同推理闭环。

| 2025 | Zefu Lin; Wenbo Chen; Xiaojuan Jin; Yu-Ren Yang; L... | [MCOP: Multi-UAV Collaborative Occupancy Prediction...](2025_Lin_MCOP_Multi-UAV_Collaborative_Occupancy_Prediction.md) | MEDIUM | 2026-05-24 |
|  | Haotai Zhao; Jie Ruan; Xinyao Zhang; Miao Liu; Jie... | [FLASH: A Joint Optimization Framework of Splitting, Pairing,...](_Zhao_FLASH_A_Joint_Optimization_Framework_of_Splitting,_Pairing,_.md) | MEDIUM | 2026-05-24 |