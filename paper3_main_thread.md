# 小论文主线梳理

> 整理自 2026-05-09 完整对话，用于跨对话对比分析。

---

## 一、场景设定（Scenario）

### 物理场景
- **多 UAV 协同感知**：一架或多架前侧任务 UAV 拍摄图像，后侧 UAV 或后端服务器协助做语义融合
- **通信受限**：UAV 之间的 A2A（Air-to-Air）链路带宽有限，有传输延迟、排队延迟
- **边缘部署**：所有决策需在 Jetson Orin NX 等级别的嵌入设备上实时运行（毫秒级延迟预算）

### 融合策略（已验证有效）
- **B0**：前端本地检测，不发送给后端（`bbox_only_post_nms`）
- **B2_RECALL**：后端语义复核，召回率优先（`proposal_rich_backend_review`）
- **B3_TUNED**：后端语义增强，平衡精确率与召回率（`proposal_rich_backend_augment`）

B2/B3 都需要发送 proposal-rich metadata（~5.5 KB），比 B0（~1.4 KB）通信量大得多。

---

## 二、核心问题（Problem）

> **给定已验证有效的后端语义融合策略（B2_RECALL / B3_TUNED），在通信带宽受限的多 UAV 场景中，如何决定「是否触发融合」以及「与哪个后侧 UAV 协作」，使得系统整体的感知质量净效用最大化？**

拆成两个子问题：

| 子问题 | 具体表述 |
|---|---|
| **子问题 1：Pair 匹配** | 一个前侧 UAV 面对多个候选后侧 UAV（A2A 链路质量不同、排队状态不同），应该选哪一个协作？或者不协作？ |
| **子问题 2：触发决策** | 给定匹配好的 pair，当前拍摄的这张图像是否值得触发 B2/B3 融合？还是直接用 B0 本地结果？ |

### 关键约束
- **通信预算**：不能对所有图像都触发 B2/B3（带宽不够），需按比例限制
- **延迟预算**：预测器推理需在 <1ms 内完成（边缘设备限制）
- **无退化标签**：实际部署中不知道当前图像属于什么退化类型（雾？暗光？模糊？），必须从图像本身判断

---

## 三、研究方法（Method）

### 整体架构（3 层）

```
Layer 1                  Layer 2                       Layer 3
后端融合验证             通信感知 Pair 匹配             图像级触发预测
───────────             ────────────────              ──────────────
验证 B2/B3 在            给定前侧 UAV +                给定一张图，用图像
VisDrone 退化场景        候选后侧 UAV 列表，            特征预测 B2/B3 的
上有真实质量增益         计算每个 (front, back,         融合效用，在预算
                        action) 的效用，              约束下决定是否触发
确定 B2 以召回优先       选择最优 pair /
B3 以平衡优先            none
```

### Layer 2: 通信感知 Pair 选择器

**效用公式**：

```
pair_extra_latency = semantic_extra_latency
                   + front_to_back_tx_ms(payload, A2A rate, RTT)
                   + front_queue_delay_ms
                   + back_queue_delay_ms

utility = predicted_delta_quality
        - λ_latency × pair_extra_latency_ms
        - λ_payload × extra_payload_bytes
        - precision_penalty_weight × max(0, -delta_precision)
```

- `predicted_delta_quality`：早期用场景级查表（如 occlusion→delta_f1=0.027），后期接入图像级预测器
- 每个 (front_uav, back_uav, action) 算出一个 utility，选择 utility 最高且 > 0 的 pair 和 action
- 通过 Monaco 蒙特卡洛占用采样（500 次）评估排队状态随机性下的鲁棒性

### Layer 3: 预算约束图像级增益预测器

**预测流程**：

```
输入图像
  → 提取 V 特征（17 个像素统计量，纯 OpenCV，不跑 YOLO）
  → 标准化：(x - x_mean) / x_std
  → Ridge 回归：utility = x_norm @ w + y_mean
  → 对 B2_RECALL 和 B3_TUNED 分别预测效用
  → 在 budget 约束下选择：效用最高的 floor(budget × n) 张图触发
```

**17 个 V 特征**：亮度均值/标准差、拉普拉斯方差、Canny 边缘密度、暗通道均值/p90、HSV 饱和度和明度统计、雾度代理、遮挡代理。全部是像素级统计，无 YOLO 依赖。

**为什么不用更复杂的特征**：也测试了 D（检测框统计特征，~45 维）和 H（YOLO latent ~1870 维），但 H 因校准样本不足（588 ≪ 1870）而严重过拟合，效用不如 V。

**预算约束**：实验了三种策略——`budget_only`（只约束触发率）、`false_trigger_constrained`（同时约束误触发率 ≤ 0.35）、`hard_topk`（直接取效用预测值最高的 k 张，跳过阈值选择）。

---

## 四、实验设置（Experiments）

### 数据集
- **VisDrone2019-DET-val**：548 张无人机视角图像，含 7 种退化场景（clean、blur_heavy、dark_heavy、downscale_0.25、fog、occlusion、mixed）
- **DroneVehicle**（外部域）：1469 张无人机+车载视角 RGB 图像，单类车辆检测

