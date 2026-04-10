# VSCode + Codex 文献阅读与产出工作流

## 1. 文档目的
这份文档用于把当前已经摸索出的 `VSCode + Codex` 文献阅读流程迁移到新的电脑，尤其适合实验室 PC 场景。目标不是只“看论文”，而是形成一套稳定、可复用、可落盘的研究资料生产流程，包括：

- 元数据初筛
- PDF 正文精读
- 结构化 paper card
- 多篇 compare
- gap 提炼
- 后续写作支撑

这套流程的核心原则是：

- 以 `workspace` 为中心组织材料
- 用 `Agents.md.txt` 约束分析口径
- 用结构化目录沉淀中间结果
- 用明确提示词驱动 Codex 输出到文件，而不是只停留在对话里
- 所有结论优先基于 `metadata + PDF + notes`，信息不足时明确写 `待确认`

---

## 2. 迁移前要准备什么

### 2.1 软件环境
- VSCode
- Codex 可用环境
  - 你当前使用的 Codex 桌面端或 VSCode 集成环境都可以
- Python 3.12 或 3.13
- 一个项目级虚拟环境 `.venv`
- PDF 解析库
  - `pymupdf`
  - `pdfplumber`
- 可选工具
  - Zotero：管理论文与导出 metadata/notes
  - PDFgear：人工查看、OCR、辅助导出文本
  - OneDrive 或 Git：多机同步

### 2.2 推荐安装步骤
在新电脑上打开 PowerShell，进入项目根目录后执行：

```powershell
python -m venv D:\Research-hub\.venv
D:\Research-hub\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pymupdf pdfplumber
```

如果激活虚拟环境时报执行策略错误，先运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后再执行：

```powershell
D:\Research-hub\.venv\Scripts\Activate.ps1
```

### 2.3 最低可用验证
在 VSCode 终端中验证：

```powershell
python --version
python -m pip show pymupdf
python -m pip show pdfplumber
```

如果要测试 PDF 能否抽正文，可执行：

```powershell
@'
import fitz
pdf = fitz.open(r"D:\Research-hub\papers\UAV-Multi-Model\Ren 等 - 2024 - Multimodal Virtual Semantic Communication for Tiny-Machine-Learning-Based UAV Task Execution.pdf")
print(pdf[0].get_text()[:2000])
'@ | python -
```

若能打印出标题、摘要、正文片段，说明 PDF 提取链路已经可用。

---

## 3. 推荐目录结构

建议把整个研究工作区做成一个统一根目录，例如：

```text
Research-hub/
├─ .venv/
├─ Agents.md.txt
├─ metadata/
│  ├─ 2026-04-09_uav-multi-model_zotero-weekly_raw.csv
│  └─ ...
├─ papers/
│  ├─ UAV-Multi-Model/
│  ├─ UAV-SemCom/
│  └─ ...
├─ notes/
│  ├─ UAV-Multi-Model/
│  └─ ...
├─ papercard/
│  ├─ UAV-Multi-Model/
│  └─ ...
├─ compare/
│  ├─ UAV-Multi-Model/
│  └─ ...
├─ gap_map/
│  ├─ UAV-Multi-Model/
│  └─ ...
├─ related_work_bank/
│  ├─ topic_summaries/
│  └─ ...
├─ writing_support/
│  ├─ background/
│  ├─ related_work/
│  ├─ method_logic/
│  └─ ...
├─ prompts/
│  ├─ screening_prompt.md
│  ├─ papercard_prompt.md
│  ├─ compare_prompt.md
│  └─ gap_prompt.md
└─ scripts/
   ├─ extract_pdf_text.py
   └─ ...
```

### 3.1 关键目录作用
- `metadata/`
  - Zotero 导出的题目、作者、摘要、年份、DOI、URL 等
- `papers/`
  - 原始 PDF，按主题分文件夹
- `notes/`
  - Zotero 导出的 item notes、annotation notes
