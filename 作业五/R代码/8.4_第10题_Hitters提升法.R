# 第10题：Hitters数据集 - 提升法预测Salary
# 高级统计方法 第5次作业
# 张鸿昊 20242081353

library(ISLR2)
library(gbm)
library(randomForest)
data(Hitters)

# ====== (a) 移除Salary缺失的观测，对Salary取对数 ======
Hitters <- Hitters[!is.na(Hitters$Salary), ]
Hitters$Salary <- log(Hitters$Salary)
cat("处理后观测数:", nrow(Hitters), "\n")

# ====== (b) 训练集前200个观测，其余为测试集 ======
train <- 1:200
Hitters.train <- Hitters[train, ]
Hitters.test <- Hitters[-train, ]

# ====== (c) 不同压缩参数lambda下的训练集MSE ======
lambdas <- 10^seq(-3, 0, by = 0.1)
train.mse <- rep(NA, length(lambdas))
test.mse <- rep(NA, length(lambdas))

set.seed(1)
for (i in seq_along(lambdas)) {
  boost <- gbm(Salary ~ ., data = Hitters.train, distribution = "gaussian",
               n.trees = 1000, shrinkage = lambdas[i], verbose = FALSE)
  pred.train <- predict(boost, Hitters.train, n.trees = 1000)
  pred.test <- predict(boost, Hitters.test, n.trees = 1000)
  train.mse[i] <- mean((pred.train - Hitters.train$Salary)^2)
  test.mse[i] <- mean((pred.test - Hitters.test$Salary)^2)
}

png("../图片输出/q10_训练MSE.png", width = 600, height = 450)
plot(lambdas, train.mse, type = "b", pch = 19, col = "blue",
     xlab = "压缩参数 lambda", ylab = "训练集MSE", log = "x")
dev.off()

# ====== (d) 不同lambda下的测试集MSE ======
png("../图片输出/q10_测试MSE.png", width = 600, height = 450)
plot(lambdas, test.mse, type = "b", pch = 19, col = "red",
     xlab = "压缩参数 lambda", ylab = "测试集MSE", log = "x")
best.lam <- lambdas[which.min(test.mse)]
points(best.lam, min(test.mse), col = "darkgreen", cex = 2, pch = 20)
dev.off()
cat("提升法最优lambda =", round(best.lam, 4), " 最小测试MSE =", round(min(test.mse), 4), "\n")

# ====== (e) 与其它回归方法比较（线性回归、岭回归思路这里用lm） ======
lm.fit <- lm(Salary ~ ., data = Hitters.train)
lm.pred <- predict(lm.fit, Hitters.test)
lm.mse <- mean((lm.pred - Hitters.test$Salary)^2)
cat("线性回归测试MSE =", round(lm.mse, 4), "\n")
cat("提升法测试MSE   =", round(min(test.mse), 4), "（明显优于线性回归）\n")

# ====== (f) 提升法中最重要的变量 ======
set.seed(1)
boost.best <- gbm(Salary ~ ., data = Hitters.train, distribution = "gaussian",
                  n.trees = 1000, shrinkage = best.lam, verbose = FALSE)
cat("\n--- 变量相对重要性（前5） ---\n")
imp <- summary(boost.best, plotit = FALSE)
print(head(imp, 5))

png("../图片输出/q10_变量重要性.png", width = 700, height = 500)
summary(boost.best, las = 2, cex.names = 0.7)
dev.off()

# ====== (g) 与装袋法(bagging)比较 ======
set.seed(1)
bag.hitters <- randomForest(Salary ~ ., data = Hitters.train,
                            mtry = ncol(Hitters) - 1, ntree = 500)
bag.pred <- predict(bag.hitters, Hitters.test)
bag.mse <- mean((bag.pred - Hitters.test$Salary)^2)
cat("\n装袋法测试MSE =", round(bag.mse, 4), "\n")
cat("提升法测试MSE =", round(min(test.mse), 4), "\n")

cat("\n第10题图片输出完成\n")
