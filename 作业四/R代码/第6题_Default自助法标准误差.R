# 第6题：Default数据集 - 逻辑斯蒂回归系数标准误差的两种估计
# 高级统计方法 第4次作业
# 张鸿昊 20242081353

library(ISLR2)
library(boot)
data(Default)

# ====== (a) 用glm()公式法估计income和balance系数的标准误差 ======
glm.fit <- glm(default ~ income + balance, data = Default, family = binomial)
summary(glm.fit)
# 公式法标准误差：income的SE约4.985e-06，balance的SE约2.274e-04

# ====== (b) 编写boot.fn()函数 ======
# 输入数据集和观测索引，输出income和balance的系数估计
boot.fn <- function(data, index) {
  fit <- glm(default ~ income + balance, data = data, family = binomial,
             subset = index)
  return(coef(fit)[2:3])  # 只返回income和balance的系数
}

# 测试boot.fn
set.seed(1)
boot.fn(Default, 1:nrow(Default))

# ====== (c) 用boot()自助法估计标准误差 ======
set.seed(1)
boot.result <- boot(Default, boot.fn, R = 1000)
print(boot.result)

# 自助法估计的标准误差
cat("\n自助法标准误差:\n")
cat("income SE  =", apply(boot.result$t, 2, sd)[1], "\n")
cat("balance SE =", apply(boot.result$t, 2, sd)[2], "\n")

# ====== (d) 比较两种方法 ======
glm.se <- summary(glm.fit)$coefficients[2:3, 2]
boot.se <- apply(boot.result$t, 2, sd)
compare <- data.frame(
  变量 = c("income", "balance"),
  公式法SE = glm.se,
  自助法SE = boot.se
)
cat("\n=== 两种方法对比 ===\n")
print(compare)

# 可视化对比
png("../图片输出/q6_自助法分布.png", width = 700, height = 350)
par(mfrow = c(1, 2))
hist(boot.result$t[, 1], breaks = 30, col = "lightblue",
     main = "Bootstrap: income coef", xlab = "income coefficient")
abline(v = coef(glm.fit)[2], col = "red", lwd = 2)
hist(boot.result$t[, 2], breaks = 30, col = "lightgreen",
     main = "Bootstrap: balance coef", xlab = "balance coefficient")
abline(v = coef(glm.fit)[3], col = "red", lwd = 2)
dev.off()

cat("第6题图片输出完成\n")