- `papercard/`
  - 每篇论文的结构化精读卡片
- `compare/`
  - 同主题论文横向比较
- `gap_map/`
  - 研究空白、切入点、创新方向
- `related_work_bank/`
  - 可直接复用到论文写作的综述素材
- `writing_support/`
  - 背景、研究意义、研究内容、贡献表达等写作材料
- `prompts/`
  - 常用提示词模板，便于多机迁移
- `scripts/`
  - 可复用的小脚本，如 PDF 正文抽取

### 3.2 命名建议
- 主题目录尽量短而稳定，例如：
  - `UAV-Multi-Model`
  - `Task-Oriented-SemCom`
  - `Split-Inference`
- paper card 文件名建议：

```text
年份_第一作者_短标题.md
```

例如：

```text
2026_Guo_PE_MMSC_and_Resource_Management.md
2024_Ren_Multimodal_Virtual_Semantic_Communication.md
```

---

## 4. 前期准备建议

### 4.1 必备研究规则文件
把当前项目中的规则文件也一起迁移：

- `Agents.md.txt`

这份文件相当于你的“阅读标准”。它已经定义了：

- 默认子方向标签
- paper card 的 10 个固定部分
- compare 的维度
- gap 的提炼逻辑
- 输出风格与禁忌

在新电脑上，最稳妥的做法是：

- 保留同名文件 `Agents.md.txt`
- 放在工作区根目录
- 每次让 Codex 工作前，都显式引用“按 `Agents.md.txt` 规则执行”

### 4.2 输入材料的最低要求
至少准备：

- `metadata csv`
- 对应 PDF

最好再补齐：

- `notes`
- `annotations`

如果没有 notes，也可以先做，但要明确要求 Codex：

- 不要把摘要复述当精读
- PDF 正文提不到的地方写 `待确认`

### 4.3 多机同步建议
如果你在主机、笔记本、实验室 PC 之间切换，建议同步以下内容：

- `metadata/`
- `papers/`
- `notes/`
- `papercard/`
- `compare/`
- `gap_map/`
- `Agents.md.txt`
- `prompts/`

不建议同步：

- `.venv/`
- 大缓存
- 临时抽取文本

原因是：

- Python 环境通常按机器单独重建更稳
- 研究材料需要同步，运行环境不必同步

---

## 5. 提示词设计原则

好用的 Codex 提示词，通常要同时交代 5 件事：

1. 任务阶段
- 是初筛、精读、比较、gap，还是写作支撑

2. 输入范围
- 明确告诉它读哪些 `metadata`、哪些 `PDF`、哪些 `notes`

3. 输出位置
- 明确告诉它生成到哪个目录、哪个文件

4. 分析口径
- 明确要求按 `Agents.md.txt` 规则执行

5. 证据边界
- 明确要求只基于 `metadata + PDF + notes`
- 不足时写 `待确认`
- 允许覆盖旧文件时要说清楚

### 5.1 一个高质量提示词的基本框架

```text
按照 D:\Research-hub\Agents.md.txt 中的规则执行。

任务：
- 对 [主题目录] 下的文献进行 [初筛 / 精读 / 比较 / gap 提炼]

输入：
- metadata: [路径]
- papers: [路径]
- notes: [路径，若有]

要求：
- 必须结合 PDF 正文，不要只复述摘要
- 只依据 metadata、PDF、notes，可确认的就写结论，不可确认的写“待确认”
- 输出为结构化 markdown
- 生成到 [输出路径]
- [是否允许覆盖旧文件]

研究主线：
- [例如：多无人机任务导向通信]
```

---

## 6. 常用提示词模板

### 6.1 初筛提示词

