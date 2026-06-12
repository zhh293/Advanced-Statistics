# 第6题：p=1情形下岭回归(6.12式)与lasso(6.13式)解析解验证（概念+数值验证）
# 高级统计方法 第5次作业
# 张鸿昊 20242081353
#
# p=1, n=1 简化情形：
#   岭回归 (6.12): minimize (y - beta)^2 + lambda*beta^2
#                  解析解 (6.14): beta_hat = y / (1 + lambda)
#   lasso  (6.13): minimize (y - beta)^2 + lambda*|beta|
#                  解析解 (6.15) 软阈值:
#                     beta_hat = y - lambda/2 ,  若 y >  lambda/2
#                     beta_hat = y + lambda/2 ,  若 y < -lambda/2
#                     beta_hat = 0            ,  若 |y| <= lambda/2

# ====== 数值验证岭回归解析解 (6.14) ======
y <- 4
lambda <- 2

ridge_obj <- function(b) (y - b)^2 + lambda * b^2
opt_ridge <- optimize(ridge_obj, c(-10, 10))
analytic_ridge <- y / (1 + lambda)
cat("岭回归: 数值解 =", round(opt_ridge$minimum, 4),
    " 解析解(6.14) y/(1+lambda) =", round(analytic_ridge, 4), "\n")

# ====== 数值验证lasso解析解 (6.15) ======
lasso_obj <- function(b) (y - b)^2 + lambda * abs(b)
opt_lasso <- optimize(lasso_obj, c(-10, 10))
analytic_lasso <- if (y > lambda/2) y - lambda/2 else if (y < -lambda/2) y + lambda/2 else 0
cat("lasso:  数值解 =", round(opt_lasso$minimum, 4),
    " 解析解(6.15) 软阈值 =", round(analytic_lasso, 4), "\n")

# 画出两种惩罚下的目标函数曲线
png("../图片输出/q6_目标函数曲线.png", width = 800, height = 400)
par(mfrow = c(1, 2))
bs <- seq(-2, 6, 0.05)
plot(bs, sapply(bs, ridge_obj), type = "l", lwd = 2,
     xlab = "beta", ylab = "目标函数", main = "岭回归 p=1")
abline(v = analytic_ridge, col = "red", lty = 2)
plot(bs, sapply(bs, lasso_obj), type = "l", lwd = 2,
     xlab = "beta", ylab = "目标函数", main = "lasso p=1")
abline(v = analytic_lasso, col = "red", lty = 2)
dev.off()

cat("\n结论：数值解与解析解(6.14)(6.15)完全吻合，验证了公式的正确性。\n")
cat("第6题图片输出完成\n")
