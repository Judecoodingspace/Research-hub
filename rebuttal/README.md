# Rebuttal 审稿意见与支撑文献管理

## 使用说明
- 本目录存放每篇论文的审稿意见、修改计划和文献支撑矩阵
- 核心用途：在查阅文献时快速判断**某论文的哪些观点/实验可以支撑审稿意见的回复**
- 工作流程：`审稿意见 → lit_support_matrix → 定向查阅支撑文献 → 写入回复策略`

## 目录结构
```
rebuttal/
├── README.md                           ← 本文件
├── cvn-dsa/                            ← CVN-DSA 小论文（已有审稿意见）
│   ├── reviewer_comments.md
│   ├── revision_plan.md
│   └── lit_support_matrix.md
└── paper3-conditional-collaboration/   ← Paper 3 小论文（实验完善中，待投稿）
    ├── reviewer_comments.md            ← 占位：投后填充
    ├── revision_plan.md               ← 占位：投后填充
    └── lit_support_matrix.md           ← 占位：投后填充
```

## 当前状态

| 论文 | 审稿状态 | rebuttal 完整度 |
|------|----------|:---:|
| CVN-DSA | 退稿重投，已有审稿意见 | ✅ 已填充 |
| Paper3 (Conditional Collaboration) | 实验完善中 | ⬜ 占位待投 |

## 使用提示
向 Codex 提问示例：
- "这篇论文的哪些实验结论可以支撑 CVN-DSA 审稿意见 R1-Q2 的回复？"
- "对比这篇论文和 CVN-DSA 已有支撑文献，是否有更强的论据可用？"
