# 第3题：6个观测、2个变量，手动执行 K=2 的K均值聚类（概念+作图）
# 高级统计方法 第6次作业
# 张鸿昊 20242081353
#
# 数据：
#   观测  X1  X2
#    1    1   4
#    2    1   3
#    3    0   4
#    4    5   1
#    5    6   2
#    6    4   0

X <- matrix(c(1, 4,
              1, 3,
              0, 4,
              5, 1,
              6, 2,
              4, 0), ncol = 2, byrow = TRUE)
colnames(X) <- c("X1", "X2")

# ====== (b) 随机给每个观测分配类标签 ======
set.seed(3)
labels <- sample(c(1, 2), nrow(X), replace = TRUE)
cat("(b) 随机初始标签:", labels, "\n")

# ====== (c)(d)(e) 迭代：算类中心 -> 按欧式距离重新分配 -> 直到不变 ======
repeat {
  # (c) 计算每个类的类中心
  cent <- t(sapply(1:2, function(k) colMeans(X[labels == k, , drop = FALSE])))
  # (d) 按到类中心的欧式距离重新分配
  new.labels <- apply(X, 1, function(row) {
    d1 <- sum((row - cent[1, ])^2)
    d2 <- sum((row - cent[2, ])^2)
    if (d1 <= d2) 1 else 2
  })
  if (all(new.labels == labels)) break    # (e) 标签不再变化则停止
  labels <- new.labels
}
cat("(e) 收敛后的类标签:", labels, "\n")
cat("\n类中心:\n"); print(round(cent, 3))
cat("\n最终聚类: 类1 =", which(labels == 1), " 类2 =", which(labels == 2), "\n")

# 用内置kmeans验证
set.seed(1)
km <- kmeans(X, centers = 2, nstart = 20)
cat("kmeans()验证 类标签:", km$cluster, "\n")

# ====== (a)(f) 散点图，按最终类标签上色 ======
png("../图片输出/q3_手动K均值.png", width = 600, height = 600)
plot(X, col = ifelse(labels == 1, "red", "blue"), pch = 19, cex = 2.5,
     xlim = c(-1, 7), ylim = c(-1, 5), xlab = "X1", ylab = "X2",
     main = "K=2 K均值聚类结果")
text(X[, 1], X[, 2], labels = 1:6, pos = 4, cex = 1.2)
points(cent, pch = 8, cex = 3, lwd = 2,
       col = c("darkred", "darkblue"))  # 类中心用星号
legend("topright", legend = c("类1", "类2", "类中心"),
       col = c("red", "blue", "black"), pch = c(19, 19, 8))
dev.off()

cat("\n第3题图片输出完成\n")
