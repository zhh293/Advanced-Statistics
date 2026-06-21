# 第4题：非线性可分模拟数据 - 支持向量分类器 vs 多项式核 vs 径向核SVM
# 高级统计方法 第6次作业
# 张鸿昊 20242081353

library(e1071)

# ====== 生成100个观测、2个特征、非线性可分的两类别数据 ======
set.seed(1)
x <- matrix(rnorm(100 * 2), ncol = 2)
# 让一类落在环形/曲线区域，制造非线性可分隔
y <- ifelse(x[, 1]^2 + x[, 2]^2 > 1.5, 1, -1)
x[y == 1, ] <- x[y == 1, ] + 1.0   # 适当偏移，保持可见但非线性的分隔
dat <- data.frame(x = x, y = as.factor(y))

# 划分训练集与测试集
train <- sample(100, 50)
dat.train <- dat[train, ]
dat.test <- dat[-train, ]

# 误差计算辅助函数
err.rate <- function(fit, data) {
  pred <- predict(fit, data)
  mean(pred != data$y)
}

# ====== 1) 支持向量分类器（线性核） ======
svm.lin <- svm(y ~ ., data = dat.train, kernel = "linear", cost = 1)
cat("线性核(支持向量分类器): 训练误差 =", round(err.rate(svm.lin, dat.train), 4),
    " 测试误差 =", round(err.rate(svm.lin, dat.test), 4), "\n")

# ====== 2) 多项式核SVM（degree>1） ======
svm.poly <- svm(y ~ ., data = dat.train, kernel = "polynomial", degree = 2, cost = 1)
cat("多项式核SVM(degree=2): 训练误差 =", round(err.rate(svm.poly, dat.train), 4),
    " 测试误差 =", round(err.rate(svm.poly, dat.test), 4), "\n")

# ====== 3) 径向核SVM ======
svm.rad <- svm(y ~ ., data = dat.train, kernel = "radial", gamma = 1, cost = 1)
cat("径向核SVM: 训练误差 =", round(err.rate(svm.rad, dat.train), 4),
    " 测试误差 =", round(err.rate(svm.rad, dat.test), 4), "\n")

# ====== 作图：三种方法的决策边界（plot.svm内部使用filled.contour，
#         不能用par(mfrow)拼接，故分别单独输出三张图） ======
png("../图片输出/q4_线性核.png", width = 500, height = 450)
plot(svm.lin, dat.train)
dev.off()
png("../图片输出/q4_多项式核.png", width = 500, height = 450)
plot(svm.poly, dat.train)
dev.off()
png("../图片输出/q4_径向核.png", width = 500, height = 450)
plot(svm.rad, dat.train)
dev.off()

cat("\n结论：在非线性可分数据上，多项式核与径向核SVM的训练误差远低于\n")
cat("      线性的支持向量分类器；测试集上径向核SVM通常表现最好，\n")
cat("      因为它能灵活地刻画弯曲的决策边界。\n")
cat("\n第4题图片输出完成\n")
