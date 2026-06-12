# 第5题：p=2,n=2特殊情形下岭回归与lasso系数估计的唯一性（概念+数值验证）
# 高级统计方法 第5次作业
# 张鸿昊 20242081353
#
# 设定：n=2, p=2, 无截距, x11=x12, x21=x22,
#       y1+y2=0, x11+x21=0, x12+x22=0
#
# 数学结论：
#   岭回归：目标函数关于(b1,b2)严格凸，最优解唯一且满足 b1_hat = b2_hat。
#           （因为两个预测变量完全相同，对称性 + L2惩罚的严格凸性）
#   lasso：约束/惩罚是L1，等高线在对角线上是一条线段，
#          满足 b1_hat + b2_hat = 常数 的所有点都是最优解 -> 解不唯一。
#
# 下面用数值演示岭回归解的唯一性与lasso解的不唯一性：

library(glmnet)

# 构造满足条件的数据
x1 <- c(1, -1)          # x11=1, x21=-1  -> x11+x21=0
x  <- cbind(x1, x1)     # x12=x11, x22=x21（两列相同）
y  <- c(2, -2)          # y1+y2=0

# 岭回归（alpha=0），系数应满足 b1 = b2
ridge <- glmnet(x, y, alpha = 0, lambda = 1, intercept = FALSE,
                standardize = FALSE)
cat("岭回归系数（应近似相等 b1≈b2）:\n")
print(coef(ridge))

# lasso（alpha=1）
lasso <- glmnet(x, y, alpha = 1, lambda = 0.5, intercept = FALSE,
                standardize = FALSE)
cat("\nlasso系数（解不唯一，b1+b2为定值的任意组合都可行）:\n")
print(coef(lasso))

cat("\n结论：岭回归对完全共线的两列给出相等的系数（唯一）；\n")
cat("      lasso只约束 |b1|+|b2|，对角线上的整条线段都是最优解（不唯一）。\n")
