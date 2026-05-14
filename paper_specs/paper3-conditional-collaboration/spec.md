# Paper 3: Conditional Semantic Collaboration — 文献分析专属标准

> 本文件从 `paper3_main_thread.md` 提炼而来，定义对这篇论文进行文献分析时必须使用的专属对照维度。
> 通用规则（papercard 11 条结构、比较规则、空白提炼、输出风格）见仓库根目录 `Agents.md`。

---

## 一、论文锚点（必读）

当前论文的核心问题不是"是否进行语义通信"的一般性讨论，而是：

**在多无人机协同感知场景中，系统是否应当触发某一种语义协作动作，并在考虑感知增益、A2A 链路时延、前后端排队时延、载荷开销、精度-召回-F1 权衡的条件下，选择合适的协作动作与后端接收节点。**

核心关键词（用于判断文献相关性）：
- one-step contextual selector / contextual decision baseline
- conditional semantic collaboration
- trigger-and-select mechanism
- pair-level / queue-aware / link-aware / payload-aware decision
- multi-action communication selector
- image-level gain prediction as an extension direction
- label-free online selector still not fully solved

**不是**：
- always-on semantic communication
- full MARL policy
- long-horizon control / trajectory policy
- 一般性的语义通信综述
- 一般性的多 UAV 路径规划
- 一般性的模型切分 / 协同推理
- 一般性的强化学习调度

---

## 二、场景与约束速查

| 参数 | 值 |
|------|-----|
| UAV 数量 | 多 UAV（front + back） |
| 通信链路 | A2A，带宽受限，RTT 变化 |
| 部署平台 | Jetson Orin NX 级嵌入设备 |
| 推理延迟预算 | <1ms（预测器） |
| 数据集 | VisDrone2019-DET-val (548张) + DroneVehicle 外部域 (1469张) |
| 融合策略 | B0 (本地)、B2_RECALL (召回优先)、B3_TUNED (平衡) |
| payload | B0 ~1.4 KB、B2/B3 ~5.5 KB |

---

## 三、专属对照维度（Cross-Reference Dimensions）

精读其他论文时，**必须**对照以下维度（来源：`paper3_main_thread.md` 第七节）：

| 对照维度 | 核心问题 | papercard 位置 |
|----------|---------|---------------|
| **设定差异** | 被分析论文的场景/假设/约束与当前论文有何异同？差异对当前论文是威胁还是机会？ | §2 / §10 |
| **方法验证/挑战** | 被分析论文的设计选择（特征工程、效用函数、模型复杂度、预算策略）是否支持或质疑当前论文的决策？ | §3 / §7 / §11 |
| **实验补强线索** | 被分析论文覆盖了哪些当前论文未探索的实验维度（退化类型、指标、budget 范围、baseline、ablation 策略）？ | §5 |
| **写作与论证借鉴** | 被分析论文的贡献表达、消融组织逻辑、"why not simpler"论证是否可复用？ | §8 / §11 |
| **防御素材** | 被分析论文是否提供了可支撑当前论文设计合理性的外部证据（如"简单特征在少样本下优于深度特征""线性模型可部署性优势"）？ | §11.4 |
| **baseline 候选** | 被分析论文的方法是否可作为当前论文的对比方法或 Related Work 定位锚点？ | §10 |

---

## 四、当前论文的关键设计选择（用于文献对比时的压力测试）

文献对比时必须牢记以下设计选择，并评估每篇文献对这些选择的验证/挑战程度：

| 设计选择 | 说明 | 需要验证的问题 |
|----------|------|---------------|
| 17 维像素统计特征 (V) | 亮度/模糊度/雾度/边缘密度，纯 OpenCV，无 YOLO | 是否有文献证明更复杂特征在少样本下反而更差？H 过拟合的证据是否充分？ |
| Ridge 回归 | 线性模型，<1ms 推理 | 是否有文献证明非线性模型在 <1ms 约束下不可行？ |
| One-step selector | 单次决策，非 sequential | 是否有文献的 sequential 方法可对比？偏离主流叙事是否需要更多辩护？ |
| 固定 payload (~5.5KB) | 不压缩不调整 | 是否有文献做自适应 payload？是否应标记为 future work？ |
| 效用函数 | `delta_quality − λ×latency − λ×payload − precision_penalty` | 是否有文献用更复杂的效用函数？差异是否场景驱动的？ |
| 预算约束触发 | budget_only / false_trigger_constrained / hard_topk | 是否有文献用类似约束？hard_topk 是否需要更多定位声明？ |

---

## 五、Critical Self-Review Rules（对当前论文保持合理怀疑）

在分析任何一篇文献时，必须将文献视为"攻击当前论文设计选择"或"暴露当前论文薄弱环节"的潜在武器。

### 5.1 识别可疑简化
当当前论文的某个设计明显比文献主流方案简单时，必须同时给出：
- (a) 简化的正面理由（部署约束？样本不足？可解释性？）
- (b) 简化场景下可能崩塌的条件（如果未来算力提升、样本增加，简化还有优势吗？）
- (c) 文献中的复杂方案是否应标记为扩展方向而非"不适用"

### 5.2 不替论文辩护
不能因为当前论文"故意选择了简单方案"就自动将文献中的复杂方案判为"不适合借鉴"。简单方案的合理性需要通过文献对比来证明，而非通过断言。

### 5.3 压力测试
对当前论文的每个设计选择，追问：
- 如果审稿人读过这篇文献，他会用文献中的什么证据来质疑当前论文？
- 当前论文是否有实验证据或场景论证来回应这种质疑？
- 如果没有，这是论文的薄弱环节——必须标记，不能掩盖。

