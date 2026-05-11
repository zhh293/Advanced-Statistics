# ============================================================
# ISLR 第2章 2.4节 第9题
# 题目类型：应用题（变量类型识别 + 描述统计 + 探索性分析）
# 数据集：Auto（ISLR2包内置，392辆汽车的燃油效率数据）
# 知识点：定量/定性变量区分、range()、mean()、sd()、子集操作、相关系数
# ============================================================
#
# 【题目背景】
# Auto数据集记录了392辆汽车的9个变量，包括油耗(mpg)、气缸数、
# 排量、马力、重量、加速度、年份、产地和车型名称。
# 本题要求识别变量类型、计算描述统计量，并探索哪些变量能预测mpg。
#
# 【为什么区分定量/定性变量很重要？】
# 定量变量（连续/离散数值）：可以计算均值、方差、相关系数
# 定性变量（类别）：需要用频数表、箱线图等方式分析
# 错误地将定性变量当定量处理会导致错误的统计结论
# ============================================================

library(ISLR2)
data(Auto)

cat("=== Auto数据集基本信息 ===\n")
cat("维度：", dim(Auto), "\n")
cat("变量名：", names(Auto), "\n")
print(str(Auto))

# ------ 第(a)题：识别定量与定性变量 ------
cat("\n=== 第(a)题：变量类型识别 ===\n")
cat("定量变量（可以计算均值/方差）：\n")
cat("  mpg          - 每加仑英里数（连续）\n")
cat("  cylinders    - 气缸数（离散，但通常作定量处理）\n")
cat("  displacement - 发动机排量（连续）\n")
cat("  horsepower   - 马力（连续）\n")
cat("  weight       - 车重（连续）\n")
cat("  acceleration - 0到60mph加速时间（连续）\n")
cat("  year         - 出厂年份（离散）\n")
cat("\n定性变量（类别标签）：\n")
cat("  origin - 产地（1=美国, 2=欧洲, 3=日本）虽存为数字，实为类别\n")
cat("  name   - 车型名称（字符串）\n")

# ------ 第(b)题：定量变量的范围 ------
# 为什么用range()：同时返回最小值和最大值，比分别调用min/max更简洁
quant_vars <- c("mpg","cylinders","displacement","horsepower",
                "weight","acceleration","year")

cat("\n=== 第(b)题：定量变量的范围 ===\n")
for (v in quant_vars) {
  r <- range(Auto[[v]], na.rm = TRUE)
  cat(sprintf("  %-15s: [%6.1f, %6.1f]\n", v, r[1], r[2]))
}

# ------ 第(c)题：均值和标准差 ------
# 为什么用sd()：标准差衡量数据的离散程度，与均值配合描述分布
cat("\n=== 第(c)题：均值和标准差 ===\n")
for (v in quant_vars) {
  cat(sprintf("  %-15s: 均值=%7.2f, 标准差=%7.2f\n",
              v, mean(Auto[[v]], na.rm=TRUE), sd(Auto[[v]], na.rm=TRUE)))
}

# ------ 第(d)题：移除第10-85行后重新计算 ------
# 为什么要做这个操作：练习子集操作，同时观察移除部分数据后统计量的变化
# 负索引 -(10:85) 表示"除了第10到85行之外的所有行"
Auto_sub <- Auto[-(10:85), ]
cat("\n=== 第(d)题：移除第10-85行后（共", nrow(Auto_sub), "行）===\n")
for (v in quant_vars) {
  r <- range(Auto_sub[[v]], na.rm = TRUE)
  cat(sprintf("  %-15s: 范围=[%6.1f,%6.1f], 均值=%7.2f, 标准差=%6.2f\n",
              v, r[1], r[2],
              mean(Auto_sub[[v]], na.rm=TRUE),
              sd(Auto_sub[[v]], na.rm=TRUE)))
}
cat("观察：移除76个观测后，各变量统计量变化不大，说明数据分布较稳定\n")

