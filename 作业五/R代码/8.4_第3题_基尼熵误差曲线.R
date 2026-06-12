# 第3题：基尼指数、分类误差、交叉熵随p_m1的变化曲线
# 高级统计方法 第5次作业
# 张鸿昊 20242081353

# 两类别情形：p_m1为第1类的比例，p_m2 = 1 - p_m1
p <- seq(0, 1, 0.001)

# 分类误差率： E = 1 - max(p, 1-p)
class.error <- 1 - pmax(p, 1 - p)

# 基尼指数： G = 2*p*(1-p)  （两类时 Σp_mk(1-p_mk) = p(1-p)+(1-p)p = 2p(1-p)）
gini <- 2 * p * (1 - p)

# 交叉熵： D = -[p*log(p) + (1-p)*log(1-p)]
entropy <- -(p * log(p) + (1 - p) * log(1 - p))
entropy[is.nan(entropy)] <- 0   # 处理 p=0 和 p=1 的 0*log(0)=0

png("../图片输出/q3_三种指标曲线.png", width = 650, height = 500)
plot(p, gini, type = "l", lwd = 2, col = "red", ylim = c(0, 0.75),
     xlab = expression(hat(p)[m1]), ylab = "指标值",
     main = "基尼指数 / 分类误差 / 交叉熵")
lines(p, class.error, lwd = 2, col = "blue")
lines(p, entropy, lwd = 2, col = "darkgreen")
legend("topright", legend = c("基尼指数", "分类误差", "交叉熵"),
       col = c("red", "blue", "darkgreen"), lwd = 2)
dev.off()

cat("三种指标都在 p=0.5 处取最大、在 p=0/1 处为0。\n")
cat("分类误差是折线（在0.5处不可导），基尼与交叉熵更光滑，\n")
cat("因此建树时常用基尼指数或交叉熵而非分类误差率。\n")
cat("第3题图片输出完成\n")
