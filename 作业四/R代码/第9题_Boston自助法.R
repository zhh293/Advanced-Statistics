# 第9题：Boston住房数据集 - 自助法估计各种统计量的标准误差
# 高级统计方法 第4次作业
# 张鸿昊 20242081353

library(ISLR2)   # ISLR2包含Boston数据集（与MASS版本一致）
library(boot)
data(Boston)

# ====== (a) 估计medv的总体均值 ======
mu.hat <- mean(Boston$medv)
cat("(a) medv样本均值 mu.hat =", mu.hat, "\n")

# ====== (b) 估计mu.hat的标准误差（公式法） ======
# SE = 样本标准差 / sqrt(n)
se.formula <- sd(Boston$medv) / sqrt(nrow(Boston))
cat("(b) 公式法 SE(mu.hat) =", se.formula, "\n")

# ====== (c) 自助法估计mu.hat的标准误差 ======
boot.mean <- function(data, index) {
  return(mean(data[index]))
}
set.seed(1)
boot.mu <- boot(Boston$medv, boot.mean, R = 1000)
print(boot.mu)
se.boot <- sd(boot.mu$t)
cat("(c) 自助法 SE(mu.hat) =", se.boot, "\n")
cat("    与(b)非常接近，说明公式法和自助法结果一致。\n")

# ====== (d) 95%置信区间 ======
ci.boot <- c(mu.hat - 2 * se.boot, mu.hat + 2 * se.boot)
cat("\n(d) 自助法95%置信区间: [", ci.boot[1], ",", ci.boot[2], "]\n")
t.result <- t.test(Boston$medv)
cat("    t.test 95%置信区间: [", t.result$conf.int[1], ",",
    t.result$conf.int[2], "]\n")
cat("    两者非常接近。\n")

# ====== (e) 估计medv的中位数 ======
med.hat <- median(Boston$medv)
cat("\n(e) medv样本中位数 med.hat =", med.hat, "\n")

# ====== (f) 自助法估计中位数的标准误差 ======
boot.median <- function(data, index) {
  return(median(data[index]))
}
set.seed(1)
boot.med <- boot(Boston$medv, boot.median, R = 1000)
se.med <- sd(boot.med$t)
cat("(f) 自助法 SE(中位数) =", se.med, "\n")
cat("    中位数没有简单的标准误差公式，自助法是有效手段。\n")

# ====== (g) 估计第10%分位数 ======
mu.0.1 <- quantile(Boston$medv, 0.1)
cat("\n(g) medv第10%分位数 mu.0.1 =", mu.0.1, "\n")

# ====== (h) 自助法估计第10%分位数的标准误差 ======
boot.quant <- function(data, index) {
  return(quantile(data[index], 0.1))
}
set.seed(1)
boot.q <- boot(Boston$medv, boot.quant, R = 1000)
se.q <- sd(boot.q$t)
cat("(h) 自助法 SE(第10%分位数) =", se.q, "\n")
cat("    相对中位数较大，因为分位数对尾部数据更敏感。\n")

# 可视化各统计量的自助分布
png("../图片输出/q9_自助分布.png", width = 800, height = 350)
par(mfrow = c(1, 3))
hist(boot.mu$t, breaks = 30, col = "lightblue", main = "Bootstrap Mean",
     xlab = "mean(medv)")
abline(v = mu.hat, col = "red", lwd = 2)
hist(boot.med$t, breaks = 30, col = "lightgreen", main = "Bootstrap Median",
     xlab = "median(medv)")
abline(v = med.hat, col = "red", lwd = 2)
hist(boot.q$t, breaks = 30, col = "lightpink", main = "Bootstrap 10% Quantile",
     xlab = "10% quantile(medv)")
abline(v = mu.0.1, col = "red", lwd = 2)
dev.off()

cat("第9题图片输出完成\n")