# ------ 第(e)题：探索性分析图 ------
# 为什么先画散点图矩阵：快速发现所有变量对之间的关系
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q9_散点图矩阵.png",
    width = 900, height = 900, res = 100)
pairs(Auto[, 1:7],
      main = "Auto数据集定量变量散点图矩阵",
      col  = "steelblue",
      cex  = 0.4)
# 从图中可以看出：
# - mpg与weight、displacement、horsepower呈明显负相关（曲线形）
# - weight与displacement、horsepower高度正相关（多重共线性）
# - year与mpg有正相关（越新的车越省油）
dev.off()
cat("\n图片已保存：q9_散点图矩阵.png\n")

# mpg vs weight 详细图（最强的负相关关系）
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q9_mpg与weight关系.png",
    width = 700, height = 500, res = 100)
plot(Auto$weight, Auto$mpg,
     xlab = "车重 (weight, 磅)",
     ylab = "油耗 (mpg, 英里/加仑)",
     main = "车重 vs 油耗（附线性回归拟合线）",
     col  = "steelblue", pch = 16, cex = 0.7)
# 添加线性回归拟合线：lm()拟合线性模型，abline()画出拟合线
abline(lm(mpg ~ weight, data = Auto), col = "red", lwd = 2)
# 添加LOESS平滑曲线：展示真实的非线性关系
lines(lowess(Auto$weight, Auto$mpg), col = "orange", lwd = 2, lty = 2)
legend("topright",
       legend = c("线性拟合", "LOESS平滑"),
       col    = c("red", "orange"),
       lty    = c(1, 2), lwd = 2, cex = 0.9)
# 观察：关系呈非线性（曲线），重车油耗高，轻车油耗低
dev.off()
cat("图片已保存：q9_mpg与weight关系.png\n")

# 按年份看mpg变化趋势
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q9_mpg年份趋势.png",
    width = 700, height = 500, res = 100)
boxplot(mpg ~ year, data = Auto,
        xlab = "出厂年份（70=1970年）",
        ylab = "油耗 (mpg)",
        main = "各年份汽车油耗分布",
        col  = "lightblue")
# 观察：1970年代末到1980年代初，油耗明显改善（受石油危机影响）
dev.off()
cat("图片已保存：q9_mpg年份趋势.png\n")

# ------ 第(f)题：哪些变量有助于预测mpg？ ------
# 为什么用相关系数：衡量线性关系的强度和方向
# cor()计算相关矩阵，取mpg那一行
cat("\n=== 第(f)题：各变量与mpg的相关系数 ===\n")
cor_matrix <- cor(Auto[, quant_vars], use = "complete.obs")
cor_mpg    <- sort(cor_matrix["mpg", ], decreasing = TRUE)
print(round(cor_mpg, 3))

cat("\n结论：\n")
cat("  强负相关（|r|>0.7）：weight(-0.832), displacement(-0.805),\n")
cat("                       cylinders(-0.778), horsepower(-0.778)\n")
cat("  → 这4个变量是预测mpg最重要的特征\n")
cat("  正相关：year(0.581) → 新款车型燃油效率更高\n")
cat("  弱相关：acceleration(0.423) → 加速性能与油耗有一定关系\n")

# 相关系数可视化
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q9_相关系数.png",
    width = 700, height = 450, res = 100)
par(mar = c(5, 7, 3, 2))
barplot(cor_mpg[-1],   # 去掉mpg自身（相关系数=1）
        horiz  = TRUE,
        las    = 1,
        col    = ifelse(cor_mpg[-1] > 0, "steelblue", "tomato"),
        main   = "各变量与mpg的相关系数",
        xlab   = "Pearson相关系数",
        xlim   = c(-1, 1))
abline(v = 0, col = "black", lwd = 1)
abline(v = c(-0.7, 0.7), col = "gray50", lty = 2)
dev.off()
cat("图片已保存：q9_相关系数.png\n")

cat("\n=== 第9题全部代码运行完毕 ===\n")
