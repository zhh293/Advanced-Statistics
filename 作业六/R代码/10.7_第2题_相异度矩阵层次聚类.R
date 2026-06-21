# 第2题：4个观测的相异度矩阵 - 最长/最短距离法系统聚类（概念+作图）
# 高级统计方法 第6次作业
# 张鸿昊 20242081353
#
# 相异度矩阵（对称）：
#        1     2     3     4
#   1    0    0.3   0.4   0.7
#   2   0.3    0    0.5   0.8
#   3   0.4   0.5    0    0.45
#   4   0.7   0.8   0.45   0

d <- matrix(c(0,    0.3,  0.4,  0.7,
              0.3,  0,    0.5,  0.8,
              0.4,  0.5,  0,    0.45,
              0.7,  0.8,  0.45, 0), nrow = 4, byrow = TRUE)
rownames(d) <- colnames(d) <- 1:4
dist.obj <- as.dist(d)

# ====== (a) 最长距离法(complete linkage)系统聚类 ======
hc.complete <- hclust(dist.obj, method = "complete")
cat("=== (a) 最长距离法 汇合顺序与高度 ===\n")
print(data.frame(merge = apply(hc.complete$merge, 1, paste, collapse = " & "),
                 height = hc.complete$height))
# 说明：先{1,2}在0.3汇合，{3,4}在0.45汇合，最后两组在0.8(最长距离)汇合

# ====== (b) 最短距离法(single linkage)系统聚类 ======
hc.single <- hclust(dist.obj, method = "single")
cat("\n=== (b) 最短距离法 汇合顺序与高度 ===\n")
print(data.frame(merge = apply(hc.single$merge, 1, paste, collapse = " & "),
                 height = hc.single$height))

# ====== 作图：两种谱系图 ======
png("../图片输出/q2_两种聚类谱系图.png", width = 1000, height = 450)
par(mfrow = c(1, 2))
plot(hc.complete, main = "(a) 最长距离法", xlab = "", sub = "", ylab = "高度")
plot(hc.single, main = "(b) 最短距离法", xlab = "", sub = "", ylab = "高度")
dev.off()

# ====== (c)(d) 切割成两个类 ======
cat("\n=== (c) 最长距离法切割成2类 ===\n")
print(cutree(hc.complete, 2))     # {1,2} 与 {3,4}
cat("=> 类A={1,2}, 类B={3,4}\n")
cat("\n=== (d) 最短距离法切割成2类 ===\n")
print(cutree(hc.single, 2))       # {1,2,3} 与 {4}
cat("=> 类A={1,2,3}, 类B={4}\n")

cat("\n(e) 谱系图中每次汇合时，左右两片子树交换位置不改变含义。\n")
cat("第2题图片输出完成\n")
