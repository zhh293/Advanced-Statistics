<template>
  <div class="heatmap-page">
    <el-card shadow="never">
      <template #header>
        <span>事故地点热力分布图</span>
        <span style="color: #909399; font-size: 13px; margin-left: 12px;">
          气泡大小代表事故数量，支持滚轮缩放和拖拽
        </span>
      </template>
      <div v-loading="loading" style="height: 650px;">
        <div ref="chartRef" style="height: 100%;"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getHeatmap } from '../api'

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

    // 加载中国地图 GeoJSON
    const geoResp = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    const geo = await geoResp.json()
    echarts.registerMap('china', geo)

    const heatData = await getHeatmap()

    chart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: (p) => `${p.name}<br/>案例数：${p.value[2]}`,
      },
      geo: {
        map: 'china',
        roam: true,
        zoom: 1.2,
        center: [115, 32],
        itemStyle: { areaColor: '#f3f3f3', borderColor: '#ccc' },
        emphasis: { itemStyle: { areaColor: '#e0e0e0' } },
      },
      series: [{
        type: 'scatter',
        coordinateSystem: 'geo',
        data: heatData,
        symbolSize: (val) => Math.sqrt(val[2]) * 4,
        itemStyle: { color: '#dd4b39' },
        label: { show: true, formatter: '{b}', position: 'right', fontSize: 11 },
        emphasis: { itemStyle: { color: '#ff6b6b' } },
      }],
    })

    window.addEventListener('resize', handleResize)
  } catch (e) {
    console.error('加载热力图失败', e)
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>
