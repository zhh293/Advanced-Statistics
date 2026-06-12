# 第10题：高维模拟数据 - 最优子集选择的训练/测试误差
# 高级统计方法 第5次作业
# 张鸿昊 20242081353

library(leaps)

# ====== (a) 生成 p=20 个特征, n=1000 个观测, Y = X*beta + eps ======
set.seed(1)
p <- 20
n <- 1000
X <- matrix(rnorm(n * p), n, p)
beta <- rnorm(p)
# 让beta的部分元素为0（题目要求）
beta[c(2, 4, 6, 8, 10, 12, 14)] <- 0
eps <- rnorm(n)
Y <- X %*% beta + eps
df <- data.frame(Y = Y, X)

# ====== (b) 划分训练集(100)与测试集(900) ======
train <- sample(1:n, 100)
test <- (-train)
df.train <- df[train, ]
df.test <- df[test, ]

# ====== (c) 最优子集选择, 训练集MSE ======
regfit <- regsubsets(Y ~ ., data = df.train, nvmax = p)

# 构造预测函数（regsubsets无predict方法）
predict.regsubsets <- function(object, newdata, id) {
  form <- as.formula(object$call[[2]])
  mat <- model.matrix(form, newdata)
  coefi <- coef(object, id = id)
  mat[, names(coefi)] %*% coefi
}

train.err <- rep(NA, p)
for (i in 1:p) {
  pred <- predict.regsubsets(regfit, df.train, i)
  train.err[i] <- mean((df.train$Y - pred)^2)
}

# ====== (d) 测试集MSE ======
test.err <- rep(NA, p)
for (i in 1:p) {
  pred <- predict.regsubsets(regfit, df.test, i)
  test.err[i] <- mean((df.test$Y - pred)^2)
}

png("../图片输出/q10_训练测试MSE.png", width = 900, height = 400)
par(mfrow = c(1, 2))
plot(1:p, train.err, type = "b", pch = 19, xlab = "模型大小（变量个数）", ylab = "训练集MSE")
plot(1:p, test.err, type = "b", pch = 19, col = "blue",
     xlab = "模型大小（变量个数）", ylab = "测试集MSE")
points(which.min(test.err), min(test.err), col = "red", cex = 2, pch = 20)
dev.off()

# ====== (e) 测试集MSE最小对应的模型大小 ======
cat("训练集MSE最小的模型大小:", which.min(train.err), "（应为p=20，含全部变量）\n")
cat("测试集MSE最小的模型大小:", which.min(test.err), "\n")
cat("测试集最小MSE =", round(min(test.err), 4), "\n")

# ====== (f) 最小测试MSE模型与真实模型对比 ======
best.id <- which.min(test.err)
cat("\n--- 测试集MSE最小模型的系数估计 ---\n")
print(coef(regfit, best.id))
cat("\n--- 真实系数beta（非零项） ---\n")
true.coef <- beta
names(true.coef) <- paste0("X", 1:p)
print(true.coef[true.coef != 0])

# ====== (g) 系数估计误差随模型大小的变化 ======
true.full <- c(0, beta)               # 含截距0
names(true.full) <- c("(Intercept)", paste0("X", 1:p))
coef.err <- rep(NA, p)
for (i in 1:p) {
  ci <- coef(regfit, id = i)
  # 对齐到完整系数向量
  diff2 <- 0
  allnames <- names(true.full)
  for (nm in allnames) {
    est <- ifelse(nm %in% names(ci), ci[nm], 0)
    diff2 <- diff2 + (est - true.full[nm])^2
  }
  coef.err[i] <- sqrt(diff2)
}

png("../图片输出/q10_系数估计误差.png", width = 600, height = 450)
plot(1:p, coef.err, type = "b", pch = 19, xlab = "模型大小（变量个数）",
     ylab = "系数估计误差（L2范数）")
points(which.min(coef.err), min(coef.err), col = "red", cex = 2, pch = 20)
dev.off()
cat("\n系数估计误差最小的模型大小:", which.min(coef.err), "\n")

cat("\n第10题图片输出完成\n")
