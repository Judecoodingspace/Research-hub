# Kang 2023 — Personalized Saliency in Task-Oriented Semantic Communications: Image Transmission and Performance Analysis

> IEEE JSAC, Vol.41, No.1, Jan 2023 | Jiawen Kang, Hongyang Du, Zonghang Li, Zehui Xiong, Shiyao Ma, Dusit Niyato, Yuan Li

---

## 1. Problem

**论文试图解决什么问题？**
现有 UAV 语义通信方案普遍存在两个盲区：① 能效低下——UAV 将所有拍摄图像全量回传，但用户只需要其中一部分（如特定场景/对象），导致传输资源和 UAV 电量的浪费；② 无个性化——语义编码未考虑不同用户对不同内容的偏好差异，所有用户收到相同的语义信息。核心问题：**如何设计一种既节能又个性化的 UAV 任务导向语义通信框架，使 UAV 只向用户推送其感兴趣的图像语义？**

问题偏向：**传输效率不足** + **多模态语义没有统一建模**

---

## 2. Setting / Assumptions

| 维度 | 设定 |
|------|------|
| UAV 数量 | **单 UAV** 服务多用户 |
| 边缘服务器 | 有（云服务器做语义匹配和图像检索） |
| 异构算力 | 未显式建模（UAV 做语义提取+编码，服务器做匹配） |
| 信道假设 | Fisher-Snedecor F 复合衰落（含小尺度 Nakagami-m + 大尺度逆 Nakagami-m），有数学推导 |
| 路径/任务 | 固定悬停或预设路径，不做轨迹优化 |
| 模型切分 | 隐式固定（UAV 提取三元组语义，云侧匹配） |
| 多视角 | 无（单 UAV 单视角） |
| 模态 | **跨模态**：图像→文本三元组（Scene Graph）→ 用户文本查询匹配 |
| 协作机制 | 无（单 UAV→多用户，无 UAV 间协同） |

---

## 3. Core Idea

**"把图像语义压缩为三元组 Scene Graph，让用户用自然语言查询匹配图像，再根据用户兴趣对三元组做个性化权重编码——这样 UAV 不需要传全图，只传用户关心的语义"**。

核心创新链：图像 → Scene Graph 三元组提取 → 用户查询文本匹配 → 个性化注意力权重编码 → 博弈论功率分配 → 用户侧匹配评分决定是否下载原图。这是一条从"语义提取"到"个性化传输"到"资源分配"的完整链路。

---

## 4. Key Mechanism

### 4.1 任务建模
- 两阶段：Phase 1（UAV→用户：三元组语义传输），Phase 2（用户按匹配得分选择性下载原图）
- 两个优化问题：P1（用户间功率分配，Nash Bargaining Solution），P2（用户内三元组功率分配，个性化权重驱动）

### 4.2 语义表征
- **Scene Graph 三元组**：从航拍图像中提取 (subject, predicate, object) 三元组，如 (car, parked_near, building)
- 三元组经编码+调制后通过无线信道传输
- 用户侧用文本查询与接收三元组匹配，计算匹配分数 sk

### 4.3 个性化语义编码
- 用户提交兴趣查询文本
- 个性化注意力机制：对与用户兴趣更相关的三元组赋予更高编码权重
- 目的：确保用户关心的语义信息在信道衰落中优先被保护

### 4.4 信道建模与理论分析
- Fisher-Snedecor F 复合衰落信道（比 Rayleigh/Rician 更通用）
- 数学推导三元组丢弃概率（triplet drop probability）的精确闭式表达式
- 分析多天线 MRT 波束成形下的 SINR 分布

### 4.5 资源分配
- **用户间**：Nash Bargaining Solution（合作博弈），最大化各用户匹配得分的乘积
- **用户内**：按个性化权重分配功率给不同三元组
- 效用函数 = sk/˜sk（实际匹配得分/理想匹配得分）

