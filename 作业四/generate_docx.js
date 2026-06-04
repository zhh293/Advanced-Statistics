const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType
} = require('docx');

const IMG = path.join(__dirname, '图片输出');

// ===== 样式 helper（精确复刻作业三）=====
// 标题：SimHei 加粗 sz32 居中
function title(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, font: 'SimHei', size: 32 })],
  });
}
// 信息行：SimSun sz24
function infoLine(text) {
  return new Paragraph({
    spacing: { before: 100, after: 200 },
    children: [new TextRun({ text, font: 'SimSun', size: 24 })],
  });
}
// 区块标题（概念/应用）：SimHei 加粗 sz28
function sectionTitle(text) {
  return new Paragraph({
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, font: 'SimHei', size: 28 })],
  });
}
// 题目：SimSun 加粗 sz24
function question(text) {
  return new Paragraph({
    spacing: { before: 50, after: 50 },
    children: [new TextRun({ text, bold: true, font: 'SimSun', size: 24 })],
  });
}
// 答案/内容行：SimSun sz24，左缩进480
function answer(text) {
  return new Paragraph({
    spacing: { before: 50, after: 50 },
    indent: { left: 480 },
    children: [new TextRun({ text, font: 'SimSun', size: 24 })],
  });
}
// 代码行：等宽字体 Consolas，左缩进480
function code(text) {
  return new Paragraph({
    spacing: { before: 50, after: 50 },
    indent: { left: 480 },
    children: [new TextRun({ text, font: 'Consolas', size: 22 })],
  });
}
// 空段落
function blank() {
  return new Paragraph({ spacing: { after: 50 }, children: [] });
}
// 图片：居中，按指定英寸
function image(file, wIn, hIn) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 50, after: 50 },
    children: [new ImageRun({
      type: 'png',
      data: fs.readFileSync(path.join(IMG, file)),
      transformation: { width: Math.round(wIn * 96), height: Math.round(hIn * 96) },
      altText: { title: file, description: file, name: file },
    })],
  });
}

const children = [];

// ===== 标题与信息行 =====
children.push(title('高级统计方法 第4次作业'));
children.push(blank());
children.push(infoLine('序号： 39  姓名： 张鸿昊  学号： 20242081353  班级：软件2410'));
children.push(blank());

// ===== 概念 =====
children.push(sectionTitle('概念'));

// 第3题
children.push(question('5.4节 第3题. 复习k折交叉验证。'));
children.push(blank());
children.push(answer('(a) 简述k折交叉验证的步骤。'));
children.push(answer('答：将观测随机分成k个大小相近的折(fold)。每次保留其中一折作为验证集、其余k-1折作为训练集，在训练集上拟合模型并在验证集上计算均方误差MSEᵢ。重复k次（每折轮流做验证集），最终的k折CV估计为 CV₍ₖ₎ = (1/k)ΣᵢMSEᵢ。'));
children.push(answer('(b) k折交叉验证相对于以下方法的优势和劣势：'));
children.push(answer('i. 相对验证集方法：验证集方法每次只用约一半数据训练，会高估测试错误率，且结果随划分随机波动大。k折CV利用了全部数据、偏差更小、估计更稳定；劣势是需训练k次，计算量更大。'));
children.push(answer('ii. 相对LOOCV：LOOCV需训练n次、计算成本高，且n个模型彼此高度相关导致CV估计的方差较大。k折CV(k=5或10)只需训练k次，折间相关性低、方差更小；劣势是偏差略高于LOOCV。这体现了偏差-方差权衡。'));
children.push(blank());

// 第4题
children.push(question('5.4节 第4题. 假设要用一些统计学习方法，对预测变量X的一个特定值，预测响应变量Y的值。请详细说明如何估计预测结果的标准差。'));
children.push(blank());
children.push(answer('答：可以使用自助法(Bootstrap)来估计预测的标准差。'));
children.push(answer('步骤：(1)对原始数据集进行有放回抽样B次，得到B个自助样本（每个样本含n个观测）；'));
children.push(answer('(2)在每个自助样本上拟合所用的统计学习模型，并对X的该特定值作出预测，得到B个预测值；'));
children.push(answer('(3)这B个预测值的标准差，即为该预测结果标准差的估计。'));
children.push(answer('自助法不依赖模型的分布假设，因此适用于KNN、决策树等没有解析标准误差公式的复杂模型。'));
children.push(blank());

// ===== 应用 =====
children.push(sectionTitle('应用'));