### 5.4 主流叙事对齐检查
如果当前论文的某个设计与当前主流论文叙事明显偏离，必须明确分析：
- (a) 这种偏离是有意为之（有充分理由）还是因为未探索？
- (b) 如果是未探索，是否应该将其列为 future work 或当前工作的局限？
- (c) 偏离本身是否可能被审稿人视为"贡献不足"？

### 5.5 禁止防御性过度
在 papercard 的 §10 和 compare/overview.md 中，不能将"当前论文不做 X"直接等同于"X 不适合当前论文"。必须区分：
- "X 因场景约束不适用"（需要场景证据）
- "X 是合理的扩展方向但当前工作未覆盖"（标记为 future work）
- "X 与当前方法形成互补"（可以共存）

---

## 六、与 MARL / NN 论文的区别速查

| 维度 | 主流 MARL / NN 论文 | 本篇 Paper 3 |
|------|---------------------|-------------|
| **做什么** | 学习「如何融合」：设计端到端融合网络或学习通信调度策略 | 假设融合策略已定，解决「该不该融合、找谁融合」 |
| **贡献类型** | 算法创新 | 系统架构 + 消融验证 + 可部署性 |
| **baseline** | 其他 RL 算法 | always-B2、always-none、随机触发 |
| **可部署性** | 很少考虑 | 17 特征 ridge <1ms，仅依赖 OpenCV+numpy，无 GPU |
| **消融深度** | 通常有限 | 5 seed × 4 fraction × 5 budget × 4 feature groups |
| **负面结果** | 很少报告 | 诚实报告 H 过拟合、B3 负效用 |
| **跨域验证** | 通常单数据集 | VisDrone → DroneVehicle |

---

## 七、实验参数速查（用于评估文献实验覆盖度）

| 维度 | Paper 3 覆盖 |
|------|-------------|
| 特征组 | V (17维) / D (~45维) / H (~1870维) / HC (~77维) |
| 校准比例 | 0.05 / 0.10 / 0.20 / 0.40 |
| 随机种子 | 11, 23, 37, 51, 73 (5 seed) |
| 通信预算 | 0.30 / 0.40 / 0.50 / 0.60 / 0.70 |
| 预算策略 | budget_only / false_trigger_constrained / hard_topk |
| 退化场景 | clean, blur_heavy, dark_heavy, downscale_0.25, fog, occlusion, mixed |
| 外部域 | DroneVehicle (1469张) |
| 指标 | Utility, Oracle Capture, False Trigger Rate, Trigger Rate |
| 排队建模 | MC 采样 500 次 |

---

## 八、通用脚手架中的 Paper 3 聚焦判断

> 以下定义 Paper 3 在使用 `Agents.md` 通用脚手架时的**领域专属侧重**。
> 分析文献时，优先关注以下子项；其他子项按需选用。

### Paper 3 重点关注的 Problem 类别
在使用 §1 Problem 通用分类时，Paper 3 重点关注：
- **决策触发条件不明确**（主：何时触发融合、与谁协作）
- **传输效率不足**（主：B2/B3 的 5.5KB payload 不能对所有图像发送）
- **协同机制不足**（主：front-back pair 选择、多动作选择）
- **推理/计算实时性不足**（辅：预测器需 <1ms）
- 感知质量不足、资源分配不合理（辅：预算约束触发）

### Paper 3 重点关注的 Assumption 维度
在使用 §2 Setting/Assumptions 通用脚手架时，Paper 3 重点关注：
- 节点数量：多 UAV（front + back pair）
- 算力条件：异构（Jetson Orin NX 级嵌入设备）
- 通信条件：A2A 受限信道，RTT 变化，排队延迟
- 感知条件：含噪声/退化（blur, dark, fog, occlusion, downscale）
- 模型部署：不讨论模型切分（B2/B3 融合策略已固定）
- 模态范围：单模态（仅图像，但区分 V/D/H 特征组）

### Paper 3 重点关注的 Key Mechanism
在使用 §4 Key Mechanism 通用脚手架时，Paper 3 重点关注：
- 资源调度方法：预算约束触发（budget_only / false_trigger_constrained / hard_topk）
- 任务建模方式：效用函数 `utility = delta_quality − λ×latency − λ×payload − precision_penalty`
- 学习类方法：Ridge 回归（线性模型，<1ms），非 DRL/MARL
- 信息表征方式：17 维像素统计特征（V），非深度特征

### Paper 3 重点关注的 Weakness 类型
在使用 §7 Weakness 通用分类时，Paper 3 优先寻找：
- 算法/模型选择缺乏场景必要性论证（技术堆砌嫌疑）
- 方法复杂但实验支撑不足（消融不充分）
- 只在理想条件下成立，难以在真实平台部署

---

## 九、三条核心贡献（用于评估文献支撑价值）

1. **通信-排队联合感知的 UAV pair 选择框架**：A2A 链路 + 排队 + payload + 质量增益 → 单一效用函数；MC 验证鲁棒性
2. **可部署的预算约束图像级融合触发器**：17 视觉代理特征 + Ridge 回归，61% oracle capture，false trigger 减半，<1ms
3. **跨域验证与诚实消融**：双域 + 四组特征 + 诚实报告负面结果

---
*关联主线文档：`paper3_main_thread.md`*
*关联 insights：`literature_insights/paper3-conditional-collaboration/`*
