# 第5题：多数表决法 vs 平均概率法的最终分类（概念+数值验证）
# 高级统计方法 第5次作业
# 张鸿昊 20242081353

# 10个自助样本估计的 P(Class is Red | X)
probs <- c(0.1, 0.15, 0.2, 0.2, 0.55, 0.6, 0.6, 0.65, 0.7, 0.75)

# 方法一：多数表决（majority vote）
# 每个样本先按0.5阈值分类，再取多数
votes <- ifelse(probs > 0.5, "Red", "Green")
n.red <- sum(votes == "Red")
n.green <- sum(votes == "Green")
cat("多数表决：Red票数 =", n.red, " Green票数 =", n.green, "\n")
cat("  -> 最终分类：", ifelse(n.red > n.green, "Red", "Green"), "\n\n")

# 方法二：平均概率（average probability）
avg <- mean(probs)
cat("平均概率 =", avg, "\n")
cat("  -> 最终分类：", ifelse(avg > 0.5, "Red", "Green"), "\n\n")

cat("结论：多数表决得到Red（6票>4票），平均概率得到Green（均值0.45<0.5）。\n")
cat("两种组合方法给出不同结果，说明集成时的组合策略会影响最终判别。\n")
