# 第9题：Auto数据集 - 多元线性回归
# 高级统计方法 第3次作业
# 张鸿昊 20242081353

library(ISLR2)
data(Auto)

# ====== (a) 散点图矩阵 ======
png("../图片输出/q9_散点图矩阵.png", width=800, height=800)
pairs(Auto[, 1:8], col="darkgray", pch=16, cex=0.5)
dev.off()

# ====== (b) 相关系数矩阵 ======
cor_matrix <- cor(Auto[, 1:8])
print(round(cor_matrix, 3))

# ====== (c) 多元线性回归 ======
lm.fit <- lm(mpg ~ . - name, data=Auto)
summary(lm.fit)

# i. 预测变量与响应变量之间是否存在关系？
# F统计量和p值

# ii. 哪些预测变量在统计上显著？
# 查看各系数的p值

# iii. year系数的含义
# 年份系数为正，表明每年mpg平均提升

# ====== (d) 诊断图 ======
png("../图片输出/q9_诊断图.png", width=700, height=600)
par(mfrow=c(2,2))
plot(lm.fit)
dev.off()

# ====== (e) 交互项 ======
lm.fit2 <- lm(mpg ~ cylinders*displacement + displacement*weight + 
               year*origin, data=Auto)
summary(lm.fit2)

# 尝试更多交互项
lm.fit3 <- lm(mpg ~ . - name + displacement:weight + year:origin, data=Auto)
summary(lm.fit3)

png("../图片输出/q9_交互项诊断.png", width=700, height=600)
par(mfrow=c(2,2))
plot(lm.fit3)
dev.off()

# ====== (f) 非线性变换 ======
lm.fit4 <- lm(mpg ~ poly(horsepower, 2) + poly(weight, 2) + year + origin, data=Auto)
summary(lm.fit4)

lm.fit5 <- lm(mpg ~ log(horsepower) + log(weight) + sqrt(displacement) + 
               year + origin, data=Auto)
summary(lm.fit5)

png("../图片输出/q9_非线性变换.png", width=700, height=600)
par(mfrow=c(2,2))
plot(lm.fit5)
dev.off()

cat("第9题图片输出完成\n")
