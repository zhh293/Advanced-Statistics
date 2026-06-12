# 第9题：OJ数据集 - 决策树分类
# 高级统计方法 第5次作业
# 张鸿昊 20242081353

library(ISLR2)
library(tree)
data(OJ)

# ====== (a) 训练集800个观测，其余为测试集 ======
set.seed(1)
train <- sample(1:nrow(OJ), 800)
OJ.train <- OJ[train, ]
OJ.test <- OJ[-train, ]

# ====== (b) 拟合分类树，以Purchase为响应变量 ======
tree.oj <- tree(Purchase ~ ., data = OJ.train)
print(summary(tree.oj))
# summary给出：训练误差率、终端节点数、用到的变量

# ====== (c) 详细输出树结构 ======
cat("\n--- 树结构 ---\n")
print(tree.oj)

# ====== (d) 绘制树 ======
png("../图片输出/q9_决策树.png", width = 800, height = 600)
plot(tree.oj)
text(tree.oj, pretty = 0, cex = 0.8)
dev.off()

# ====== (e) 测试集预测与混淆矩阵 ======
tree.pred <- predict(tree.oj, OJ.test, type = "class")
cm <- table(预测 = tree.pred, 真实 = OJ.test$Purchase)
cat("\n--- 测试集混淆矩阵 ---\n")
print(cm)
test.err <- 1 - sum(diag(cm)) / sum(cm)
cat("测试集错误率 =", round(test.err, 4), "\n")

# ====== (f)(g)(h) 交叉验证选择最优树规模 ======
set.seed(1)
cv.oj <- cv.tree(tree.oj, FUN = prune.misclass)
cat("\n--- 交叉验证结果 ---\n")
print(data.frame(size = cv.oj$size, dev = cv.oj$dev))

png("../图片输出/q9_交叉验证.png", width = 600, height = 450)
plot(cv.oj$size, cv.oj$dev, type = "b", pch = 19,
     xlab = "树的终端节点数", ylab = "交叉验证错误数")
best.size <- cv.oj$size[which.min(cv.oj$dev)]
points(best.size, min(cv.oj$dev), col = "red", cex = 2, pch = 20)
dev.off()
cat("交叉验证错误率最低对应的终端节点数 =", best.size, "\n")

# ====== (i)(j)(k) 剪枝树 vs 未剪枝树 ======
prune.oj <- prune.misclass(tree.oj, best = max(2, best.size))
png("../图片输出/q9_剪枝树.png", width = 800, height = 600)
plot(prune.oj)
text(prune.oj, pretty = 0, cex = 0.8)
dev.off()

# 训练误差比较
cat("\n未剪枝树训练误差率 =", round(summary(tree.oj)$misclass[1] / summary(tree.oj)$misclass[2], 4), "\n")
cat("剪枝树训练误差率   =", round(summary(prune.oj)$misclass[1] / summary(prune.oj)$misclass[2], 4), "\n")

# 测试误差比较
prune.pred <- predict(prune.oj, OJ.test, type = "class")
cm2 <- table(预测 = prune.pred, 真实 = OJ.test$Purchase)
prune.err <- 1 - sum(diag(cm2)) / sum(cm2)
cat("未剪枝树测试误差率 =", round(test.err, 4), "\n")
cat("剪枝树测试误差率   =", round(prune.err, 4), "\n")

cat("\n第9题图片输出完成\n")
