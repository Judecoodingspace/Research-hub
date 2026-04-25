# UAV-Resouce-Alloaction 文献索引

## 使用说明
- 研究主线：多无人机任务导向通信。
- 当前主题聚焦“多 UAV 资源分配 / 任务卸载 / 轨迹规划”。
- 本轮分析以 PDF 正文为主要证据来源。
- 仓库中未发现该主题对应的 `metadata/` 与 `notes/`，因此凡无法由 PDF 正文直接确认的细节，均保守处理，不做扩展性推断。

## 对齐结果

| 年份 | 第一作者 | 文献题目 | PDF 对齐 | 相关性等级 | 子方向标签 | 初筛理由 | 证据完整性 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2024 | Guo | Multi-UAV Cooperative Task Offloading and Resource Allocation in 5G Advanced and Beyond | 已与 `papers/UAV-Resource-Alloaction/Guo 等 - 2024 - Multi-UAV Cooperative Task Offloading and Resource Allocation in 5G Advanced and Beyond.pdf` 对齐 | 高相关 | 资源分配与调度；边缘智能 / 空地协同 | 直接研究多 UAV 协同卸载、任务依赖、通信/计算时延与能量约束，是资源分配类工作的强相关前置文献。 | 中等：PDF 正文可支撑系统模型、约束和算法；`notes/` 缺失。 |
| 2024 | Qin | DRL-Based Resource Allocation and Trajectory Planning for NOMA-Enabled Multi-UAV Collaborative Caching 6G Network | 已与 `papers/UAV-Resource-Alloaction/Qin 等 - 2024 - DRL-Based Resource Allocation and Trajectory Planning for NOMA-Enabled Multi-UAV Collaborative Cachi.pdf` 对齐 | 中高相关 | 资源分配与调度；路径规划；边缘智能 / 空地协同 | 典型多 UAV 通信资源分配与轨迹规划文章，适合作为 NOMA/功率/信道复用方向 baseline；但不含计算模型。 | 中等：PDF 正文可支撑 NOMA 模型、delay 模型和求解框架；`notes/` 缺失。 |
| 2025 | Zhang | Resource Allocation and Trajectory Optimization in Multi-UAV Collaborative Vehicular Networks: An Extended Multiagent DRL Approach | 已与 `papers/UAV-Resource-Alloaction/Zhang 等 - 2025 - Resource Allocation and Trajectory Optimization in Multi-UAV Collaborative Vehicular Networks An Ex.pdf` 对齐 | 高相关 | 资源分配与调度；路径规划；边缘智能 / 空地协同 | 显式耦合轨迹、带宽、队列与外部服务器卸载，适合支撑“轨迹-通信-计算耦合”建模。 | 中等：PDF 正文能支撑通信/计算模型和实验结论；`notes/` 缺失。 |

## 索引备注
- Guo 2024 更偏“任务卸载 + 多 UAV 协同计算 + 多约束求解”。
- Qin 2024 更偏“协同缓存 + NOMA 资源分配 + 轨迹规划”。
- Zhang 2025 更偏“车辆网络中的轨迹-带宽-卸载联合优化”。
- 三篇文章都和“多 UAV 资源分配”有关，但共同缺少任务导向/语义导向建模，因此更适合作为系统建模与 baseline 储备，而不是当前主线的完整方法来源。
