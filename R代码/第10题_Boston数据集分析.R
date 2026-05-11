# ============================================================
# ISLR 第2章 2.4节 第10题
# 题目类型：应用题（多维度探索性分析）
# 数据集：Boston（ISLR2包内置，波士顿506个郊区的住房数据）
# 知识点：cor()相关分析、which.min()、条件筛选、summary()对比
# ============================================================
#
# 【题目背景】
# Boston数据集包含波士顿地区506个郊区的13个变量，
# 核心响应变量是medv（房屋中位价值，单位千美元）。
# 本题要求全面探索数据，重点分析犯罪率(crim)的影响因素。
#
# 【变量说明】
# crim    - 人均犯罪率
# zn      - 住宅用地超过25000平方英尺的比例
# indus   - 非零售商业用地比例
# chas    - 是否临查尔斯河（1=是，0=否）
# nox     - 氮氧化物浓度（每千万份）
# rm      - 每套住宅平均房间数
# age     - 1940年前建造的自住房比例
# dis     - 到波士顿5个就业中心的加权距离
# rad     - 公路可达性指数
# tax     - 每万美元财产税率
# ptratio - 师生比
# lstat   - 低收入人口比例（%）
# medv    - 自住房中位价值（千美元）← 通常作为响应变量
# ============================================================

library(ISLR2)
data(Boston)

# ------ 第(a)题：数据集基本描述 ------
cat("=== 第(a)题：Boston数据集描述 ===\n")
cat("行数（郊区数量）：", nrow(Boston), "\n")
cat("列数（变量数量）：", ncol(Boston), "\n")
cat("变量名：", names(Boston), "\n")
cat("\n数值摘要：\n")
print(summary(Boston))

# ------ 第(b)题：散点图矩阵 ------
# 为什么画散点图矩阵：13个变量两两之间的关系一览无余
# 可以快速发现：哪些变量与medv（房价）相关，哪些变量之间存在多重共线性
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q10_散点图矩阵.png",
    width = 1000, height = 1000, res = 100)
pairs(Boston,
      main = "Boston数据集散点图矩阵（13个变量）",
      col  = "steelblue",
      cex  = 0.2)
dev.off()
cat("\n图片已保存：q10_散点图矩阵.png\n")

# ------ 第(c)题：与犯罪率相关的变量 ------
# 为什么用cor()：计算所有变量与crim的线性相关系数
# 相关系数范围[-1,1]，绝对值越大说明线性关系越强
cat("\n=== 第(c)题：与犯罪率(crim)的相关系数 ===\n")
cor_crim <- cor(Boston)["crim", ]
print(round(sort(cor_crim, decreasing = TRUE), 3))

cat("\n解读：\n")
cat("  正相关（犯罪率随之升高）：\n")
cat("    rad(0.626)  - 公路可达性高 → 犯罪率高（交通便利利于逃跑？）\n")
cat("    tax(0.583)  - 高税率地区 → 犯罪率高（贫困地区税率高）\n")
cat("    lstat(0.456)- 低收入人口多 → 犯罪率高（贫困与犯罪的关联）\n")
cat("  负相关（犯罪率随之降低）：\n")
cat("    medv(-0.388)- 房价高 → 犯罪率低（富裕地区治安好）\n")
cat("    dis(-0.380) - 距就业中心远 → 犯罪率低（郊区更安全）\n")

# 犯罪率与关键变量的散点图
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q10_犯罪率关联分析.png",
    width = 900, height = 700, res = 100)
par(mfrow = c(2, 3), mar = c(4, 4, 3, 1))

plot(Boston$rad,   Boston$crim, pch=16, cex=0.5, col="tomato",
     xlab="公路可达性(rad)", ylab="犯罪率(crim)", main="crim vs rad (r=0.626)")
plot(Boston$tax,   Boston$crim, pch=16, cex=0.5, col="tomato",
     xlab="税率(tax)", ylab="犯罪率(crim)", main="crim vs tax (r=0.583)")
plot(Boston$lstat, Boston$crim, pch=16, cex=0.5, col="tomato",
     xlab="低收入比例(lstat)", ylab="犯罪率(crim)", main="crim vs lstat (r=0.456)")
plot(Boston$medv,  Boston$crim, pch=16, cex=0.5, col="steelblue",
     xlab="房价中位值(medv)", ylab="犯罪率(crim)", main="crim vs medv (r=-0.388)")
plot(Boston$dis,   Boston$crim, pch=16, cex=0.5, col="steelblue",
     xlab="到就业中心距离(dis)", ylab="犯罪率(crim)", main="crim vs dis (r=-0.380)")
plot(Boston$nox,   Boston$crim, pch=16, cex=0.5, col="orange",
     xlab="氮氧化物浓度(nox)", ylab="犯罪率(crim)", main="crim vs nox (r=0.421)")
dev.off()
cat("图片已保存：q10_犯罪率关联分析.png\n")

