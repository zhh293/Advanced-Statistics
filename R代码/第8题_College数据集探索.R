# ============================================================
# ISLR 第2章 2.4节 第8题
# 题目类型：应用题（探索性数据分析）
# 数据集：College（ISLR2包内置，777所美国大学数据）
# 知识点：数据读取、summary()、pairs()、箱线图、直方图、因子变量创建
# ============================================================
#
# 【题目背景】
# College数据集包含777所美国大学的18个变量，包括是否私立、
# 申请人数、录取人数、学费等。本题要求做基本的探索性分析。
#
# 【为什么做探索性分析（EDA）？】
# 在建模之前，EDA帮助我们：
#   1. 了解数据的基本分布（是否有异常值、偏态等）
#   2. 发现变量之间的关联关系
#   3. 为后续建模选择合适的变量和方法
# ============================================================

library(ISLR2)   # 加载包含College数据集的库

# ------ 第(a)题：读取数据 ------
# 题目要求用read.csv()从文件读取，这里直接用包内置数据集效果相同
data(College)
cat("=== 数据集基本信息 ===\n")
cat("行数（大学数量）：", nrow(College), "\n")
cat("列数（变量数量）：", ncol(College), "\n")
cat("变量名：\n")
print(names(College))

# ------ 第(b)题：查看数据集 ------
# head()查看前几行，了解数据结构
cat("\n=== 前3行数据 ===\n")
print(head(College, 3))
# 注意：行名是大学名称，这是一个重要的数据特征

# ------ 第(c.i)题：数值摘要 ------
# 为什么用summary()：一次性获取每个变量的最小值、四分位数、均值、最大值
# 对因子变量（Private）会显示各类别的频数
cat("\n=== 数值摘要（前5列）===\n")
print(summary(College[, 1:5]))

# ------ 第(c.ii)题：散点图矩阵 ------
# 为什么用pairs()：同时展示多个变量两两之间的散点图
# 可以快速发现哪些变量之间存在线性或非线性关系
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q8_散点图矩阵.png",
    width = 900, height = 900, res = 100)
pairs(College[, 1:10],
      main = "College数据集前10个变量的散点图矩阵",
      cex = 0.3, col = ifelse(College$Private == "Yes", "steelblue", "tomato"))
dev.off()
cat("\n图片已保存：q8_散点图矩阵.png\n")

# ------ 第(c.iii)题：Outstate vs Private 箱线图 ------
# 为什么用箱线图：比较两组（私立/公立）的州外学费分布差异
# plot(因子, 数值) 在R中会自动生成箱线图
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q8_学费箱线图.png",
    width = 600, height = 500, res = 100)
plot(College$Private, College$Outstate,
     xlab = "是否私立 (Private)",
     ylab = "州外学费 (Outstate, 美元)",
     main = "私立 vs 公立大学的州外学费比较",
     col  = c("lightblue", "lightcoral"))
# 从图中可以看出：私立大学学费中位数明显高于公立大学
dev.off()
cat("图片已保存：q8_学费箱线图.png\n")

# ------ 第(c.iv)题：创建Elite变量 ------
# 为什么要创建新变量：将连续变量（Top10perc）转化为分类变量，
# 便于比较"精英大学"和"普通大学"之间的差异
#
# 规则：Top10perc > 50 → Elite = "Yes"（超过50%的学生来自高中前10%）
Elite <- rep("No", nrow(College))          # 先全部初始化为"No"
Elite[College$Top10perc > 50] <- "Yes"     # 满足条件的改为"Yes"
Elite <- as.factor(Elite)                  # 转为因子类型，便于后续分析
College <- data.frame(College, Elite)      # 添加到数据框

cat("\n=== Elite大学统计 ===\n")
print(summary(Elite))
# 结果：No:699, Yes:78 → 只有约10%的大学是精英大学

# Elite vs Outstate 箱线图
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q8_精英大学学费.png",
    width = 600, height = 500, res = 100)
plot(College$Elite, College$Outstate,
     xlab = "是否精英大学 (Elite)",
     ylab = "州外学费 (Outstate, 美元)",
     main = "精英大学 vs 普通大学的州外学费",
     col  = c("lightyellow", "lightcoral"))
dev.off()
cat("图片已保存：q8_精英大学学费.png\n")

# ------ 第(c.v)题：直方图 ------
# 为什么用直方图：展示单个变量的分布形态（正态/偏态/双峰等）
# par(mfrow=c(2,2)) 将画布分成2行2列，同时展示4个直方图
png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q8_直方图.png",
    width = 900, height = 700, res = 100)
par(mfrow = c(2, 2), mar = c(4, 4, 3, 1))

hist(College$Apps,
     breaks = 50,
     main   = "申请人数分布 (Apps)",
     xlab   = "申请人数",
     col    = "steelblue",
     border = "white")
# 右偏分布：大多数学校申请人数较少，少数顶尖学校申请人数极多

hist(College$Accept,
     breaks = 50,
     main   = "录取人数分布 (Accept)",
     xlab   = "录取人数",
     col    = "tomato",
     border = "white")

hist(College$Enroll,
     breaks = 50,
     main   = "注册人数分布 (Enroll)",
     xlab   = "注册人数",
     col    = "seagreen",
     border = "white")

hist(College$Outstate,
     breaks = 50,
     main   = "州外学费分布 (Outstate)",
     xlab   = "学费（美元）",
     col    = "gold",
     border = "white")
# 相对均匀，集中在5000-20000美元区间

dev.off()
cat("图片已保存：q8_直方图.png\n")

# ------ 额外探索：录取率分析 ------
# 为什么要算录取率：比申请/录取人数的绝对值更有意义
College$AcceptRate <- College$Accept / College$Apps
cat("\n=== 录取率统计 ===\n")
cat("最低录取率：", round(min(College$AcceptRate) * 100, 1), "%\n")
cat("最高录取率：", round(max(College$AcceptRate) * 100, 1), "%\n")
cat("平均录取率：", round(mean(College$AcceptRate) * 100, 1), "%\n")

png("/Users/zhanghonghao/Desktop/高统作业/图片输出/q8_录取率vs学费.png",
    width = 600, height = 500, res = 100)
plot(College$AcceptRate, College$Outstate,
     col  = ifelse(College$Elite == "Yes", "red", "gray70"),
     pch  = 16, cex = 0.7,
     xlab = "录取率",
     ylab = "州外学费（美元）",
     main = "录取率 vs 州外学费（红色=精英大学）")
legend("topright", legend = c("精英大学", "普通大学"),
       col = c("red", "gray70"), pch = 16, cex = 0.9)
dev.off()
cat("图片已保存：q8_录取率vs学费.png\n")

cat("\n=== 第8题全部代码运行完毕 ===\n")
