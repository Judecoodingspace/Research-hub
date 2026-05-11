# Kang 2022 Task-Oriented Image Transmission → Paper 3 启发

> 来源：`papercard/UAV-Task-Oriented-Communication/2022_Kang_Task_Oriented_Image_Transmission_Scene_Classification_UAV.md`

## 场景启发

1. **信道+内容联合感知架构**：Kang 2022将信道增益作为policy network输入（非后验约束）。这直接支撑当前论文Layer 2的设计——A2A链路质量应作为pair选择的输入特征，而非仅作为约束条件

## 建模启发

2. **单步MDP与one-step selector同构**：Kang 2022建模为单步MDP（每张图独立决策），与当前论文的one-step contextual selector一致。可引用Kang 2022证明"单步决策在任务导向传输中是可行的"
3. **精度-延迟联合奖励函数**：`reward = -α×CE_loss - β×T_up` 与当前论文 `utility = delta_quality - λ×latency - λ×payload` 结构同构

## 实验启发

4. **warning: Kang 2022无消融实验**——这恰是当前论文应避免的错误。当前论文的V/D/H/HC消融正好弥补这类缺陷
5. **建议增加link-agnostic baseline**：utility公式中移除A2A延迟项，仅用感知增益选pair——证明链路感知的必要性

## 写作启发

6. Kang 2022的"信道+内容联合"论证链可直接平移："A2A链路质量动态变化 → pair选择不能只看后端算力 → 必须将链路延迟和排队状态纳入效用函数"

## 应避免

- Kang 2022最大缺陷：没有讨论"why DRL, not simpler"——当前论文必须写"why Ridge, not DNN/DRL"
