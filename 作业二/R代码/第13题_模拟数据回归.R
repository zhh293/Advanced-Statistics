# 第13题：模拟数据 - 简单线性回归验证
# 高级统计方法 第2次作业
# 张鸿昊 20242081353

# ====== (a)-(c) 创建数据 ======
set.seed(1)
x <- rnorm(100)
eps <- rnorm(100, mean=0, sd=0.5)
y <- -1 + 0.5*x + eps
cat("向量y的长度:", length(y), "\n")
cat("真实参数: beta0 = -1, beta1 = 0.5\n")

# ====== (d) 散点图 ======
png("../图片输出/q13_散点图.png", width=600, height=450)
plot(x, y, main="Simulated Data: Y = -1 + 0.5X + eps",
     xlab="X", ylab="Y", col="darkgray", pch=16)
dev.off()

# ====== (e) 拟合线性回归 ======
lm.fit <- lm(y ~ x)
summary(lm.fit)
cat("估计系数: beta0_hat =", coef(lm.fit)[1], 
    ", beta1_hat =", coef(lm.fit)[2], "\n")

# ====== (f) 散点图 + 回归线 + 真实线 ======
png("../图片输出/q13_回归线对比.png", width=600, height=450)
plot(x, y, main="Least Squares vs True Line (sd=0.5)",
     xlab="X", ylab="Y", col="darkgray", pch=16)
abline(lm.fit, col="blue", lwd=2)
abline(a=-1, b=0.5, col="red", lwd=2, lty=2)
legend("topleft", legend=c("Least Squares", "True Line (Y=-1+0.5X)"),
       col=c("blue", "red"), lwd=2, lty=c(1,2))
dev.off()

# ====== (g) 多项式回归 ======
lm.fit2 <- lm(y ~ x + I(x^2))
summary(lm.fit2)
cat("X^2项的p值:", summary(lm.fit2)$coef[3,4], "\n")

# ====== (h) 低噪声数据 ======
set.seed(1)
x2 <- rnorm(100)
eps2 <- rnorm(100, mean=0, sd=0.1)
y2 <- -1 + 0.5*x2 + eps2
lm.fit3 <- lm(y2 ~ x2)
summary(lm.fit3)

png("../图片输出/q13_低噪声.png", width=600, height=450)
plot(x2, y2, main="Less Noise (sd=0.1)",
     xlab="X", ylab="Y", col="darkgray", pch=16)
abline(lm.fit3, col="blue", lwd=2)
abline(a=-1, b=0.5, col="red", lwd=2, lty=2)
legend("topleft", legend=c("Least Squares", "True Line"),
       col=c("blue", "red"), lwd=2, lty=c(1,2))
dev.off()

# ====== (i) 高噪声数据 ======
set.seed(1)
x3 <- rnorm(100)
eps3 <- rnorm(100, mean=0, sd=1.0)
y3 <- -1 + 0.5*x3 + eps3
lm.fit4 <- lm(y3 ~ x3)
summary(lm.fit4)

png("../图片输出/q13_高噪声.png", width=600, height=450)
plot(x3, y3, main="More Noise (sd=1.0)",
     xlab="X", ylab="Y", col="darkgray", pch=16)
abline(lm.fit4, col="blue", lwd=2)
abline(a=-1, b=0.5, col="red", lwd=2, lty=2)
legend("topleft", legend=c("Least Squares", "True Line"),
       col=c("blue", "red"), lwd=2, lty=c(1,2))
dev.off()

# ====== (j) 置信区间比较 ======
cat("\n原始数据 (sd=0.5) 的置信区间:\n")
print(confint(lm.fit))
cat("\n低噪声 (sd=0.1) 的置信区间:\n")
print(confint(lm.fit3))
cat("\n高噪声 (sd=1.0) 的置信区间:\n")
print(confint(lm.fit4))

# ====== 三组对比图 ======
png("../图片输出/q13_三组噪声对比.png", width=900, height=350)
par(mfrow=c(1,3))

plot(x2, y2, main="Low Noise (sd=0.1)", xlab="X", ylab="Y", 
     col="darkgray", pch=16, ylim=c(-3,2))
abline(lm.fit3, col="blue", lwd=2)
abline(a=-1, b=0.5, col="red", lwd=2, lty=2)

plot(x, y, main="Medium Noise (sd=0.5)", xlab="X", ylab="Y",
     col="darkgray", pch=16, ylim=c(-3,2))
abline(lm.fit, col="blue", lwd=2)
abline(a=-1, b=0.5, col="red", lwd=2, lty=2)

plot(x3, y3, main="High Noise (sd=1.0)", xlab="X", ylab="Y",
     col="darkgray", pch=16, ylim=c(-3,2))
abline(lm.fit4, col="blue", lwd=2)
abline(a=-1, b=0.5, col="red", lwd=2, lty=2)

dev.off()

cat("第13题图片输出完成\n")
