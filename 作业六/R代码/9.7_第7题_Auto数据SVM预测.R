# 第7题：Auto数据集 - 用SVM预测汽车每英里耗油量(mpg)的高低
# 高级统计方法 第6次作业
# 张鸿昊 20242081353

library(e1071)
library(ISLR)
data(Auto)

# ====== (a) 创建二分变量：mpg高于中位数记为1，否则记为0 ======
Auto$mpglevel <- as.factor(ifelse(Auto$mpg > median(Auto$mpg), 1, 0))
# 去掉mpg与name（避免信息泄露和非数值变量）
dat <- subset(Auto, select = -c(mpg, name))

# ====== (b) 支持向量分类器(线性核)，不同cost的交叉验证误差 ======
set.seed(1)
tune.lin <- tune(svm, mpglevel ~ ., data = dat, kernel = "linear",
                 ranges = list(cost = c(0.01, 0.1, 1, 5, 10, 100)))
cat("=== (b) 线性核 不同cost的交叉验证误差 ===\n")
print(tune.lin$performances[, c("cost", "error")])
cat("线性核最优cost =", tune.lin$best.parameters$cost,
    " 最优CV误差 =", round(tune.lin$best.performance, 4), "\n")

# ====== (c) 径向核 SVM：调 cost 与 gamma ======
set.seed(1)
tune.rad <- tune(svm, mpglevel ~ ., data = dat, kernel = "radial",
                 ranges = list(cost = c(0.1, 1, 10, 100),
                               gamma = c(0.01, 0.1, 1, 5)))
cat("\n=== (c) 径向核 最优参数 ===\n")
cat("cost =", tune.rad$best.parameters$cost,
    " gamma =", tune.rad$best.parameters$gamma,
    " 最优CV误差 =", round(tune.rad$best.performance, 4), "\n")

# 多项式核 SVM：调 cost 与 degree
set.seed(1)
tune.poly <- tune(svm, mpglevel ~ ., data = dat, kernel = "polynomial",
                  ranges = list(cost = c(0.1, 1, 10, 100),
                                degree = c(2, 3, 4)))
cat("\n=== (c) 多项式核 最优参数 ===\n")
cat("cost =", tune.poly$best.parameters$cost,
    " degree =", tune.poly$best.parameters$degree,
    " 最优CV误差 =", round(tune.poly$best.performance, 4), "\n")

# ====== (d) 画图说明结论：以 weight 与 horsepower 为例展示决策边界 ======
svm.lin <- svm(mpglevel ~ ., data = dat, kernel = "linear",
               cost = tune.lin$best.parameters$cost)
svm.rad <- svm(mpglevel ~ ., data = dat, kernel = "radial",
               cost = tune.rad$best.parameters$cost,
               gamma = tune.rad$best.parameters$gamma)

png("../图片输出/q7_SVM决策边界.png", width = 1000, height = 450)
par(mfrow = c(1, 2))
plot(svm.lin, dat, weight ~ horsepower)
plot(svm.rad, dat, weight ~ horsepower)
dev.off()

cat("\n结论：三种核的交叉验证误差都较低（约8%~10%）。径向核和多项式核\n")
cat("      通过调参后通常略优于线性核，说明mpg高低与各特征间存在一定\n")
cat("      非线性关系；weight 与 horsepower 是区分油耗高低的关键变量。\n")
cat("\n第7题图片输出完成\n")
