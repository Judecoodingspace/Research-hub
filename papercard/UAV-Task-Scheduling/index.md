# UAV-Task-Scheduling 文献索引

## 使用说明
- 研究主线：异构 UAV 集群任务调度与资源分配
- 当前主题聚焦"UAV 边缘辅助遥感场景下的联合调度与资源分配"
- 论文从 metadata + PDF 正文中提取分析，notes/ 缺失。

## 对齐结果

| 年份 | 第一作者 | 文献题目 | PDF 对齐 | 相关性等级 | 子方向标签 | 初筛理由 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026 | Zhang | Learning Enhanced Scheduling and Resource Allocation for Heterogeneous UAV Swarms in Edge Assisted Remote Sensing | 已对齐 | 中相关 | 资源分配与调度；路径规划 / 轨迹优化；协同推理 / 边缘智能 | 异构 UAV 集群三阶段任务调度框架（DMMP-PR-TSA），路径规划与资源分配联合优化，但无通信约束、无感知质量反馈、无 trigger/reject 机制——与 Paper 3 互补但非同一问题域 |

## 索引备注
- Zhang 2026 是"宏观任务调度层"的代表工作：管"哪个 UAV 去哪做什么任务"。
- Paper 3 是"微观触发决策层"：管"任务中哪些图像值得前后端协作"——两者形成清晰层级关系。
- Zhang 2026 的异构能力建模（三维能力向量）、动态触发条件分类、三阶段级联架构可提供方法论参考。
- 其主要局限（无通信建模、无消融实验、无感知质量指标）恰是 Paper 3 的贡献空间。