```text
按照 D:\Research-hub\Agents.md.txt 中的规则执行。

请基于以下 metadata 对该主题论文做相关性初筛，不要生成摘要堆叠：
- metadata: D:\Research-hub\metadata\2026-04-09_uav-multi-model_zotero-weekly_raw.csv
- papers: D:\Research-hub\papers\UAV-Multi-Model

要求：
- 围绕“多无人机任务导向通信”判断相关性
- 对每篇标注高/中/低相关
- 给出子方向标签
- 写明初筛理由
- 输出到 D:\Research-hub\papercard\UAV-Multi-Model\index.md
- 允许覆盖旧文件
```

### 6.2 单篇精读 / paper card 提示词

```text
按照 D:\Research-hub\Agents.md.txt 中的规则执行。

请基于以下材料重写这篇论文的 paper card：
- metadata: D:\Research-hub\metadata\2026-04-09_uav-multi-model_zotero-weekly_raw.csv
- pdf: D:\Research-hub\papers\UAV-Multi-Model\Guo 等 - 2026 - Perception Enhanced Multimodal Multitask Semantic Communication and Resource Management for UAV-Assi.pdf
- notes: 若无，则按“现有材料版”执行

要求：
- 必须结合 PDF 正文，不要只依据摘要
- 输出固定包含 Problem / Setting / Core Idea / Key Mechanism / Experiments / Strength / Weakness / Reusable Part / Attack Point / Relation to My Topic / 证据完整性说明
- 研究主线固定为“多无人机任务导向通信”
- 无法确认的地方写“待确认”
- 输出到 D:\Research-hub\papercard\UAV-Multi-Model\2026_Guo_PE_MMSC_and_Resource_Management.md
- 允许覆盖旧文件
```

### 6.3 多篇 compare 提示词

```text
按照 D:\Research-hub\Agents.md.txt 中的规则执行。

请比较以下主题下的论文：
- metadata: D:\Research-hub\metadata\2026-04-09_uav-multi-model_zotero-weekly_raw.csv
- papers: D:\Research-hub\papers\UAV-Multi-Model

要求：
- 比较维度至少包括：问题定义、场景设定、方法机制、评价指标、局限与空白
- 不要按“每篇一段摘要”堆叠
- 必须围绕“多无人机任务导向通信”主线比较差异和共性缺口
- 输出到 D:\Research-hub\compare\UAV-Multi-Model\overview.md
- 允许覆盖旧文件
```

### 6.4 gap 提示词

```text
按照 D:\Research-hub\Agents.md.txt 中的规则执行。

请基于以下 compare 和 paper card 提炼研究空白：
- compare: D:\Research-hub\compare\UAV-Multi-Model\overview.md
- paper cards: D:\Research-hub\papercard\UAV-Multi-Model

要求：
- gap 必须来自多篇论文的共性缺陷，不要凭空发明创新点
- 必须围绕“多无人机任务导向通信”
- 重点关注：多 UAV 协同、异构算力、感知-通信-推理联合优化、多视角路径规划联动
- 输出到 D:\Research-hub\gap_map\UAV-Multi-Model\task_oriented_comm_gap.md
- 允许覆盖旧文件
```

### 6.5 写作支撑提示词

```text
按照 D:\Research-hub\Agents.md.txt 中的规则执行。

请基于以下 compare 与 gap，生成一份可用于论文写作的 related work 素材：
- compare: D:\Research-hub\compare\UAV-Multi-Model\overview.md
- gap: D:\Research-hub\gap_map\UAV-Multi-Model\task_oriented_comm_gap.md

要求：
- 不写宣传稿
- 围绕“多无人机任务导向通信”
- 输出学术化、可直接复用的中文段落
- 输出到 D:\Research-hub\writing_support\related_work\uav_multi_model_related_work.md
```

---

## 7. 推荐实际工作流

### 阶段 1：导入材料
- Zotero 导出 metadata csv
- 下载或整理 PDF 到 `papers/主题名/`
- 导出 notes 到 `notes/主题名/`

### 阶段 2：验证 PDF 可抽取
- 先用 `PyMuPDF` 测 1 篇论文
- 如果能抽出标题、摘要、正文，就可以批量走
- 如果不行，再考虑 OCR 或 PDFgear 导出文本

