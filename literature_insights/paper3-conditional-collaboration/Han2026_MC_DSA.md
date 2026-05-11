# Han 2026 MC-DSA → Paper 3 启发

> 来源：`papercard/UAV-Semantic-Communication/2026_Han_MC_DSA_Multi_UAV_Cooperative_Deep_Semantic_Autoencoders.md`

## 场景启发

1. **T-UAV/S-UAV角色命名**：将"前侧UAV→Task UAV""后侧UAV→Support UAV"正式化，提升论文可读性
2. **图像退化驱动的触发可视化**：放clean vs. degraded场景的对比图，让读者直观理解"为什么需要trigger"
3. **多S-UAV同时激活 vs. 单pair选择**：当前论文每帧只选一个(back, action)，Han 2026可激活多个——这是当前论文的局限，应列为future work

## 建模启发

4. **Query-Key端到端学习 → 质疑手工效用函数**：Han 2026不需要oracle utility标签，从分割损失中学会何时协作。当前论文需要预跑oracle——更脆弱但更可解释。必须在论文中承认这个trade-off
5. **Soft Training / Hard Testing两阶段策略**：训练用连续权重，测试用二值门控——未来升级Layer 2时可复用
6. **语义特征 vs. Proposal Metadata传输粒度**：显式对比两种方案，将proposal论证为更通信高效的语义表征

## 算法与实验启发

7. **阈值灵敏度分析 → 预算参数校准**：仿照sth分析，做utility vs. budget曲线，找效用饱和点
8. **Random Selection负收益 → 证明选择机制必要性**：增加`random-pair` baseline
9. **自适应池化 → 多分辨率V特征**：2-3个分辨率下采样分别提V特征取均值，低成本增强
10. **端到端联合优化 → 分层优化的局限**：必须在Discussion中承认分层≠全局最优

## 一句话收束

Han 2026："让T-UAV发query，只有语义相关的S-UAV才响应"
当前论文应能说清："用17个像素特征预测效用，在预算内只触发最值得的图像"——如果说不清，就是堆砌
