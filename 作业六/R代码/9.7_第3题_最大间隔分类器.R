# 第3题：用小型数据集探索最大间隔分类器（概念+作图）
# 高级统计方法 第6次作业
# 张鸿昊 20242081353
#
# 数据：7个观测，2个特征，2个类别
#   Obs  X1  X2   Y
#   1    3   4   Red
#   2    2   2   Red
#   3    4   4   Red
#   4    1   4   Red
#   5    2   1   Blue
#   6    4   3   Blue
#   7    4   1   Blue

X1 <- c(3, 2, 4, 1, 2, 4, 4)
X2 <- c(4, 2, 4, 4, 1, 3, 1)
Y  <- c("Red", "Red", "Red", "Red", "Blue", "Blue", "Blue")

# ---- (b)(c) 最优分割超平面 ----
# 观察可知，支持向量为 obs2(2,2,Red), obs3(4,4,Red), obs5(2,1,Blue), obs6(4,3,Blue)
# 最优超平面位于 Red 点(X2较大)与 Blue 点(X2较小)之间，
# 由 (2,1.5) 和 (4,3.5) 两点确定：斜率=1，过这两点 -> X2 = X1 - 0.5
# 即 -0.5 + X1 - X2 = 0  =>  beta0=-0.5, beta1=1, beta2=-1
# (c) 分类规则：若 -0.5 + X1 - X2 > 0 判为 Blue，否则 Red。
#     （Blue点在直线下方 X2<X1-0.5，使 -0.5+X1-X2>0）
b0 <- -0.5; b1 <- 1; b2 <- -1
cat("最优分割超平面: ", b0, "+", b1, "*X1 +", b2, "*X2 = 0\n")
cat("即 X2 = X1 - 0.5\n")
f <- b0 + b1 * X1 + b2 * X2
cat("\n各点判别值 (f>0 -> Blue, f<0 -> Red):\n")
print(data.frame(X1, X2, Y, f = f, 判别 = ifelse(f > 0, "Blue", "Red")))

# (d) 间隔：支持向量到超平面距离。直线 X1 - X2 - 0.5 = 0
#     点(2,2)到直线距离 = |2-2-0.5|/sqrt(1^2+1^2) = 0.5/sqrt(2) = 0.3536
#     间隔(margin) = 0.3536（半间隔），两侧总间隔 = 2*0.3536 = 0.7071
margin <- 0.5 / sqrt(2)
cat("\n(d) 最大间隔(到超平面距离) =", round(margin, 4), "\n")
cat("(e) 支持向量为 obs2(2,2)、obs3(4,4)、obs5(2,1)、obs6(4,3)\n")
cat("(f) 第7个观测(4,1)远离边界，轻微移动不会改变最大间隔超平面\n")

# ---- 作图：观测点 + 最优超平面 + 间隔 + 一个非最优超平面 ----
png("../图片输出/q3_最大间隔分类器.png", width = 650, height = 650)
plot(X1, X2, col = ifelse(Y == "Red", "red", "blue"), pch = 19, cex = 2,
     xlim = c(0, 5), ylim = c(0, 5), xlab = "X1", ylab = "X2",
     main = "最大间隔分类器")
text(X1, X2, labels = 1:7, pos = 4, cex = 1.1)
# 最优超平面 X2 = X1 - 0.5
abline(a = -0.5, b = 1, lwd = 3)
# 间隔边界（平行线）
abline(a = 0, b = 1, lty = 2, col = "gray40")     # 上边界 X2=X1
abline(a = -1, b = 1, lty = 2, col = "gray40")    # 下边界 X2=X1-1
# (g) 一个非最优分割超平面（也能分开但间隔不是最大）
abline(a = -0.2, b = 0.9, lwd = 2, col = "darkgreen", lty = 3)
legend("topleft",
       legend = c("最优超平面 X2=X1-0.5", "间隔边界", "非最优超平面(g)"),
       lwd = c(3, 1, 2), lty = c(1, 2, 3),
       col = c("black", "gray40", "darkgreen"))
dev.off()

cat("\n(g) 非最优超平面示例: -0.2 + 0.9*X1 - X2 = 0（图中绿色虚线）\n")
cat("(h) 若在(2,3)附近增加一个Blue点，则两类无法被任何超平面线性分离\n")
cat("\n第3题图片输出完成\n")
