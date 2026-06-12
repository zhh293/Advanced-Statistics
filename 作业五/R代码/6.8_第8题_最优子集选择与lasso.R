# 第8题：模拟数据 - 最优子集选择、向前/向后逐步选择与lasso
# 高级统计方法 第5次作业
# 张鸿昊 20242081353

library(leaps)
library(glmnet)

# ====== (a) 生成预测变量X和噪声向量epsilon ======
set.seed(1)
X <- rnorm(100)
eps <- rnorm(100)

# ====== (b) 生成响应向量 Y = b0 + b1*X + b2*X^2 + b3*X^3 + eps ======
b0 <- 3; b1 <- 2; b2 <- -3; b3 <- 0.5
Y <- b0 + b1*X + b2*X^2 + b3*X^3 + eps
df <- data.frame(Y = Y, X = X)

# ====== (c) 最优子集选择（X, X^2, ..., X^10） ======
regfit.full <- regsubsets(Y ~ poly(X, 10, raw = TRUE), data = df, nvmax = 10)
reg.summary <- summary(regfit.full)

# 用Cp、BIC、调整R^2选择最优模型大小
cat("Cp最小的模型大小:", which.min(reg.summary$cp), "\n")
cat("BIC最小的模型大小:", which.min(reg.summary$bic), "\n")
cat("调整R^2最大的模型大小:", which.max(reg.summary$adjr2), "\n")

png("../图片输出/q8_子集选择准则.png", width = 900, height = 300)
par(mfrow = c(1, 3))
plot(reg.summary$cp, xlab = "变量个数", ylab = "Cp", type = "b", pch = 19)
points(which.min(reg.summary$cp), min(reg.summary$cp), col = "red", cex = 2, pch = 20)
plot(reg.summary$bic, xlab = "变量个数", ylab = "BIC", type = "b", pch = 19)
points(which.min(reg.summary$bic), min(reg.summary$bic), col = "red", cex = 2, pch = 20)
plot(reg.summary$adjr2, xlab = "变量个数", ylab = "调整R^2", type = "b", pch = 19)
points(which.max(reg.summary$adjr2), max(reg.summary$adjr2), col = "red", cex = 2, pch = 20)
dev.off()

# 最优模型（以BIC选出的为例）的系数
cat("\n--- BIC选出模型的系数 ---\n")
print(coef(regfit.full, which.min(reg.summary$bic)))

# ====== (d) 向前逐步选择 与 向后逐步选择 ======
regfit.fwd <- regsubsets(Y ~ poly(X, 10, raw = TRUE), data = df, nvmax = 10, method = "forward")
regfit.bwd <- regsubsets(Y ~ poly(X, 10, raw = TRUE), data = df, nvmax = 10, method = "backward")
fwd.sum <- summary(regfit.fwd)
bwd.sum <- summary(regfit.bwd)
cat("\n向前逐步: Cp最优大小 =", which.min(fwd.sum$cp),
    " BIC最优大小 =", which.min(fwd.sum$bic), "\n")
cat("向后逐步: Cp最优大小 =", which.min(bwd.sum$cp),
    " BIC最优大小 =", which.min(bwd.sum$bic), "\n")
cat("\n--- 向前逐步BIC最优模型系数 ---\n")
print(coef(regfit.fwd, which.min(fwd.sum$bic)))
cat("\n--- 向后逐步BIC最优模型系数 ---\n")
print(coef(regfit.bwd, which.min(bwd.sum$bic)))

# ====== (e) lasso拟合（含X, ..., X^10），交叉验证选lambda ======
xmat <- poly(X, 10, raw = TRUE)
set.seed(1)
cv.lasso <- cv.glmnet(xmat, Y, alpha = 1)
bestlam <- cv.lasso$lambda.min
cat("\nlasso交叉验证最优lambda =", bestlam, "\n")

png("../图片输出/q8_lasso交叉验证.png", width = 600, height = 450)
plot(cv.lasso)
dev.off()

lasso.fit <- glmnet(xmat, Y, alpha = 1, lambda = bestlam)
cat("\n--- lasso系数估计 ---\n")
print(coef(lasso.fit))

# ====== (f) 改用 Y = b0 + b7*X^7 + eps ======
b7 <- 7
Y2 <- b0 + b7 * X^7 + eps
df2 <- data.frame(Y = Y2, X = X)

# 最优子集选择
regfit.f <- regsubsets(Y ~ poly(X, 10, raw = TRUE), data = df2, nvmax = 10)
f.sum <- summary(regfit.f)
cat("\n(f) 最优子集: BIC选出大小 =", which.min(f.sum$bic), "\n")
print(coef(regfit.f, which.min(f.sum$bic)))

# lasso
set.seed(1)
cv.lasso2 <- cv.glmnet(xmat, Y2, alpha = 1)
lasso.fit2 <- glmnet(xmat, Y2, alpha = 1, lambda = cv.lasso2$lambda.min)
cat("\n(f) lasso最优lambda =", cv.lasso2$lambda.min, "\n")
cat("--- (f) lasso系数估计 ---\n")
print(coef(lasso.fit2))

cat("\n第8题图片输出完成\n")
