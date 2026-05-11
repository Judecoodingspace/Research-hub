# UAV-Task-Oriented-Communication 文献索引

## 使用说明
- 研究主线：多无人机任务导向通信 / 语义通信。
- 当前主题聚焦"UAV 任务导向语义通信"，涵盖从单机语义块选择 → 个性化语义编码 → 多 UAV 多模态协同资源分配的演进脉络。
- 三篇论文均从 metadata + PDF 正文中提取分析，`notes/` 缺失。

## 对齐结果

| 年份 | 第一作者 | 文献题目 | PDF 对齐 | 相关性等级 | 子方向标签 | 初筛理由 |
| --- | --- | --- | --- | --- | --- | --- |
| 2022 | Kang | Task-Oriented Image Transmission for Scene Classification in Unmanned Aerial Systems | 已对齐 | 高相关 | 任务导向通信；语义通信；资源分配与调度 | 提出信道+内容联合感知的语义块选择，DRL 驱动——早期任务导向航拍图像传输代表作 |
| 2023 | Kang | Personalized Saliency in Task-Oriented Semantic Communications: Image Transmission and Performance Analysis | 已对齐 | 高相关 | 任务导向通信；语义通信；多模态语义融合 | 将 Scene Graph 三元组引入语义通信，实现跨模态个性化语义编码——与前篇形成单机→个性化的递进 |
| 2025 | Hu | Resource Allocation for Multi-Modal Semantic Communication in UAV Collaborative Networks | 已对齐 | 高相关 | 多无人机协同感知；任务导向通信；语义通信；资源分配与调度；多模态语义融合 | 多 UAV 中继协作 + 多模态语义 + K 语义符号数优化 + 混合决策 DRL——三篇中场景最完整 |

## 索引备注
- Kang 2022 是"任务导向图像传输"在 UAV 场景的先驱性工作，强调块级语义选择和信道感知，但单 UAV 单 MEC 无协同。
- Kang 2023 从"传什么块"升级到"传什么语义给谁"，引入跨模态 Scene Graph 和个性化编码，但计算代价高、部署可行性弱。
- Hu 2025 从单机→多 UAV 协作、单模态→多模态、固定编码→可变 K，形成当前最完整的系统框架。消融 baseline 设计值得借鉴。
- 三篇共同局限：无 trigger/reject 机制、无图像级增益预测、无 pair-level 选择器——恰是当前论文（conditional semantic collaboration）的切入点。
