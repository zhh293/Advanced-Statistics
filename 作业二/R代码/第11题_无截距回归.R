# 第11题：不含截距的简单线性回归
# 高级统计方法 第2次作业
# 张鸿昊 20242081353

# ====== 生成数据 ======
set.seed(1)
x <- rnorm(100)
y <- 2*x + rnorm(100)

# ====== (a) y对x的无截距回归 ======
lm.fit1 <- lm(y ~ x + 0)
summary(lm.fit1)

# ====== (b) x对y的无截距回归 ======
lm.fit2 <- lm(x ~ y + 0)
summary(lm.fit2)

# ====== (c) 比较t统计量 ======
cat("y~x+0 的 t统计量:", summary(lm.fit1)$coef[1,3], "\n")
cat("x~y+0 的 t统计量:", summary(lm.fit2)$coef[1,3], "\n")

# ====== (d) 手动验证t统计量公式 ======
n <- length(x)
t_val <- sqrt(n-1) * sum(x*y) / sqrt(sum(x^2)*sum(y^2) - (sum(x*y))^2)
cat("手动计算的t统计量:", t_val, "\n")

# ====== (e) 有截距回归的t统计量比较 ======
cat("y~x (有截距) 的 t统计量:", summary(lm(y ~ x))$coef[2,3], "\n")
cat("x~y (有截距) 的 t统计量:", summary(lm(x ~ y))$coef[2,3], "\n")

# ====== 绘图 ======
png("../图片输出/q11_无截距回归.png", width=600, height=450)
plot(x, y, main="Y vs X (No Intercept Regression)",
     xlab="X", ylab="Y", col="darkgray", pch=16)
abline(lm.fit1, col="blue", lwd=2)
abline(lm(y ~ x), col="red", lwd=2, lty=2)
legend("topleft", legend=c("No Intercept", "With Intercept"),
       col=c("blue", "red"), lwd=2, lty=c(1,2))
dev.off()

cat("第11题图片输出完成\n")
