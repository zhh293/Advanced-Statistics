<template>
  <div class="sankey-page">
    <el-card shadow="never">
      <template #header>特征流向分析：时段 → 事故原因 → 车辆类型</template>
      <div v-loading="loading" style="height: 600px;">
        <div ref="chartRef" style="height: 100%;"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getSankey } from '../api'

const chartRef = ref(null)
const loading = ref(false)
let chart = null

function handleResize() {
  chart?.resize()
}

onMounted(async () => {
  loading.value = true
  try {
    chart = echarts.init(chartRef.value)
    const data = await getSankey()

    chart.setOption({
      tooltip: { trigger: 'item', triggerOn: 'mousemove' },
      series: [{
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        nodeAlign: 'left',
        data: data.nodes,
        links: data.links,
        lineStyle: { color: 'gradient', curveness: 0.5 },
        label: { fontSize: 12 },
      }],
    })

    window.addEventListener('resize', handleResize)
  } catch (e) {
    console.error('加载桑基图失败', e)
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>
