# 第6题：近线性可分数据 - cost对训练/交叉验证/测试误分数的影响
# 高级统计方法 第6次作业
# 张鸿昊 20242081353

library(e1071)

# ====== (a) 生成p=2、两类几乎线性可分的数据 ======
set.seed(1)
n <- 200
x <- matrix(rnorm(n * 2), ncol = 2)
y <- c(rep(-1, n / 2), rep(1, n / 2))
# 让两类几乎线性可分：正类整体平移，仅留很小重叠
x[y == 1, ] <- x[y == 1, ] + 2.2
dat <- data.frame(x = x, y = as.factor(y))

# ====== (b) 不同cost下的交叉验证误差 与 训练误分数 ======
costs <- c(0.01, 0.1, 1, 5, 10, 100, 1000)

# 用tune()做10折交叉验证
set.seed(1)
tune.out <- tune(svm, y ~ ., data = dat, kernel = "linear",
                 ranges = list(cost = costs))
cv.err <- tune.out$performances[, c("cost", "error")]

# 各cost对应的训练误分数（误分观测个数）
train.miss <- sapply(costs, function(cc) {
  fit <- svm(y ~ ., data = dat, kernel = "linear", cost = cc)
  sum(predict(fit, dat) != dat$y)
})

cat("=== (b) 各cost的交叉验证误差与训练误分数 ===\n")
res.b <- data.frame(cost = costs,
                    CV误差率 = round(cv.err$error, 4),
                    训练误分数 = train.miss)
print(res.b)

# ====== (c) 生成测试集，计算各cost的测试误分数 ======
set.seed(2)
xt <- matrix(rnorm(n * 2), ncol = 2)
yt <- c(rep(-1, n / 2), rep(1, n / 2))
xt[yt == 1, ] <- xt[yt == 1, ] + 2.2
dat.test <- data.frame(x = xt, y = as.factor(yt))

test.miss <- sapply(costs, function(cc) {
  fit <- svm(y ~ ., data = dat, kernel = "linear", cost = cc)
  sum(predict(fit, dat.test) != dat.test$y)
})

cat("\n=== (c) 各cost的测试误分数 ===\n")
res.c <- data.frame(cost = costs, 测试误分数 = test.miss)
print(res.c)

cat("\n训练误分数最小的cost =", costs[which.min(train.miss)], "\n")
cat("交叉验证误差最小的cost =", costs[which.min(cv.err$error)], "\n")
cat("测试误分数最小的cost =", costs[which.min(test.miss)], "\n")

# ====== 作图 ======
png("../图片输出/q6_cost误差对比.png", width = 1000, height = 400)
par(mfrow = c(1, 2))
plot(log10(costs), train.miss, type = "b", pch = 19, col = "blue",
     xlab = "log10(cost)", ylab = "训练误分数", main = "训练误分数 vs cost")
plot(log10(costs), test.miss, type = "b", pch = 19, col = "red",
     xlab = "log10(cost)", ylab = "测试误分数", main = "测试误分数 vs cost")
points(log10(costs)[which.min(test.miss)], min(test.miss),
       col = "darkgreen", cex = 2, pch = 20)
dev.off()

cat("\n(d) 结论：cost越大，间隔越窄，训练误分数趋于减少（更拟合训练集）；\n")
cat("    但测试误分数往往在中等cost处最小。本例验证了——训练误差最小的\n")
cat("    大cost未必在测试集上最优，存在过拟合现象。\n")
cat("\n第6题图片输出完成\n")