### 4.6 优化目标
```
max Π(sk/˜sk)  (用户间)
s.t. ΣPj×T1 < WA  (能量约束)
```

---

## 5. Experiments

| 维度 | 详情 |
|------|------|
| 数据集 | Visual Genome（场景图提取）+ 自定义 UAV 航拍图像 |
| 场景图提取 | 预训练 Scene Graph 生成模型 |
| 对比方案 | (a) 无个性化（uniform weight）, (b) 无功率优化（equal power）, (c) 传统全图传输, (d) random power allocation |
| 指标 | 匹配得分 sk/˜sk、语义三元组丢弃概率、传输能量效率、用户满意度 |
| 信道 | Fisher-Snedecor F 衰落，多天线 MRT |
| 用户数 | 多用户场景（具体数值待确认） |

**关键结论**：
- 个性化权重编码显著提升用户匹配得分
- NBS 功率分配比等功率分配提高资源利用率
- Fisher-Snedecor F 信道下的 triplet drop 概率理论值与仿真吻合
- 相比全图传输，语义通信模式大幅节省带宽

**消融实验**：部分有。个性化权重 vs. 均匀权重、NBS vs. equal power 构成了组件对比。但缺少"无 Scene Graph vs. 直接图像特征"的对照。

**部署验证**：无。数学推导+数值仿真。

---

## 6. Strength

- **个性化语义通信**的概念在 2023 年具有前瞻性：将用户兴趣作为语义编码的输入，使通信从"发什么"升级到"发给谁、发什么"
- **跨模态语义桥接**：图像→三元组→文本查询，建立了视觉到语言的语义映射
- **理论深度突出**：Fisher-Snedecor F 信道下的 triplet drop 概率闭式推导，在语义通信性能分析领域较为罕见
- **博弈论资源分配**：NBS 在用户间的公平-效率权衡上有数学保证

---

## 7. Weakness

- **单 UAV、无协同**：无法处理多 UAV 协同感知/协同传输场景
- **Scene Graph 依赖**：三元组提取的质量依赖于预训练模型，在 UAV 视角（俯视、小目标、遮挡）下的鲁棒性未充分验证
- **无 trigger/reject**：所有图像都执行 Scene Graph 提取和传输，不存在"该不该处理这张图"的决策
- **计算代价未评估**：Scene Graph 生成 + 个性化注意力 + 博弈论求解的端到端延迟未报告
- **实际 UAV 部署不可信**：Scene Graph 生成通常需要 GPU，在嵌入设备上的可行性待确认
- **算法/模型选择缺乏场景必要性论证**（参见第 11 项）

---

## 8. Reusable Part

| 可复用内容 | 说明 |
|-----------|------|
| 个性化权重思想 | 可改造为当前论文的"per-image utility prediction"——不同图像对不同动作（B2/B3）的效用不同 |
| 两阶段架构 | Phase 1 传语义 → Phase 2 选择性下载，与当前论文的 proposal→backend review 流程类似 |
| 博弈论资源分配 | NBS 可用于当前论文的多 pair 选择场景（多个后侧 UAV 竞争前端 attention） |
| 跨模态语义映射 | 图像→文本的语义压缩思路可启发当前论文的 payload 压缩 |
| 信道理论分析范式 | Fisher-Snedecor F 建模 + triplet drop 推导可作为当前论文 A2A 链路建模参考 |

---

## 9. Attack Point

- **缺少协作/触发**：可加入"是否值得为这个用户提取语义"的 gating 机制
- **缺少多 UAV 协同**：多个 UAV 可分担 Scene Graph 提取负载
- **未考虑前端算力约束**：Scene Graph 在嵌入设备上的可行性未验证——这恰是当前论文 V-feature (17维, <1ms) 的优势
- **用户查询依赖人工输入**：可改进为自动任务驱动（如检测任务自动生成语义查询）

---

## 10. Relation to My Topic