### 实验矩阵
| 维度 | 取值 |
|---|---|
| 特征组 | V (17维) / D (~45维) / H (~1870维) / HC (~77维) |
| 校准比例 | 0.05 / 0.10 / 0.20 / 0.40 |
| 随机种子 | 11, 23, 37, 51, 73（5 seed 交叉验证） |
| 通信预算 | 0.30 / 0.40 / 0.50 / 0.60 / 0.70 |
| 预算策略 | budget_only / false_trigger_constrained / hard_topk |
| 退化场景 | clean, blur_heavy, dark_heavy, downscale_0.25, fog, occlusion, mixed |

### 关键指标
- **Utility**：`predicted_delta_quality − λ_latency×latency − λ_payload×payload`
- **Oracle Capture**：学习策略选中的图像中 oracle utility 之和 / 全体 oracle utility 之和
- **False Trigger Rate**：触发但效用 ≤ 0 的图像比例
- **Trigger Rate**：实际触发的图像比例

---

## 五、关键发现（Key Findings）

### Finding 1（支持假设）
**V 特征 + Ridge 回归在预算约束下显著优于 always-B2**：
- Full DroneVehicle split：utility 0.035 vs always-B2 0.023（+52%）
- False trigger 0.32 vs always-B2 0.65（减半）
- Oracle capture 61%
- 5 seed 交叉验证标准差极小（utility σ = 0.0016）

### Finding 2（诚实负面）
**更复杂的特征（D/H/HC）不提升预测器效用**：
- H（~1870 维 YOLO latent）在所有 seed/fraction 组合下 utility 均低于 V
- 失败原因：校准样本不足（588 ≪ 1870），ridge 回归欠定
- HC（top-32 latent）比 H 安全但仍不如 V

### Finding 3（B3 筛选）
**B3_TUNED 在 DroneVehicle clean RGB 上净效用为负**：
- B3 全量触发效用 = −0.0052，false trigger rate = 0.84
- Predictor 正确将其选择概率压制为近乎零
- 这不是 Bug——证明了系统能按场景自动筛选合适动作

### Finding 4（Pair 匹配）
**排队延迟可以压倒 A2A 链路质量**：
- 算法正确选择了「远但空闲」而非「近但繁忙」的后侧 UAV
- 排队延迟（27ms）> A2A 链路差异（1.3ms）
- MC 采样下 occlusion/downscale 稳定触发，fog/blur 稳定拒绝

---

## 六、与 MARL / NN 论文的区别

| 维度 | 主流 MARL / NN 论文 | 本篇 |
|---|---|---|
| **做什么** | 学习「如何融合」：设计端到端融合网络（attention/GNN/transformer）或学习通信调度策略（DQN/PPO） | 假设融合策略已定（B2_RECALL/B3_TUNED），解决「该不该融合、找谁融合」的系统决策问题 |
| **贡献类型** | 算法创新 | 系统架构 + 消融验证 + 可部署性 |
| **baseline** | 其他 RL 算法 | always-B2、always-none、随机触发 |
| **可部署性** | 很少考虑 | 17 特征 ridge <1ms，仅依赖 OpenCV+numpy，无 GPU |
| **消融深度** | 通常有限 | 5 seed × 4 fraction × 5 budget × 4 feature groups |
| **负面结果** | 很少报告 | 诚实报告 H 过拟合、B3 负效用 |
| **跨域验证** | 通常单数据集 | VisDrone → DroneVehicle |

---

## 七、当前状态与待完成

### ✅ 已完成
- VisDrone 后端融合质量验证（B2/B3 稳定性 + 阈值调优）
- 通信表示银行 + Pair 级选择器 + Fleet×退化矩阵 + MC 采样
- 多动作选择器（B2_RECALL + B3_TUNED）
- 图像级增益预测（VisDrone 域，V/D/H 特征，LOSO 验证）
- DroneVehicle 外部域迁移（backend 全量推理 + predictor full split）
- n300 门控通过（4/5 seeds）
- V-only 部署预测器（`scripts/predict_v_trigger.py`）
- 概念词典（`EXPERIMENT_CONCEPTS.md`）

### ⬜ 待完成
- 论文表格（从实验 CSV 提取紧凑对比表）
- Layer 2 ↔ Layer 3 接口整合（将 ridge 预测值接入 pair 选择器的 quality 项）
- 归一化指标（oracle capture %、false trigger 降幅）
- hard_topk 在论文中的定位声明
- 多 front × 多 back 全局匹配实验（可选加强）
- 论文写作

---

## 八、可能的三条核心贡献

1. **通信-排队联合感知的 UAV pair 选择框架**：统一建模 A2A 链路延迟、排队延迟、payload 成本和感知质量增益为单一效用函数；MC 采样验证鲁棒性；证明排队延迟可以压倒链路质量

2. **可部署的预算约束图像级融合触发器**：仅用 17 个视觉代理特征 + 线性 ridge 回归，在 budget 约束下实现 61% oracle capture、false trigger 减半；仅依赖 OpenCV + numpy，<1ms 推理，无 GPU

3. **跨域验证与诚实消融**：在 VisDrone 和 DroneVehicle 两个域上系统比较 V/D/H/HC 四组特征，诚实报告（a）YOLO latent 因小样本过拟合失败，（b）B3 在外部域上净效用为负并被系统正确抑制
