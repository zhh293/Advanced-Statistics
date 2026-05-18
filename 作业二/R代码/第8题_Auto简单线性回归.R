# 第8题：Auto数据集 - 简单线性回归
# 高级统计方法 第2次作业
# 张鸿昊 20242081353

library(ISLR2)
data(Auto)

# ====== (a) 拟合简单线性回归模型 ======
lm.fit <- lm(mpg ~ horsepower, data=Auto)
summary(lm.fit)

# 预测 horsepower=98 时的mpg
predict(lm.fit, data.frame(horsepower=98), interval="confidence")
predict(lm.fit, data.frame(horsepower=98), interval="prediction")

# ====== (b) 散点图 + 回归线 ======
png("../图片输出/q8_散点图与回归线.png", width=600, height=450)
plot(Auto$horsepower, Auto$mpg, 
     xlab="Horsepower", ylab="MPG",
     main="MPG vs Horsepower",
     col="darkgray", pch=16, cex=0.8)
abline(lm.fit, col="red", lwd=2)
legend("topright", legend="Least Squares Line", 
       col="red", lwd=2)
dev.off()

# ====== (c) 诊断图 ======
png("../图片输出/q8_诊断图.png", width=700, height=600)
par(mfrow=c(2,2))
plot(lm.fit)
dev.off()

cat("第8题图片输出完成\n")
