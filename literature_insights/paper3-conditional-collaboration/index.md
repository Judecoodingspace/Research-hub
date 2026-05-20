# Paper 3: Literature Insights Index

> 主线程文档：`paper3_main_thread.md`
> 对照规则：`Agents.md` → 当前论文主线对照 + Critical Self-Review Rule

## 已分析文献的启发汇总

| 来源 | 关键启发 | 优先级 |
|------|---------|:---:|
| Han 2026 MC-DSA | query-key匹配→质疑效用函数手工定义；多S-UAV同时激活→暴露单pair选择局限；soft-training/hard-testing两阶段策略 | 🔴 |
| Kang 2022 Task-Oriented | 信道+内容联合感知→支撑Layer 2的A2A链路作为输入；单步MDP→与one-step selector同构 | 🟡 |
| Kang 2023 Personalized | 个性化weight→支撑per-image utility；NBS博弈论→多pair竞争建模 | 🟡 |
| Hu 2025 Multi-Modal | K作为优化变量→支撑"协作动作也是优化变量"论证；5-baseline消融范式→实验矩阵设计模板 | 🔴 |
| Zhang 2026 DMMP-PR-TSA | 异构UAV能力三维向量建模→支撑Layer 2 pair能力剖面；动态触发事件分类→丰富trigger condition枚举；三阶段级联描述范式→复用架构叙述；TSA无simple baseline→反衬Paper 3消融诚实性 | 🟢 |

## 跨文献的共同薄弱环节（当前论文已补强）

1. **Trigger/Reject决策**：五篇均无 → 当前论文核心贡献
2. **Pair/后端选择**：五篇均无 → 当前论文核心贡献
3. **预算约束全局触发**：五篇均无 → 当前论文核心贡献
4. **诚实消融/负面结果**：仅Hu 2025有部分消融，Zhang 2026无消融 → 当前论文V/D/H/HC+B2/B3已做到
5. **跨域验证**：五篇均无 → 当前论文VisDrone→DroneVehicle已做到
6. **通信约束建模**：Zhang 2026/Han 2026均无 → 当前论文A2A链路+排队建模已做到

## 跨文献暴露的当前论文薄弱环节

1. **效用函数手工定义 vs. 端到端学习（Han 2026）**：需在论文中承认trade-off
2. **单pair选择 vs. 多源同时激活（Han 2026）**：应列为future work
3. **分层优化≠全局最优（Han 2026, Hu 2025）**：需在Discussion中说明
4. **One-step selector偏离主流sequential叙事**：需有意识的论证而非回避
5. **缺少random-pair baseline**：仿照Han 2026 random selection设计
6. **Zhang 2026 TSA无simple baseline的警示**：提醒Paper 3必须保留Ridge vs always-B2/random对比的论证强度，避免被质疑"RL/复杂模型不必要"
