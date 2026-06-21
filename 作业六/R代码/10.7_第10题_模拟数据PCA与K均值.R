# 第10题：模拟三类数据，主成分分析 + K均值聚类（应用题）
# 高级统计方法 第6次作业
# 张鸿昊 20242081353
#
# 题目：生成含3个类的模拟数据(每类20个观测、共60观测、50个变量)，
#   通过PCA可视化，并用K均值聚类(K=3,2,4)考察聚类与真实类的吻合程度。

set.seed(10)

# ====== (a) 生成数据：60观测×50变量，三类，类间有均值偏移 ======
n_each <- 20; p <- 50
# 基础噪声
X <- matrix(rnorm(60 * p), ncol = p)
# 给三类在若干变量上施加不同的均值偏移，使类之间可分
X[1:20,    1:10] <- X[1:20,    1:10] + 3      # 第1类
X[21:40,  11:20] <- X[21:40,  11:20] + 3      # 第2类
X[41:60,  21:30] <- X[41:60,  21:30] - 3      # 第3类
true.label <- rep(1:3, each = n_each)

# ====== (b) PCA，画前两个主成分得分 ======
pr.out <- prcomp(X, scale. = TRUE)
png("../图片输出/q10_PCA前两主成分.png", width = 700, height = 600)
plot(pr.out$x[, 1:2], col = c("red", "green3", "blue")[true.label],
     pch = 19, xlab = "第一主成分 PC1", ylab = "第二主成分 PC2",
     main = "图10-1 前两个主成分得分（颜色为真实类）")
legend("topright", legend = paste0("类", 1:3),
       col = c("red", "green3", "blue"), pch = 19)
dev.off()
cat("PCA前两主成分累计方差解释比例:",
    round(sum(pr.out$sdev[1:2]^2) / sum(pr.out$sdev^2), 3), "\n")

# 一个辅助函数：聚类标签与真实标签做交叉表
ct <- function(cl) table(真实类 = true.label, 聚类 = cl)

# ====== (c) K均值 K=3 ======
set.seed(1); km3 <- kmeans(X, centers = 3, nstart = 20)
cat("\n=== (c) K=3 聚类 vs 真实类 ===\n"); print(ct(km3$cluster))
cat("说明：3个类被完美分开（每个真实类对应一个聚类簇）。\n")

# ====== (d) K均值 K=2 ======
set.seed(1); km2 <- kmeans(X, centers = 2, nstart = 20)
cat("\n=== (d) K=2 聚类 vs 真实类 ===\n"); print(ct(km2$cluster))
cat("说明：3个真实类被迫合并成2簇，必有两个真实类被并到一起。\n")

# ====== (e) K均值 K=4 ======
set.seed(1); km4 <- kmeans(X, centers = 4, nstart = 20)
cat("\n=== (e) K=4 聚类 vs 真实类 ===\n"); print(ct(km4$cluster))
cat("说明：某个真实类被拆成2个子簇，多出的簇并无真实意义。\n")

# ====== (f) 对前两个主成分得分做 K=3 聚类 ======
set.seed(1); km3.pc <- kmeans(pr.out$x[, 1:2], centers = 3, nstart = 20)
cat("\n=== (f) 对前2个主成分得分 K=3 聚类 vs 真实类 ===\n"); print(ct(km3.pc$cluster))
cat("说明：仅用前2个主成分(降维后)仍能很好地分开三类。\n")

# ====== (g) 标准化(每列std=1)后 K=3 聚类 ======
set.seed(1); km3.sc <- kmeans(scale(X), centers = 3, nstart = 20)
cat("\n=== (g) 标准化后 K=3 聚类 vs 真实类 ===\n"); print(ct(km3.sc$cluster))
cat("说明：本例各变量量纲相近，标准化后结果与(c)基本一致。\n")

cat("\n第10题图片输出完成\n")
