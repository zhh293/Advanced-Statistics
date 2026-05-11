# ============================================================
# ISLR 第2章 2.4节 第7题
# 题目类型：概念 + 手算验证
# 知识点：K近邻分类（KNN）、欧氏距离、偏差-方差权衡
# ============================================================
#
# 【题目背景】
# 给定6个训练观测点，每个点有3个特征(X1, X2, X3)和一个类别标签Y。
# 测试点为 (X1=0, X2=0, X3=0)，用KNN方法预测其类别。
#
# 【核心思路】
# KNN的核心是"距离"：找到训练集中距离测试点最近的K个邻居，
# 用这K个邻居中出现最多的类别作为预测结果（多数投票）。
# 欧氏距离公式：d = sqrt((x1-0)^2 + (x2-0)^2 + (x3-0)^2)
# ============================================================

# ------ 第(a)题：计算各点到测试点(0,0,0)的欧氏距离 ------
# 为什么要建data.frame：方便统一管理6个观测点的所有信息

obs <- data.frame(
  X1 = c(0,  2,  0,  0, -1,  1),   # 6个观测点的第1个特征
  X2 = c(3,  0,  1,  1,  0,  1),   # 6个观测点的第2个特征
  X3 = c(0,  0,  3,  2,  1,  1),   # 6个观测点的第3个特征
  Y  = c("Red","Red","Red","Green","Green","Red")  # 真实类别
)

# 计算每个点到原点(0,0,0)的欧氏距离
# 公式：d_i = sqrt(X1_i^2 + X2_i^2 + X3_i^2)
# 因为测试点坐标全为0，所以差值就是各特征值本身
obs$dist <- sqrt(obs$X1^2 + obs$X2^2 + obs$X3^2)

cat("=== 各观测点到测试点(0,0,0)的欧氏距离 ===\n")
print(obs)
# 结果：
# 观测点1: sqrt(0+9+0)  = 3.000  Red
# 观测点2: sqrt(4+0+0)  = 2.000  Red
# 观测点3: sqrt(0+1+9)  = 3.162  Red
# 观测点4: sqrt(0+1+4)  = 2.236  Green
# 观测点5: sqrt(1+0+1)  = 1.414  Green  ← 最近
# 观测点6: sqrt(1+1+1)  = 1.732  Red

# ------ 第(a)题：K=1时的预测 ------
# 为什么用which.min：找到距离最小的那个观测点的索引
k1_idx <- which.min(obs$dist)
cat("\n=== K=1 预测结果 ===\n")
cat("最近邻：观测点", k1_idx, "\n")
cat("距离：", round(obs$dist[k1_idx], 4), "\n")
cat("类别：", obs$Y[k1_idx], "\n")
cat("预测结果：Green\n")
# 解释：K=1时只看最近的1个邻居，观测点5距离最近(√2≈1.414)，
# 其类别为Green，所以预测为Green。

# ------ 第(b)题：K=3时的预测 ------
# 为什么用order：对距离从小到大排序，取前3个
sorted_idx <- order(obs$dist)   # 按距离升序排列的索引
k3_idx     <- sorted_idx[1:3]   # 取最近的3个

cat("\n=== K=3 预测结果 ===\n")
cat("最近3个邻居的索引：", k3_idx, "\n")
cat("对应类别：", obs$Y[k3_idx], "\n")
cat("Red票数：",   sum(obs$Y[k3_idx] == "Red"),   "\n")
cat("Green票数：", sum(obs$Y[k3_idx] == "Green"), "\n")
cat("预测结果：Red（多数投票，2:1）\n")
# 解释：K=3时看最近的3个邻居：
#   观测点5(Green, 1.414), 观测点6(Red, 1.732), 观测点2(Red, 2.000)
#   Red有2票，Green有1票，多数投票 → 预测为Red

# ------ 第(c)题：贝叶斯边界非线性时，最优K应大还是小？ ------
cat("\n=== 第(c)题分析 ===\n")
cat("结论：最优K值应较小\n")
cat("原因：\n")
cat("  - K越小 → 决策边界越灵活（锯齿状）→ 偏差小，方差大\n")
cat("  - K越大 → 决策边界越平滑（趋向线性）→ 偏差大，方差小\n")
cat("  - 贝叶斯边界高度非线性 → 需要灵活的模型来拟合 → 选小K\n")

# ------ 可视化：展示不同K值对决策边界的影响（2D示意） ------
# 为什么要画这个图：直观展示K大小对边界灵活性的影响
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q7_knn示意.png",
    width = 700, height = 350, res = 100)
par(mfrow = c(1, 2), mar = c(4, 4, 3, 1))

# 用2D投影展示观测点（忽略X3维度）
colors <- ifelse(obs$Y == "Red", "red", "darkgreen")
plot(obs$X1, obs$X2, col = colors, pch = 19, cex = 2,
     xlim = c(-2, 3), ylim = c(-1, 4),
     xlab = "X1", ylab = "X2",
     main = "观测点分布（X3维度已忽略）")
points(0, 0, pch = 4, cex = 2, lwd = 3, col = "blue")  # 测试点
text(obs$X1, obs$X2, labels = 1:6, pos = 3, cex = 0.8)
legend("topright", legend = c("Red", "Green", "测试点(0,0,0)"),
       col = c("red", "darkgreen", "blue"),
       pch = c(19, 19, 4), cex = 0.8)

# 距离排序可视化
barplot(sort(obs$dist), names.arg = sorted_idx,
        col = ifelse(obs$Y[sorted_idx] == "Red", "red", "darkgreen"),
        main = "各观测点到测试点的距离（升序）",
        xlab = "观测点编号", ylab = "欧氏距离",
        ylim = c(0, 3.5))
abline(h = obs$dist[sorted_idx[1]], lty = 2, col = "purple", lwd = 2)
abline(h = obs$dist[sorted_idx[3]], lty = 2, col = "orange", lwd = 2)
legend("topleft", legend = c("K=1边界", "K=3边界"),
       lty = 2, col = c("purple", "orange"), cex = 0.8)
dev.off()
cat("\n图片已保存：q7_knn示意.png\n")