# ------ 第(d)题：犯罪率、税率、师生比的范围 ------
cat("\n=== 第(d)题：关键变量范围 ===\n")
cat(sprintf("犯罪率(crim)   : 范围=[%5.3f, %5.2f], 均值=%5.2f, 中位数=%5.3f\n",
            min(Boston$crim), max(Boston$crim),
            mean(Boston$crim), median(Boston$crim)))
cat(sprintf("税率(tax)      : 范围=[%5.1f, %5.1f], 均值=%5.1f\n",
            min(Boston$tax), max(Boston$tax), mean(Boston$tax)))
cat(sprintf("师生比(ptratio): 范围=[%5.1f, %5.1f], 均值=%5.1f\n",
            min(Boston$ptratio), max(Boston$ptratio), mean(Boston$ptratio)))

# 犯罪率分布图（原始 + 对数变换）
# 为什么要做对数变换：犯罪率分布极度右偏，对数变换后更接近正态分布
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q10_犯罪率分布.png",
    width = 800, height = 400, res = 100)
par(mfrow = c(1, 2), mar = c(4, 4, 3, 1))
hist(Boston$crim,
     breaks = 50, col = "tomato", border = "white",
     main = "犯罪率原始分布（极度右偏）",
     xlab = "crim")
hist(log(Boston$crim + 1),
     breaks = 30, col = "steelblue", border = "white",
     main = "log(crim+1)分布（更接近正态）",
     xlab = "log(crim+1)")
dev.off()
cat("图片已保存：q10_犯罪率分布.png\n")

# 高犯罪率郊区分析
high_crim_threshold <- quantile(Boston$crim, 0.95)
high_crim <- Boston[Boston$crim > high_crim_threshold, ]
cat(sprintf("\n犯罪率前5%%的郊区（crim > %.2f）共%d个\n",
            high_crim_threshold, nrow(high_crim)))

# ------ 第(e)题：查尔斯河边的郊区 ------
# chas是虚拟变量（0/1），sum()可以直接统计1的个数
cat("\n=== 第(e)题：临查尔斯河的郊区 ===\n")
cat("chas=1的郊区数量：", sum(Boston$chas == 1), "\n")
cat("占总郊区比例：", round(mean(Boston$chas == 1) * 100, 1), "%\n")

# ------ 第(f)题：师生比中位数 ------
cat("\n=== 第(f)题：师生比中位数 ===\n")
cat("ptratio中位数：", median(Boston$ptratio), "\n")
cat("解读：典型郊区每位教师对应约19名学生\n")

# ------ 第(g)题：房价最低的郊区 ------
# which.min()返回最小值所在的行索引
cat("\n=== 第(g)题：medv最低的郊区 ===\n")
min_idx <- which.min(Boston$medv)
cat("最低房价郊区编号：", min_idx, "\n")
cat("该郊区数据：\n")
print(Boston[min_idx, ])

cat("\n与全体均值对比：\n")
comparison <- rbind(
  "最低房价郊区" = as.numeric(Boston[min_idx, ]),
  "全体均值"     = round(colMeans(Boston), 3)
)
colnames(comparison) <- names(Boston)
print(comparison)
cat("\n解读：该郊区犯罪率极高(38.35 vs 均值3.61)、\n")
cat("      税率极高(666 vs 均值408)、低收入比例极高(30.59 vs 均值12.65)\n")
cat("      这些因素共同导致房价极低(5千美元 vs 均值22.5千美元)\n")

# ------ 第(h)题：大房间数郊区 ------
cat("\n=== 第(h)题：平均房间数分析 ===\n")
cat("rm > 7 的郊区数量：", sum(Boston$rm > 7), "\n")
cat("rm > 8 的郊区数量：", sum(Boston$rm > 8), "\n")

cat("\nrm > 8 的郊区统计摘要：\n")
print(summary(Boston[Boston$rm > 8, ]))

cat("\n解读：rm>8的郊区（13个）特征：\n")
cat("  - 犯罪率低（均值0.72 vs 全体3.61）\n")
cat("  - 房价极高（medv均值44.2千美元 vs 全体22.5千美元）\n")
cat("  - 低收入人口少（lstat均值4.31 vs 全体12.65）\n")
cat("  - 师生比低（ptratio均值16.36 vs 全体18.46）\n")
cat("  → 这些是波士顿地区的高档住宅区\n")

# 房间数与房价的关系图
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q10_房间数与房价.png",
    width = 700, height = 500, res = 100)
plot(Boston$rm, Boston$medv,
     col  = ifelse(Boston$rm > 8, "red",
            ifelse(Boston$rm > 7, "orange", "steelblue")),
     pch  = 16, cex = 0.7,
     xlab = "平均房间数 (rm)",
     ylab = "房价中位值 (medv, 千美元)",
     main = "平均房间数 vs 房价（红色=rm>8，橙色=rm>7）")
abline(v = c(7, 8), lty = 2, col = c("orange", "red"))
legend("topleft",
       legend = c("rm > 8", "7 < rm ≤ 8", "rm ≤ 7"),
       col    = c("red", "orange", "steelblue"),
       pch    = 16, cex = 0.9)
dev.off()
cat("\n图片已保存：q10_房间数与房价.png\n")

cat("\n=== 第10题全部代码运行完毕 ===\n")