// 第6题
children.push(question('5.4节 第6题. 用Default数据集，对income和balance做逻辑斯蒂回归预测default，比较两种估计系数标准误差的方法。'));
children.push(blank());
children.push(answer('(a) 用summary()和glm()公式法估计income和balance系数的标准误差：'));
children.push(code('glm.fit <- glm(default ~ income + balance, data=Default, family=binomial)'));
children.push(answer('公式法标准误差：income SE = 4.985e-06，balance SE = 2.274e-04。'));
children.push(answer('(b) 编写boot.fn()函数，输入数据和观测索引，输出income和balance的系数估计：'));
children.push(code('boot.fn <- function(data, index) {'));
children.push(code('  fit <- glm(default ~ income + balance, data=data,'));
children.push(code('             family=binomial, subset=index)'));
children.push(code('  return(coef(fit)[2:3])  }'));
children.push(answer('(c) 用boot()自助法(R=1000)估计标准误差：'));
children.push(code('set.seed(1); boot(Default, boot.fn, R=1000)'));
children.push(answer('自助法标准误差：income SE = 4.866e-06，balance SE = 2.299e-04。'));
children.push(answer('(d) 比较：两种方法得到的标准误差非常接近（见下表）。公式法依赖逻辑斯蒂回归的渐近理论假设，自助法不依赖分布假设、直接通过重抽样估计变异性。二者吻合说明本例glm的渐近假设成立良好。'));
children.push(answer('income：公式法4.985e-06 vs 自助法4.866e-06；balance：公式法2.274e-04 vs 自助法2.299e-04。'));
children.push(image('q6_自助法分布.png', 5.0, 2.5));
children.push(blank());

// 第8题
children.push(question('5.4节 第8题. 在模拟数据集上用留一交叉验证(LOOCV)进行模型选择。'));
children.push(blank());
children.push(answer('(a) 生成数据：'));
children.push(code('set.seed(1); x <- rnorm(100); y <- x - 2*x^2 + rnorm(100)'));
children.push(answer('n=100，p=2（预测变量为x和x²）。生成数据的模型为 Y = X - 2X² + ε，即β₀=0, β₁=1, β₂=-2。'));
children.push(answer('(b) 作X对Y的散点图：散点呈倒U形（二次曲线），说明X与Y之间为明显的非线性关系。'));
children.push(image('q8_散点图.png', 4.2, 3.15));
children.push(answer('(c) 设随机种子后计算四个多项式模型的LOOCV误差：'));
children.push(code('for(i in 1:4){ glm.fit <- glm(y~poly(x,i), data=Data);'));
children.push(code('  cv.errors[i] <- cv.glm(Data, glm.fit)$delta[1] }'));
children.push(answer('i.线性=7.288；ii.二次=0.937；iii.三次=0.957；iv.四次=0.954。'));
children.push(image('q8_LOOCV误差.png', 4.2, 3.15));
children.push(answer('(d) 换另一个随机种子(seed=100)重复：四个模型的LOOCV误差与(c)完全相同。原因：LOOCV不涉及随机划分，每个观测都轮流做一次测试集，结果是确定性的，与随机种子无关。'));
children.push(answer('(e) 二次模型的LOOCV误差最小(0.937)。这与预期一致，因为真实模型就是二次的。'));
children.push(answer('(f) 系数显著性：拟合四次多项式后，只有1次项(p=4.6e-09)和2次项(p=1.6e-43)显著，3次项(p=0.78)和4次项(p=0.19)不显著。这与LOOCV选出二次模型的结论完全一致。'));
children.push(blank());

// 第9题
children.push(question('5.4节 第9题. 考虑Boston住房数据集，用自助法估计各种统计量的标准误差。'));
children.push(blank());
children.push(answer('(a) medv（房价中位数）总体均值的估计：μ̂ = mean(medv) = 22.53。'));
children.push(answer('(b) μ̂标准误差的公式法估计：SE = sd(medv)/√n = 0.409。'));
children.push(answer('(c) 自助法(R=1000)估计μ̂的标准误差：SE = 0.411，与(b)的0.409非常接近，验证了自助法的有效性。'));
children.push(code('boot.fn <- function(data,index) mean(data[index])'));
children.push(code('set.seed(1); boot(Boston$medv, boot.fn, R=1000)'));
children.push(answer('(d) 95%置信区间：自助法 [μ̂-2SE, μ̂+2SE] = [21.71, 23.35]；t.test = [21.73, 23.34]。两者高度吻合。'));
children.push(answer('(e) medv中位数的估计：med = median(medv) = 21.20。'));
children.push(answer('(f) 自助法估计中位数的标准误差：SE = 0.378。中位数没有简单的标准误差解析公式，自助法是有效手段。'));
children.push(answer('(g) medv第10%分位数的估计：μ̂₀.₁ = quantile(medv, 0.1) = 12.75。'));
children.push(answer('(h) 自助法估计第10%分位数的标准误差：SE = 0.477。相对中位数SE更大，因为分位数对数据尾部更敏感。'));
children.push(image('q9_自助分布.png', 5.2, 2.3));

const doc = new Document({
  styles: { default: { document: { run: { font: 'SimSun', size: 24 } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 }, // A4
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buffer => {
  const out = path.join(__dirname, '4-张鸿昊-第4次作业.docx');
  fs.writeFileSync(out, buffer);
  console.log('written', out, buffer.length, 'bytes');
});
