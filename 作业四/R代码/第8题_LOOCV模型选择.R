# 第8题：模拟数据 - 留一交叉验证(LOOCV)进行模型选择
# 高级统计方法 第4次作业
# 张鸿昊 20242081353

library(boot)

# ====== (a) 生成模拟数据 ======
set.seed(1)
x <- rnorm(100)
y <- x - 2 * x^2 + rnorm(100)
# n = 100（观测数）, p = 2（预测变量个数：x 和 x^2）
# 真实模型: Y = X - 2*X^2 + eps，即 beta0=0, beta1=1, beta2=-2

cat("n =", length(x), ", p = 2\n")
cat("真实模型: Y = X - 2*X^2 + epsilon\n")

# ====== (b) 散点图 ======
png("../图片输出/q8_散点图.png", width = 600, height = 450)
plot(x, y, main = "Scatter plot of Y vs X",
     xlab = "X", ylab = "Y", col = "darkblue", pch = 16)
dev.off()
# 散点图呈倒U形（二次曲线关系），说明X与Y为非线性关系

# ====== (c) 设随机种子，计算四个模型的LOOCV误差 ======
Data <- data.frame(x = x, y = y)

set.seed(1)
cv.errors <- rep(0, 4)
for (i in 1:4) {
  glm.fit <- glm(y ~ poly(x, i), data = Data)
  cv.errors[i] <- cv.glm(Data, glm.fit)$delta[1]
}
cat("\n=== (c) seed=1 的LOOCV误差 ===\n")
for (i in 1:4) {
  cat("模型", i, "(", i, "次多项式) LOOCV误差 =", cv.errors[i], "\n")
}

# ====== (d) 换另一个随机种子重复 ======
set.seed(100)
cv.errors2 <- rep(0, 4)
for (i in 1:4) {
  glm.fit <- glm(y ~ poly(x, i), data = Data)
  cv.errors2[i] <- cv.glm(Data, glm.fit)$delta[1]
}
cat("\n=== (d) seed=100 的LOOCV误差 ===\n")
for (i in 1:4) {
  cat("模型", i, "LOOCV误差 =", cv.errors2[i], "\n")
}
cat("结论：两次结果完全相同。因为LOOCV不涉及随机划分（每个观测轮流做测试集），\n")
cat("      所以随机种子不影响LOOCV结果。\n")

# ====== (e) 哪个模型LOOCV误差最小 ======
cat("\n=== (e) ===\n")
cat("LOOCV误差最小的模型:", which.min(cv.errors), "次多项式\n")
cat("符合预期：真实模型是二次的，所以二次模型误差最小。\n")

# LOOCV误差随多项式阶数变化图
png("../图片输出/q8_LOOCV误差.png", width = 600, height = 450)
plot(1:4, cv.errors, type = "b", col = "red", pch = 16, lwd = 2,
     xlab = "Polynomial Degree", ylab = "LOOCV Error",
     main = "LOOCV Error vs Polynomial Degree")
dev.off()

# ====== (f) 系数显著性 ======
cat("\n=== (f) 四次多项式模型的系数显著性 ===\n")
glm.fit4 <- glm(y ~ poly(x, 4), data = Data)
print(summary(glm.fit4)$coefficients)
cat("结论：只有1次项和2次项显著(p<0.05)，3次和4次项不显著。\n")
cat("这与LOOCV的结论一致：真实模型是二次的。\n")

cat("第8题图片输出完成\n")
