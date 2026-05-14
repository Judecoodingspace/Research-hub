# Paper Specs Index

## 定位
本目录存放**每篇小论文专属的文献分析标准**。
当对某篇文献进行精读、比较、空白提炼时，除了遵循 `Agents.md` 中的通用规范外，
还需要读取对应论文的 `paper_specs` 文件，用论文特定的维度进行对照分析。

## 使用方式
1. 先读 `Agents.md` 了解通用 papercard 结构、比较规则、空白提炼规则。
2. 确定当前任务服务于哪篇小论文（如 Paper 3）。
3. 读取对应 `paper_specs/<paper_id>/` 下的专属规则文件。
4. 在分析中融合通用规则与专属规则。

## 论文索引

| Paper ID | 简称 / 方向 | Spec 文件 | 状态 |
|----------|-------------|----------|------|
| `paper2-cvn-dsa` | CVN 质量感知自适应频谱接入 / ESN-DDQN DSA | `paper2-cvn-dsa/spec.md` | ✅ 已有主线文档 + spec |
| `paper3-conditional-collaboration` | Conditional Semantic Collaboration / Multi-Action Selector | `paper3-conditional-collaboration/spec.md` | ✅ 已有主线文档 + spec |

## 与 paper3_main_thread.md 的关系
`paper3_main_thread.md` 是论文的事实性主线梳理（场景、方法、实验、发现），
`paper_specs/paper3-conditional-collaboration/spec.md` 是从中提炼的**分析标准**（对照维度、压力测试规则、防御策略等）。
两者互补：主线文档提供"是什么"，spec 提供"怎么对照分析"。
