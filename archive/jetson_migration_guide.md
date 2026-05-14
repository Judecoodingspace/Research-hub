# Jetson 实验项目迁移指南

> 目标：从当前膨胀的项目目录迁移到新的多 UAV 协同实验项目，保留有效文件，归档废弃 idea。

---

## 一、给 Codex 的启动提示词

将以下内容粘贴到 Jetson 的 Codex/Copilot 对话框中：

```text
## 任务：从当前膨胀的项目目录迁移到新的多 UAV 协同实验项目

### 背景
当前项目目录过于庞大，包含大量已被推翻的 idea 的遗留脚本和输出。
需要启动一个新的多 UAV 协同实验项目。请按以下步骤执行。

### Step 1：扫描当前目录结构

先执行：
```bash
find . -maxdepth 1 -type d | sort
```
然后对每个一级子目录列出内容摘要（只列文件名，不递归太深）。

输出一个目录结构树，标注每个子目录的用途（如不确定写"待确认"）。

### Step 2：分类文件

对每个文件/子目录，按以下标准分类：

**必迁（复用）**：
- 文件名包含 `EXPERIMENT_CONCEPTS`、`README`、`index` 的 `.md` 文档
- 文件名包含 `experiment`、`concept`、`result`、`finding` 的关键实验记录 `.md`
- **排除**：零散的随手笔记、过时的设计草稿、已被推翻 idea 的分析文档
- 预测器脚本（名称含 `predict`、`trigger`、`ridge`）
- Backend review 脚本（名称含 `backend_review`、`fusion`、`B2`、`B3`）
- Utility/oracle 计算脚本（名称含 `utility`、`oracle`）
- 通信选择器评估脚本（名称含 `selector`、`comm`）
- V/D/H 特征提取脚本（名称含 `feature`、`visual_proxy`）
- 数据路径和退化场景标签配置文件
- MC 采样 / Monaco 相关脚本

**应归档（已废弃——明确证明无价值，不留后路）**：
- 文件名含 `deprecated`、`old`、`v0`、`v1`、`backup`、`draft`
- 重复的旧版本输出 CSV（同实验多日期版本，只留最新）
- `*.log` 日志文件
- 中间产物 `*.pkl`、`*.pt`（可重新生成）

**暂不迁移（当前框架下效用不足，留待后续项目中换用不同模型重评）**：
- H 特征全量提取脚本（1870 维 YOLO latent）——当前 Ridge 下过拟合，换 PCA/正则化后可能有效
- ROI fallback 策略——已有负结果，但可能因线性效用限制
- split-feature S0/S1/S2——当前主线不需要，但可能在新场景中有用

**不确定**：
- 无法从文件名判断用途的，列出后暂停，等我确认

### Step 3：确认当前的"有效 idea 清单"

以下是已知有效的 idea（必须保留相关脚本和输出）：
- V 特征（17 维像素统计，纯 OpenCV）的定义和提取代码
- Ridge 回归预测器（线性模型，<1ms 推理）
- B2_RECALL / B3_TUNED 的后端融合验证
- utility formula：`utility = delta_quality - λ×latency - λ×payload - precision_penalty`
- DroneVehicle full split 的 oracle utility 数据
- 5-seed 交叉验证评估框架
- budget_only / false_trigger_constrained / hard_topk 三种预算策略
- Front→Back pair 选择器（含 queue delay MC 采样）
- 概念词典 EXPERIMENT_CONCEPTS.md

以下是已知**在当前线性 Ridge 框架下效用不如 V 特征**的 idea（相关文件暂时不迁，但保留记号，在后续多机项目中重新评估——这些 idea 的失败可能来自线性模型的限制而非 idea 本身）：
- H 特征（1870 维 YOLO latent）——当前 Ridge 下过拟合；换用 PCA+Ridge 或适当正则化的非线性模型后可能有效，**留待重评**
- ROI fallback 策略——已有负结果，但可能因线性效用函数限制，**留待重评**
- split-feature S0/S1/S2——不是当前主线，但可能在新多机场景中有不同角色，**暂不迁、不否定**

### Step 4：拟定迁移计划（先计划，再执行）

**重要：不要直接动手迁移。先输出一份迁移计划，等我确认后再执行。**

迁移计划必须包含：
1. 列出所有**必迁文件**（完整路径），按原有目录分组
2. 列出所有**应归档文件**（完整路径），说明归档原因
3. 列出所有**不确定文件**（完整路径），说明为什么不确定
4. 目标新文件夹路径（如 `uav-multi-collab/`）

**新项目结构**：

**不做任何目录重组。** 直接将必迁文件按原有目录结构复制到新文件夹根目录下。
不要新建子文件夹、不要移动文件位置、不要改变文件之间的相对路径关系。
新文件夹的唯一变化是：不包含被废弃的文件。

```
新项目/
├── (原有子目录，结构与旧项目完全一致)
├── (只包含必迁文件，废弃文件不在此)
│
└── archive/                          ← 这是唯一新增的目录
    └── migration_log.md              ← 迁移日志（记录哪些文件没带、为什么）
```

**旧项目完全不动。** 不创建 `archive/`，不移动或删除旧项目中的任何文件。

### Step 5：执行迁移（人工确认后）

1. 在我的确认下，创建新项目文件夹
2. 将必迁文件**复制**（`cp`，不是 `mv`）到新项目对应位置（保持原有子目录结构）
3. 在新项目的 `archive/migration_log.md` 中记录：哪些文件迁移了、哪些废弃文件被排除、排除原因
4. 更新新项目的实验索引文件
5. **旧项目不做任何改动**

### 特别注意

- 旧项目完全不动——不删除、不移动任何文件
- 新项目中只放必迁文件（`cp`），废弃文件不带
- 文件中提到的"暂不迁移"类别的脚本，不迁但也不否定——在 `migration_log.md` 中标记为"待未来重评"
- 如果某个文件可能在未来需要参考但当前不需要执行，同样在 `migration_log.md` 中记录一笔
```

---

## 二、迁移原则

**目录结构**：新项目**完全保持原有目录组织**。不新建子文件夹、不移动文件位置、不改变相对路径关系。唯一新增的目录是 `archive/`，仅存放一份 `migration_log.md`。

**文件处理**：
| 操作 | 对象 | 说明 |
|------|------|------|
| `cp`（复制） | 必迁文件 | 旧项目 → 新项目（同路径） |
| 不动 | 所有文件 | 旧项目保持原样，不删除、不移动任何文件 |

**旧项目完全不动**——这是最高原则。

**新项目的 `archive/migration_log.md`** 记录：
- 哪些文件被迁移了
- 哪些文件被排除了、为什么
- 迁移日期

---

## 三、迁移后的验证清单

迁移完成后，在新项目根目录下执行：

- [ ] `python scripts/predictor/predict_v_trigger.py` 能跑通
- [ ] `python scripts/backend_review/run_backend_review.py` 能跑通
- [ ] `python scripts/comm_selector/pair_selector.py` 能跑通
- [ ] `experiments/index.md` 列出了所有有效实验
- [ ] `archive/migration_log.md` 记录了所有文件的去向
- [ ] `README.md` 写了快速开始步骤
