# 第4章第12题：编写Power函数
# 高级统计方法 第3次作业
# 张鸿昊 20242081353

# ====== (a) Power() 函数 ======
Power <- function() {
  print(2^3)
}
Power()

# ====== (b) Power2() 函数 ======
Power2 <- function(x, a) {
  print(x^a)
}
Power2(3, 8)

# ====== (c) 验证 Power2 ======
Power2(10, 3)    # 1000
Power2(8, 17)    # 2251799813685248
Power2(131, 3)   # 2248091

# ====== (d) Power3() 函数（返回值而非打印） ======
Power3 <- function(x, a) {
  return(x^a)
}

# ====== (e) 绘制 x^2 图形 ======
x <- 1:10

png("../图片输出/q4_12_幂函数.png", width=600, height=450)
par(mfrow=c(1,2))
plot(x, Power3(x, 2), main="f(x) = x^2", xlab="x", ylab="x^2",
     type="b", col="blue", pch=16)
plot(x, log(Power3(x, 2)), main="log(x^2)", xlab="x", ylab="log(x^2)",
     type="b", col="red", pch=16)
dev.off()

# ====== (f) PlotPower() 函数 ======
PlotPower <- function(x, a) {
  y <- x^a
  plot(x, y, main=paste0("f(x) = x^", a), 
       xlab="x", ylab=paste0("x^", a),
       type="b", col="blue", pch=16)
}

png("../图片输出/q4_12_PlotPower.png", width=800, height=400)
par(mfrow=c(1,3))
PlotPower(1:10, 3)
PlotPower(1:10, 0.5)
PlotPower(1:10, -1)
dev.off()

cat("第4章第12题完成\n")