**与当前论文（conditional semantic collaboration / multi-action selector）的关系**：

- **互补关系**：Kang 2023 关心的是"传什么语义给哪个用户"（semantic content selection + user matching），当前论文关心的是"该不该触发融合 + 选哪个后端"（trigger + pair selection）。二者在决策链上相邻但不同。
- **可作为对比基线**：Kang 2023 的"对所有图像都提取语义"对应当前论文的 `always-B2` 基线。
- **启发当前论文的 payload 设计**：三元组语义是一种极端的语义压缩——当前论文的 proposal-rich metadata (~5.5KB) 相比全图已是大幅压缩，可借鉴 Scene Graph 的压缩哲学来论证 "proposal 比全图更语义"。
- **可支撑"个性化"论证**：Kang 2023 证明个性化（per-user saliency）比通用方案好——这为当前论文的 per-image utility prediction（每张图预测不同的 B2/B3 效用）提供了外部佐证：不是所有图都适合同样的协作动作。

---

## 11. Scenario-Experiment Justification（场景-实验双重合理化）

### 11.1 Scenario → Algorithm Mapping

| 场景特征 | 引发的技术需求 | 选择的算法/模型 | 必要性强度 |
|----------|--------------|----------------|-----------|
| 用户只想看特定场景的图像（如"停车场"） | 需要图像内容理解和匹配 | Scene Graph 三元组提取 + 文本匹配 | 中 |
| 不同用户兴趣不同 | 需要个性化语义编码 | 个性化注意力权重 | 强 |
| UAV 能量有限、多用户竞争 | 需要公平高效的功率分配 | Nash Bargaining Solution (博弈论) | 中 |
| 无线信道存在多径衰落和阴影 | 需要精确信道建模 | Fisher-Snedecor F 复合衰落模型 | 中 |
| 无明显场景约束 | 为何用 Scene Graph 而非 CLIP embedding？ | Scene Graph 生成模型 | **可疑** |

**关键质疑**：为何不用更简单的方案——如 CLIP 图像-文本联合嵌入直接计算相似度——而要经过 Scene Graph 三元组提取？论文未讨论这一替代方案。Scene Graph 的提取精度在 UAV 俯视场景下未经充分验证。

### 11.2 Ablation & Necessity Evidence

- **部分消融**：有个性化权重 vs. 均匀权重、NBS vs. equal power 的对比
- **缺失关键消融**：没有 "无 Scene Graph（直接图像特征匹配）" vs. "有 Scene Graph" 的对照
- **组合收益不明**：个性化 + NBS + Fisher 信道建模三者的协同效应未被独立量化

### 11.3 "Why Not Simpler" Logic

- 未讨论 CLIP-style 直接嵌入匹配作为替代方案
- 未讨论简单的 keyword matching（不用三元组关系）是否足够
- 博弈论 NBS 的必要性论证不充分——简单的 proportional fairness 或 round-robin 是否也能达到类似效果？
- **存在过度设计嫌疑**：Scene Graph + 个性化注意力 + Fisher 理论推导 + NBS 博弈论，四条技术线各自的独立必要性未被充分论证

### 11.4 Defensibility Summary

**部分能经受质疑，但不够结实**。个性化权重编码与均匀权重的对比、NBS 与 equal power 的对比构成了一定的必要性证据。但 Scene Graph 作为核心语义表征的选择缺乏替代方案排除论证，且多条技术线的组合必要性未被消融证实。整体而言，这篇论文的方法论更像"技术展示"而非"场景驱动的精简方案"。

---

> 对照 `paper3_main_thread.md`：Kang 2023 的"个性化语义"提醒当前论文——不同图像对不同协作动作的"个性化效用"是合理的，per-image utility prediction 的设计方向有外部支撑。但其 Scene Graph 的计算代价恰反衬了当前论文 V-feature（17维 OpenCV，<1ms）的部署优势。
