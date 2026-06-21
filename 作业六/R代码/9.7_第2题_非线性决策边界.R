# 第2题：非线性决策边界（概念+作图）
# 高级统计方法 第6次作业
# 张鸿昊 20242081353
#
# 决策边界为圆 (1+X1)^2 + (2-X2)^2 = 4，圆心(-1,2)，半径2。
#
# (a) 画出曲线 (1+X1)^2 + (2-X2)^2 = 4。
# (b) 区分 >4（圆外）与 <=4（圆内）的点集。
# (c) 分类规则：(1+X1)^2+(2-X2)^2 > 4 判为蓝色，否则红色。
#     (0,0): (1)^2+(2)^2 = 1+4 = 5 > 4   -> 蓝色
#     (-1,1): 0 + 1 = 1 <= 4              -> 红色
#     (2,2): 9 + 0 = 9 > 4                -> 蓝色
#     (3,8): 16 + 36 = 52 > 4             -> 蓝色
# (d) 对 X1,X2 是非线性的（含平方项），但展开后
#     (1+X1)^2+(2-X2)^2 = 1+2X1+X1^2 +4-4X2+X2^2
#     = 5 + 2*X1 - 4*X2 + 1*X1^2 + 1*X2^2
#     对 X1, X1^2, X2, X2^2 而言是线性的。

# ---- (c) 四个测试点的判别 ----
pts <- data.frame(X1 = c(0, -1, 2, 3), X2 = c(0, 1, 2, 8))
val <- (1 + pts$X1)^2 + (2 - pts$X2)^2
pts$value <- val
pts$class <- ifelse(val > 4, "蓝色(Blue)", "红色(Red)")
cat("各测试点判别结果：\n")
print(pts)

# ---- (a)(b) 画出圆形决策边界及内外区域 ----
png("../图片输出/q2_决策边界.png", width = 600, height = 600)
# 背景：在网格上根据规则上色
g <- seq(-4, 4, length.out = 300)
grid <- expand.grid(X1 = g, X2 = g)
gv <- (1 + grid$X1)^2 + (2 - grid$X2)^2
cols <- ifelse(gv > 4, "lightblue", "mistyrose")
plot(grid$X1, grid$X2, col = cols, pch = 15, cex = 0.6,
     xlab = "X1", ylab = "X2", main = "决策边界 (1+X1)^2+(2-X2)^2=4")
# 画圆（决策边界）
theta <- seq(0, 2 * pi, length.out = 200)
lines(-1 + 2 * cos(theta), 2 + 2 * sin(theta), lwd = 3)
# 标出四个测试点
points(pts$X1, pts$X2, pch = 19, cex = 1.6,
       col = ifelse(pts$value > 4, "blue", "red"))
text(pts$X1, pts$X2, labels = paste0("(", pts$X1, ",", pts$X2, ")"),
     pos = 3, cex = 1.1)
legend("topleft", legend = c("外部>4 判蓝", "内部<=4 判红"),
       fill = c("lightblue", "mistyrose"))
dev.off()

cat("\n第2题图片输出完成\n")
