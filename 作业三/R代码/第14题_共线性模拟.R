# 第14题：共线性模拟实验
# 高级统计方法 第3次作业
# 张鸿昊 20242081353

# ====== (a) 生成数据 ======
set.seed(1)
x1 <- runif(100)
x2 <- 0.5 * x1 + rnorm(100) / 10
y <- 2 + 2*x1 + 0.3*x2 + rnorm(100)

# 真实模型: Y = 2 + 2*X1 + 0.3*X2 + eps
# beta0 = 2, beta1 = 2, beta2 = 0.3

# ====== (b) x1和x2的相关性 ======
cor(x1, x2)
png("../图片输出/q14_x1x2相关性.png", width=600, height=450)
plot(x1, x2, main="Correlation between X1 and X2",
     xlab="X1", ylab="X2", col="darkgray", pch=16)
abline(lm(x2 ~ x1), col="red", lwd=2)
text(0.2, 0.8, paste("r =", round(cor(x1,x2), 3)), cex=1.2)
dev.off()

# ====== (c) y对x1和x2的回归 ======
lm.fit <- lm(y ~ x1 + x2)
summary(lm.fit)
cat("beta0_hat =", coef(lm.fit)[1], "\n")
cat("beta1_hat =", coef(lm.fit)[2], "\n")
cat("beta2_hat =", coef(lm.fit)[3], "\n")

# ====== (d) y对x1的回归 ======
lm.fit1 <- lm(y ~ x1)
summary(lm.fit1)

# ====== (e) y对x2的回归 ======
lm.fit2 <- lm(y ~ x2)
summary(lm.fit2)

# ====== (f) 结果是否矛盾 ======
cat("\n=== 结果对比 ===\n")
cat("双变量回归 x1的p值:", summary(lm.fit)$coef[2,4], "\n")
cat("双变量回归 x2的p值:", summary(lm.fit)$coef[3,4], "\n")
cat("单变量回归 x1的p值:", summary(lm.fit1)$coef[2,4], "\n")
cat("单变量回归 x2的p值:", summary(lm.fit2)$coef[2,4], "\n")

# VIF计算
cat("\nVIF(x1) =", 1/(1-cor(x1,x2)^2), "\n")

# ====== (g) 添加异常观测 ======
x1 <- c(x1, 0.1)
x2 <- c(x2, 0.8)
y <- c(y, 6)

lm.fit_new <- lm(y ~ x1 + x2)
summary(lm.fit_new)

lm.fit1_new <- lm(y ~ x1)
summary(lm.fit1_new)

lm.fit2_new <- lm(y ~ x2)
summary(lm.fit2_new)

# 诊断图
png("../图片输出/q14_新观测诊断.png", width=700, height=600)
par(mfrow=c(2,2))
plot(lm.fit_new)
dev.off()

# 检查新观测点是否为高杠杆点或异常值
cat("\n新观测点(101)的杠杆值:", hatvalues(lm.fit_new)[101], "\n")
cat("新观测点(101)的学生化残差:", rstudent(lm.fit_new)[101], "\n")

cat("第14题图片输出完成\n")
