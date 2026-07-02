<template>
  <div class="mining-page">
    <!-- 参数控制 -->
    <el-card shadow="never" class="param-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="4">
          <span class="param-label">最小支持度</span>
          <el-slider v-model="params.min_support" :min="0.01" :max="0.3" :step="0.01" show-input />
        </el-col>
        <el-col :span="4">
          <span class="param-label">最小置信度</span>
          <el-slider v-model="params.min_confidence" :min="0.3" :max="0.95" :step="0.05" show-input />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="run" :loading="running">
            <el-icon><Search /></el-icon> 执行挖掘
          </el-button>
        </el-col>
        <el-col :span="8" v-if="latestParams">
          <span style="color: #909399; font-size: 13px;">
            上次挖掘参数：支持度={{ latestParams.params?.split(',')[0] }},
            置信度={{ latestParams.params?.split(',')[1] }}
          </span>
        </el-col>
        <el-col :span="4">
          <el-input v-model="keyword" placeholder="过滤规则" clearable @input="loadRules">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
      </el-row>
    </el-card>

    <!-- 规则列表 -->
    <el-card shadow="never" style="margin-top: 12px;">
      <template #header>
        关联规则列表
        <span style="color: #909399; font-size: 13px;">（共 {{ total }} 条，按提升度降序）</span>
      </template>

      <el-table :data="rules" stripe v-loading="loading" max-height="500">
        <el-table-column label="前件 (如果)" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="a in parseItems(row.antecedents)" :key="a" size="small" style="margin: 2px;">
              {{ a }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="→" width="50" align="center">
          <span style="font-size: 18px; color: #409EFF;">→</span>
        </el-table-column>
        <el-table-column label="后件 (则)" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="c in parseItems(row.consequents)" :key="c" size="small" type="success" style="margin: 2px;">
              {{ c }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="support" label="支持度" width="90" align="center">
          <template #default="{ row }">{{ (row.support * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" width="90" align="center">
          <template #default="{ row }">{{ (row.confidence * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="lift" label="提升度" width="90" align="center" sortable>
          <template #default="{ row }">
            <el-tag :type="row.lift > 1.5 ? 'danger' : row.lift > 1 ? 'warning' : ''" size="small">
              {{ row.lift.toFixed(2) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 规则解读 -->
    <el-card shadow="never" style="margin-top: 12px;" v-if="rules.length > 0">
      <template #header>📖 规则解读（Top 3）</template>
      <div v-for="(r, i) in rules.slice(0, 3)" :key="i" style="margin-bottom: 12px;">
        <el-alert type="info" :closable="false">
          <template #title>
            <strong>规则{{ i + 1 }}：</strong>
            当出现「{{ r.antecedents }}」时，有 <strong>{{ (r.confidence * 100).toFixed(0) }}%</strong>
            的概率同时出现「{{ r.consequents }}」。
            该组合的出现频率是随机情况的 <strong>{{ r.lift.toFixed(1) }}倍</strong>
            {{ r.lift > 1.5 ? '，属于强关联规则，具有显著参考价值。' : '。' }}
          </template>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { runMining, getRules, getLatestParams } from '../api'

const params = reactive({ min_support: 0.05, min_confidence: 0.6 })
const rules = ref([])
const total = ref(0)
const loading = ref(false)
const running = ref(false)
const keyword = ref('')
const latestParams = ref(null)

onMounted(async () => {
  latestParams.value = await getLatestParams()
  await loadRules()
})

async function run() {
  running.value = true
  try {
    const res = await runMining({ ...params })
    latestParams.value = { params: `${params.min_support},${params.min_confidence}` }
    await loadRules()
  } finally {
    running.value = false
  }
}

async function loadRules() {
  loading.value = true
  try {
    const q = { sort_by: 'lift', limit: 50 }
    if (keyword.value) q.keyword = keyword.value
    const res = await getRules(q)
    rules.value = res
    total.value = res.length
  } finally {
    loading.value = false
  }
}

function parseItems(str) {
  if (!str) return []
  return str.split(',').map(s => s.trim())
}
</script>

<style scoped>
.param-card :deep(.el-card__body) { padding: 16px 20px; }
.param-label { font-size: 13px; color: #606266; margin-bottom: 4px; display: block; }
</style>
