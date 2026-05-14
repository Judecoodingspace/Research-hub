# CVN-DSA Rebuttal Workspace

> 退稿重投工作区 | 原稿号 `VT-2026-02444` | IEEE TVT | 120 天重投窗口

## 目录结构

```
rebuttal/cvn-dsa/
├── README.md                                  ← 本文件
│
├── source/                                    ← 📥 原始材料（只读，不修改）
│   ├── decision_letter_raw.md                 ← 编辑决定信原文
│   └── review_comments_raw.md                 ← 4 位审稿人完整评语原文
│
├── planning/                                  ← 📋 意见整理与修改计划
│   ├── review_comments_clean.md               ← 规范化编号 + 符号纠错 + Author note
│   ├── revision_matrix.md                     ← 35 条意见→action→severity→status 核心矩阵
│   ├── revision_strategy.md                   ← 修改策略与 Path A/B 投资路线分析
│   └── revision_execution_plan.md             ← 阶段 0-6 分步执行计划 + 里程碑
│
├── analysis/                                  ← 🔬 专题深入分析
│   ├── advisor_discussion_brief_bilingual.md  ← 博导讨论稿（双语）
│   └── novelty_revision_directions_bilingual.md ← 创新性重写方案（双语）
│
└── outputs/                                   ← 📤 产出物
    ├── response_letter.md                     ← Response Letter 草稿（待填充）
    └── code_migration_guide.md                ← 仿真代码迁移方案
```

## 使用工作流

1. 原始材料放 `source/` → 只读
2. 规范化整理在 `planning/` → 修改矩阵是核心工作文档
3. 深入分析在 `analysis/` → 与导师讨论、创新性重写
4. 产出物在 `outputs/` → Response Letter + 代码方案
