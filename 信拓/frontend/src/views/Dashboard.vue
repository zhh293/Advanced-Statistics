<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value" :style="{ color: card.color }">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>事故原因分布</template>
          <div ref="reasonChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>涉事车辆类型</template>
          <div ref="vehicleChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>24小时事故分布</template>
          <div ref="hourChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>高发地点 TOP10</template>
          <div ref="locationChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>时段 × 原因交叉分析</template>
          <div ref="crossChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>关键词词云</template>
          <div ref="wordcloudChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { getSummary, getHourly, getReasonPeriodCross, getWordcloud } from '../api'

const statCards = ref([
  { label: '事故总数', value: 0, color: '#E6A23C' },
  { label: '涉及城市', value: 0, color: '#409EFF' },
  { label: '数据来源', value: 0, color: '#67C23A' },
  { label: '最新数据', value: '-', color: '#909399' },
])

const reasonChart = ref(null)
const vehicleChart = ref(null)
const hourChart = ref(null)
const locationChart = ref(null)
const crossChart = ref(null)
const wordcloudChart = ref(null)

let charts = []

onMounted(async () => {
  await loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
})

function handleResize() {
  charts.forEach(c => c.resize())
}

async function loadData() {
  try {
    const [summary, hourly, cross, wordcloudData] = await Promise.all([
      getSummary(),
      getHourly(),
      getReasonPeriodCross(),
      getWordcloud(),
    ])

    // 更新卡片
    statCards.value = [
      { label: '事故总数', value: summary.total_accidents, color: '#E6A23C' },
      { label: '涉及城市', value: summary.total_locations, color: '#409EFF' },
      { label: '数据来源', value: summary.total_sources, color: '#67C23A' },
      { label: '最新数据', value: summary.latest_time?.slice(0, 10) || '-', color: '#909399' },
    ]

    // 事故原因饼图
    const rChart = echarts.init(reasonChart.value)
    rChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        itemStyle: { borderRadius: 8 },
        data: summary.reason_distribution,
        label: { formatter: '{b}\n{d}%' },
      }],
    })
    charts.push(rChart)

    // 车辆类型玫瑰图
    const vChart = echarts.init(vehicleChart.value)
    vChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: ['30%', '70%'], roseType: 'area',
        itemStyle: { borderRadius: 8 },
        data: summary.vehicle_distribution,
      }],
    })
    charts.push(vChart)

    // 24小时分布
    const hChart = echarts.init(hourChart.value)
    hChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: hourly.map(d => d.x + '时') },
      yAxis: { type: 'value' },
      series: [{
        type: 'line', data: hourly.map(d => d.y),
        smooth: true, areaStyle: { color: 'rgba(64,158,255,0.3)' },
        lineStyle: { color: '#409EFF' },
      }],
    })
    charts.push(hChart)

    // 高发地点
    const lChart = echarts.init(locationChart.value)
    lChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: summary.top_locations.map(d => d.name).reverse(),
        axisLabel: { fontSize: 11 } },
      series: [{
        type: 'bar', data: summary.top_locations.map(d => d.value).reverse(),
        itemStyle: { color: '#E6A23C', borderRadius: [0, 4, 4, 0] },
      }],
    })
    charts.push(lChart)

    // 交叉分析
    const cChart = echarts.init(crossChart.value)
    const colors = ['#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEAA7','#DDA0DD','#98D8C8']
    cChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: cross.reasons, top: 5 },
      xAxis: { type: 'category', data: cross.periods },
      yAxis: { type: 'value' },
      color: colors,
      series: cross.reasons.map((r, i) => ({
        name: r, type: 'bar', stack: 'total',
        emphasis: { focus: 'series' },
        data: cross.data.map(row => row[i]),
      })),
    })
    charts.push(cChart)

    // 词云图
    if (wordcloudData && wordcloudData.length > 0) {
      const wChart = echarts.init(wordcloudChart.value)
      wChart.setOption({
        tooltip: { show: true, formatter: (p) => `${p.name}: ${p.value}` },
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          sizeRange: [14, 60],
          rotationRange: [-45, 45],
          rotationStep: 15,
          gridSize: 8,
          drawOutOfBound: false,
          textStyle: {
            fontFamily: 'Microsoft YaHei',
            color: () => {
              const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
                '#4ECDC4', '#45B7D1', '#FF6B6B', '#DDA0DD', '#96CEB4']
              return colors[Math.floor(Math.random() * colors.length)]
            },
          },
          data: wordcloudData.map(d => ({ name: d.name, value: d.value })),
        }],
      })
      charts.push(wChart)
    }

  } catch (e) {
    console.error('加载看板数据失败', e)
  }
}
</script>

<style scoped>
.stat-row { margin-bottom: 16px; }
.stat-card { text-align: center; }
.stat-label { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; }
</style>
