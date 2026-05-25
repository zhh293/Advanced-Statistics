# 第4章第10题：Weekly股市数据分析
# 高级统计方法 第3次作业
# 张鸿昊 20242081353

library(ISLR2)
data(Weekly)

# ====== (a) 数值摘要和图形 ======
summary(Weekly)
cor(Weekly[, -9])  # 去掉Direction列

png("../图片输出/q4_10_散点图矩阵.png", width=800, height=800)
pairs(Weekly[, -9], col="darkgray", pch=16, cex=0.4)
dev.off()

png("../图片输出/q4_10_volume趋势.png", width=600, height=450)
plot(Weekly$Volume, type="l", xlab="Week", ylab="Volume",
     main="Weekly Trading Volume Over Time", col="blue")
dev.off()

# ====== (b) 逻辑斯蒂回归（全部Lag变量+Volume） ======
glm.fit <- glm(Direction ~ Lag1 + Lag2 + Lag3 + Lag4 + Lag5 + Volume,
               data=Weekly, family=binomial)
summary(glm.fit)

# ====== (c) 混淆矩阵 ======
glm.probs <- predict(glm.fit, type="response")
glm.pred <- rep("Down", nrow(Weekly))
glm.pred[glm.probs > 0.5] <- "Up"
table(glm.pred, Weekly$Direction)
cat("整体正确率:", mean(glm.pred == Weekly$Direction), "\n")

# ====== (d) 逻辑斯蒂回归（训练/测试划分） ======
train <- (Weekly$Year <= 2008)
Weekly.test <- Weekly[!train, ]
Direction.test <- Weekly$Direction[!train]

glm.fit2 <- glm(Direction ~ Lag2, data=Weekly, family=binomial, subset=train)
glm.probs2 <- predict(glm.fit2, Weekly.test, type="response")
glm.pred2 <- rep("Down", nrow(Weekly.test))
glm.pred2[glm.probs2 > 0.5] <- "Up"
table(glm.pred2, Direction.test)
cat("Logistic测试正确率:", mean(glm.pred2 == Direction.test), "\n")

# ====== (e) LDA ======
library(MASS)
lda.fit <- lda(Direction ~ Lag2, data=Weekly, subset=train)
lda.pred <- predict(lda.fit, Weekly.test)
table(lda.pred$class, Direction.test)
cat("LDA测试正确率:", mean(lda.pred$class == Direction.test), "\n")

# ====== (f) QDA ======
qda.fit <- qda(Direction ~ Lag2, data=Weekly, subset=train)
qda.pred <- predict(qda.fit, Weekly.test)
table(qda.pred$class, Direction.test)
cat("QDA测试正确率:", mean(qda.pred$class == Direction.test), "\n")

# ====== (g) KNN (K=1) ======
library(class)
train.X <- as.matrix(Weekly$Lag2[train])
test.X <- as.matrix(Weekly$Lag2[!train])
train.Direction <- Weekly$Direction[train]

set.seed(1)
knn.pred <- knn(train.X, test.X, train.Direction, k=1)
table(knn.pred, Direction.test)
cat("KNN(K=1)测试正确率:", mean(knn.pred == Direction.test), "\n")

# ====== (h) 哪个方法表现最好 ======
cat("\n=== 方法对比 ===\n")
cat("Logistic:", mean(glm.pred2 == Direction.test), "\n")
cat("LDA:", mean(lda.pred$class == Direction.test), "\n")
cat("QDA:", mean(qda.pred$class == Direction.test), "\n")
cat("KNN(K=1):", mean(knn.pred == Direction.test), "\n")

# ====== (i) 尝试不同组合改进 ======
# KNN with different K values
set.seed(1)
knn.pred3 <- knn(train.X, test.X, train.Direction, k=3)
cat("KNN(K=3)测试正确率:", mean(knn.pred3 == Direction.test), "\n")

set.seed(1)
knn.pred5 <- knn(train.X, test.X, train.Direction, k=5)
cat("KNN(K=5)测试正确率:", mean(knn.pred5 == Direction.test), "\n")

set.seed(1)
knn.pred10 <- knn(train.X, test.X, train.Direction, k=10)
cat("KNN(K=10)测试正确率:", mean(knn.pred10 == Direction.test), "\n")

# Logistic with interaction
glm.fit3 <- glm(Direction ~ Lag1*Lag2, data=Weekly, family=binomial, subset=train)
glm.probs3 <- predict(glm.fit3, Weekly.test, type="response")
glm.pred3 <- rep("Down", nrow(Weekly.test))
glm.pred3[glm.probs3 > 0.5] <- "Up"
cat("Logistic(Lag1*Lag2)测试正确率:", mean(glm.pred3 == Direction.test), "\n")

cat("第4章第10题完成\n")
