<template>
  <div>
    <div class="flex-header">
      <div class="page-title" style="margin:0">科室管理</div>
      <el-button type="primary" icon="Plus" @click="openDialog()">新增科室</el-button>
    </div>

    <el-card class="card-shadow" style="margin-top:16px">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="ID"     prop="dept_id"    width="70" />
        <el-table-column label="科室名称" prop="dept_name" width="130" />
        <el-table-column label="楼层"   prop="floor_no"   width="70" />
        <el-table-column label="在职医生" prop="doctor_count" width="90" />
        <el-table-column label="简介"   prop="description" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editRow ? '编辑科室' : '新增科室'" width="440px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="科室名称" prop="dept_name">
          <el-input v-model="form.dept_name" />
        </el-form-item>
        <el-form-item label="楼层">
          <el-input-number v-model="form.floor_no" :min="1" :max="30" />
        </el-form-item>
        <el-form-item label="科室简介">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { departmentApi } from '@/api/department'

const list    = ref([])
const loading = ref(false)
const saving  = ref(false)
const dialogVisible = ref(false)
const editRow = ref(null)
const formRef = ref(null)

const form = reactive({ dept_name: '', floor_no: 1, description: '' })
const rules = { dept_name: [{ required: true, message: '请输入科室名称', trigger: 'blur' }] }

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const res = await departmentApi.list()
  list.value = res.data
  loading.value = false
}

function openDialog(row = null) {
  editRow.value = row
  if (row) {
    Object.assign(form, { dept_name: row.dept_name, floor_no: row.floor_no, description: row.description || '' })
  } else {
    Object.assign(form, { dept_name: '', floor_no: 1, description: '' })
  }
  dialogVisible.value = true
}

async function handleSave() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editRow.value) {
      await departmentApi.update(editRow.value.dept_id, form)
    } else {
      await departmentApi.create(form)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchList()
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.flex-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
</style>
