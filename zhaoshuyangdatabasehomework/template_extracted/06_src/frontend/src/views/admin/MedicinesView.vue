<template>
  <div>
    <div class="flex-header">
      <div class="page-title" style="margin:0">药品管理</div>
      <el-button type="primary" icon="Plus" @click="openAddDialog">新增药品</el-button>
    </div>

    <!-- 搜索 -->
    <el-card class="card-shadow" style="margin:12px 0">
      <el-form inline>
        <el-form-item label="药品名称">
          <el-input v-model="keyword" placeholder="模糊搜索" clearable style="width:180px"
            @keyup.enter="fetchList" />
        </el-form-item>
        <el-form-item label="仅显示有库存">
          <el-switch v-model="inStock" @change="fetchList" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="fetchList">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="card-shadow">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="药品名称" prop="medicine_name" min-width="140" />
        <el-table-column label="规格"     prop="specification"  width="140" />
        <el-table-column label="单位"     prop="unit"           width="70" />
        <el-table-column label="单价"     width="90">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column label="分类"     prop="category"       width="100" />
        <el-table-column label="库存" width="100">
          <template #default="{ row }">
            <el-tag :type="row.stock > 0 ? 'success' : 'danger'">{{ row.stock }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openStockDialog(row)">调整库存</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination layout="prev,pager,next" :total="total" :page-size="pageSize"
        v-model:current-page="page" @current-change="fetchList"
        style="margin-top:14px;justify-content:flex-end;display:flex" />
    </el-card>

    <!-- 新增药品弹窗 -->
    <el-dialog v-model="addVisible" title="新增药品" width="460px">
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="90px">
        <el-form-item label="药品名称" prop="medicine_name">
          <el-input v-model="addForm.medicine_name" />
        </el-form-item>
        <el-form-item label="规格">
          <el-input v-model="addForm.specification" placeholder="如 500mg×24粒，留空填''" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="addForm.unit" placeholder="盒/瓶/支/片" />
        </el-form-item>
        <el-form-item label="单价" prop="price">
          <el-input-number v-model="addForm.price" :min="0" :precision="2" :step="0.1" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="addForm.stock" :min="0" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="addForm.category" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="addSaving" @click="handleAdd">添加</el-button>
      </template>
    </el-dialog>

    <!-- 调整库存弹窗 -->
    <el-dialog v-model="stockVisible" :title="`调整库存 - ${stockRow?.medicine_name}`" width="360px">
      <el-form label-width="80px">
        <el-form-item label="当前库存">{{ stockRow?.stock }}</el-form-item>
        <el-form-item label="新库存">
          <el-input-number v-model="newStock" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockVisible = false">取消</el-button>
        <el-button type="primary" :loading="stockSaving" @click="handleStock">更新</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { medicineApi } from '@/api/medicine'

const list     = ref([])
const loading  = ref(false)
const keyword  = ref('')
const inStock  = ref(false)
const page     = ref(1)
const pageSize = ref(20)
const total    = ref(0)

const addVisible = ref(false)
const addFormRef = ref(null)
const addSaving  = ref(false)
const addForm    = reactive({ medicine_name: '', specification: '', unit: '', price: 0, stock: 0, category: '' })
const addRules   = {
  medicine_name: [{ required: true, message: '请输入药品名称', trigger: 'blur' }],
  unit:          [{ required: true, message: '请输入计量单位', trigger: 'blur' }],
  price:         [{ required: true, message: '请输入单价',     trigger: 'blur' }],
}

const stockVisible = ref(false)
const stockSaving  = ref(false)
const stockRow     = ref(null)
const newStock     = ref(0)

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const params = { page: page.value, page_size: pageSize.value }
  if (keyword.value) params.keyword  = keyword.value
  if (inStock.value) params.in_stock = true
  const res = await medicineApi.list(params)
  list.value  = res.data.list
  total.value = res.data.total
  loading.value = false
}

function openAddDialog() {
  Object.assign(addForm, { medicine_name: '', specification: '', unit: '', price: 0, stock: 0, category: '' })
  addVisible.value = true
}

async function handleAdd() {
  await addFormRef.value?.validate()
  addSaving.value = true
  try {
    await medicineApi.create(addForm)
    ElMessage.success('药品添加成功')
    addVisible.value = false
    fetchList()
  } finally {
    addSaving.value = false
  }
}

function openStockDialog(row) {
  stockRow.value = row
  newStock.value = row.stock
  stockVisible.value = true
}

async function handleStock() {
  stockSaving.value = true
  try {
    await medicineApi.updateStock(stockRow.value.medicine_id, { stock: newStock.value })
    ElMessage.success('库存更新成功')
    stockVisible.value = false
    fetchList()
  } finally {
    stockSaving.value = false
  }
}
</script>

<style scoped>
.flex-header { display: flex; align-items: center; justify-content: space-between; }
</style>