### 阶段 3：初筛
- 先让 Codex 基于 metadata 生成 `index.md`
- 目的是判断哪些文献高相关，哪些值得精读

### 阶段 4：paper card
- 对高相关论文逐篇生成结构化 card
- 这一步一定要强调“基于 PDF 正文重写”

### 阶段 5：compare
- 对同主题论文做横向比较
- 重点找差异、共性与系统性遗漏

### 阶段 6：gap map
- 在 compare 基础上提炼真正有价值的研究空白
- 不是“关键词拼装创新点”，而是“共性缺陷 + 研究主线”

### 阶段 7：写作支撑
- 把 compare 和 gap 转成：
  - related work
  - 研究背景
  - 研究意义
  - 方法设计逻辑
  - baseline 选择理由

---

## 8. 在 VSCode 中如何组织操作

### 8.1 推荐打开方式
- 在 VSCode 里直接打开 `Research-hub` 根目录
- 左侧资源管理器固定展开：
  - `metadata`
  - `papers`
  - `notes`
  - `papercard`
  - `compare`
  - `gap_map`

### 8.2 推荐工作习惯
- 每次只处理一个主题目录
- 每次提示词都带上：
  - 输入路径
  - 输出路径
  - 是否覆盖
  - 研究主线
  - 证据边界
- 重要产出一定要求“落盘到 md 文件”
- 对话里只保留摘要结论，正式内容沉淀到目录中

### 8.3 推荐保留的固定文件
- `Agents.md.txt`
- `VSCode_Codex_Literature_Reading_Workflow.md`
- `prompts/` 下的模板文件

这 3 类文件是最值得迁移到新电脑的“流程资产”。

---

## 9. 常见问题与解决

### 9.1 没有 notes 能不能做
可以，但提示词里要明确：

- 先做 `现有材料版`
- 仅基于 `metadata + PDF`
- 信息不足处写 `待确认`

### 9.2 PDF 抽不出正文怎么办
优先顺序建议：

1. 先用 `PyMuPDF`
2. 再试 `pdfplumber`
3. 不行就用 `PDFgear` 导出文本
4. 还不行再做 OCR

### 9.3 Codex 容易只复述摘要怎么办
提示词里必须写：

- 必须结合 PDF 正文
- 不要只复述摘要
- 要提取方法、模型、实验、局限

### 9.4 compare 容易变成摘要堆叠怎么办
提示词里必须写：

- 不要按每篇一段摘要重复堆叠
- 必须围绕当前研究主线比较差异和缺口

### 9.5 如何避免文件越写越乱
做法是：

- 主题单独建目录
- paper card 单篇单文件
- compare 单主题一文件
- gap 单主题一文件
- 文件名固定格式

---

## 10. 实验室 PC 迁移清单

把下面这些带过去，基本就能复现：

- `Research-hub/` 工作区
- `Agents.md.txt`
- `metadata/`
- `papers/`
- `notes/`（若有）
- `papercard/`
- `compare/`
- `gap_map/`
- `prompts/`（若你后续建立了）
- 本文档

在新电脑上只需再做两件事：

1. 重建 Python 虚拟环境  
2. 测试 PDF 正文提取是否正常

---

## 11. 最小可复用模板

如果你以后只想保留最小版本，建议至少保留：

```text
Research-hub/
├─ Agents.md.txt
├─ metadata/
├─ papers/
├─ notes/
├─ papercard/
├─ compare/
├─ gap_map/
└─ VSCode_Codex_Literature_Reading_Workflow.md
```

这是最小但仍然可用的一套结构。

---

## 12. 一句话工作流

先用 `metadata` 做初筛，再用 `PDF + notes` 做结构化 paper card，然后做 compare，再提炼 gap，最后把 compare 和 gap 变成写作支撑材料；整个过程都通过 `Agents.md.txt` 统一分析口径，并把输出稳定落盘到 markdown 文件中。
