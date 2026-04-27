# UAV-Fire-Detection 文献索引

## 使用说明
- 研究目标：服务“重庆超大型山地火炉城市山火检测与火险预警项目指南”写作。
- 当前材料：`papers/UAV-Fire-Detection/` 下 3 篇 PDF。
- 仓库中未发现可对应到本专题的 `notes/` 或 Zotero annotation notes；本轮精读以 PDF 正文为主证据。
- 输出重点：无人机协同、山火感知、火险预警、数字孪生模拟场景、高温可靠性缺口。

## 文献列表

| 年份 | 第一作者 | 文献题目 | 本地 PDF | 相关性 | 子方向标签 | 对项目的主要价值 | 证据边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026 | Li | Two-Tier Submodel Partition Framework for Enhancing UAV Swarm Robustness in Forest Fire Detection | `papers/UAV-Fire-Detection/Two-Tier_Submodel_Partition_Framework_for_Enhancing_UAV_Swarm_Robustness_in_Forest_Fire_Detection.pdf` | 高 | 多无人机协同感知；分割计算 / 模型切分；边缘智能 / 空地协同；资源分配与调度 | 支撑“无人机集群在火场受损、通信受限条件下仍需保持检测与在线更新能力”的技术依据。 | 有 FLAME 数据集仿真与鲁棒性实验；未覆盖重庆山地、高温热防护、真实部署。 |
| 2026 | Gomes | Integrating Digital Twin and Swarm-Based UAV Systems for Autonomous Wildfire Prevention and Detection | `papers/UAV-Fire-Detection/Integrating_Digital_Twin_and_Swarm-Based_UAV_Systems_for_Autonomous_Wildfire_Prevention_and_Detection.pdf` | 高 | 多无人机协同感知；路径规划；边缘智能 / 空地协同 | 支撑“可展示模拟场景、数字孪生、Boids 集群巡检、覆盖率评估”的项目展示逻辑。 | 有 Web 原型、FoV 测试、Boids 覆盖仿真；未深入训练山火检测模型，也未建模高温热防护。 |
| 2025 | Bairam Zadeh | A Conceptual High Level Multiagent System for Wildfire Management | `papers/UAV-Fire-Detection/A_Conceptual_High_Level_Multiagent_System_for_Wildfire_Management.pdf` | 中高 | 多无人机协同感知；协同推理；资源分配与调度；边缘智能 / 空地协同 | 支撑“火险预测、检测、监测、态势感知、决策支持”之间的模块化闭环。 | 主要是概念性 MAS 架构，缺少落地实验；适合作为系统框架依据，不宜作为算法效果依据。 |

## 总体判断
- 三篇论文能共同支撑项目从“泛 AI 应急指挥”收敛到“多无人机协同山火感知 + AI 火险预警 + 可展示模拟场景”。
- 它们均未充分覆盖“重庆夏季极端高温下无人机电池热衰减、电子设备稳定性、山地通信遮挡、复杂地形巡检”的工程约束。
- 项目差异化不宜写成“替代现有森林防火系统”，而应写成“面向山地高温城市复杂场景的机动补盲、快速复核、协同预警与模拟推演能力增强”。

## 已生成成果
- `papercard/UAV-Fire-Detection/2026_Li_TSPF_UAV_Swarm_Forest_Fire_Detection.md`
- `papercard/UAV-Fire-Detection/2026_Gomes_Digital_Twin_Swarm_UAV_Wildfire_Detection.md`
- `papercard/UAV-Fire-Detection/2025_Bairam_Zadeh_MAS_Wildfire_Management.md`
- `compare/UAV-Fire-Detection/overview.md`
- `gap_map/UAV-Fire-Detection/project_gap_and_positioning.md`
- `writing_support/UAV-Fire-Detection/project_guide_core.md`
- `writing_support/UAV-Fire-Detection/simulation_scenario.md`
