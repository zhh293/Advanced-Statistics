# 第10题：Carseats数据集 - 多元回归与交互项
# 高级统计方法 第3次作业
# 张鸿昊 20242081353

library(ISLR2)
data(Carseats)

# ====== (a) 拟合多元回归模型 ======
lm.fit <- lm(Sales ~ Price + Urban + US, data=Carseats)
summary(lm.fit)

# ====== (b) 解释各系数含义 ======
# Price: 价格与销量的关系
# Urban: 城区vs非城区
# US: 美国vs非美国

# ====== (c) 写出模型方程 ======
cat("模型方程:\n")
cat("Sales = ", coef(lm.fit)[1], " + (", coef(lm.fit)[2], ")*Price + (",
    coef(lm.fit)[3], ")*UrbanYes + (", coef(lm.fit)[4], ")*USYes\n")

# ====== (d) 哪些预测变量可以拒绝零假设 ======
# 查看p值
summary(lm.fit)$coefficients[, 4]

# ====== (e) 拟合较小模型（去掉不显著变量） ======
lm.fit2 <- lm(Sales ~ Price + US, data=Carseats)
summary(lm.fit2)

# ====== (f) 比较两个模型的拟合程度 ======
cat("\n模型(a) R² =", summary(lm.fit)$r.squared, 
    ", Adj R² =", summary(lm.fit)$adj.r.squared, "\n")
cat("模型(e) R² =", summary(lm.fit2)$r.squared, 
    ", Adj R² =", summary(lm.fit2)$adj.r.squared, "\n")
anova(lm.fit2, lm.fit)

# ====== (g) 95%置信区间 ======
confint(lm.fit2)

# ====== (h) 异常值和高杠杆点 ======
png("../图片输出/q10_诊断图.png", width=700, height=600)
par(mfrow=c(2,2))
plot(lm.fit2)
dev.off()

# 高杠杆点
hat_values <- hatvalues(lm.fit2)
p <- 2  # 预测变量个数
n <- nrow(Carseats)
high_leverage <- which(hat_values > 2*(p+1)/n)
cat("\n高杠杆点数量:", length(high_leverage), "\n")

# 异常值（学生化残差绝对值>3）
stu_res <- rstudent(lm.fit2)
outliers <- which(abs(stu_res) > 3)
cat("异常值数量:", length(outliers), "\n")

png("../图片输出/q10_杠杆值.png", width=600, height=450)
plot(hat_values, stu_res, xlab="Leverage", ylab="Studentized Residuals",
     main="Leverage vs Studentized Residuals")
abline(h=c(-3,3), col="red", lty=2)
abline(v=2*(p+1)/n, col="blue", lty=2)
dev.off()

cat("第10题图片输出完成\n")
