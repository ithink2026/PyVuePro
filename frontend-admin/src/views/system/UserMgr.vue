<template>
  <div class="page">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" :model="query" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="query.username" placeholder="请输入用户名" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="main-card">
      <template #header>
        <div class="card-header">
          <el-button type="primary" :icon="Plus" @click="showAdd">新增用户</el-button>
        </div>
      </template>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" min-width="60" align="center" />
        <el-table-column prop="username" label="用户名" min-width="120" show-overflow-tooltip />
        <el-table-column prop="dept_name" label="部门" min-width="120" show-overflow-tooltip />
        <el-table-column prop="role_name" label="角色" min-width="120" show-overflow-tooltip />
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">{{ row.created_at?.split('.')[0]?.replace('T',' ') }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="280">
          <template #default="{ row }">
            <span class="op-btns">
            <el-button size="small" :icon="Edit" @click="showEdit(row)">编辑</el-button>
            <el-button size="small" :icon="RefreshRight" @click="handleResetPwd(row)">重置密码</el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="handleDel(row)">删除</el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog :title="isEdit ? '编辑用户' : '新增用户'" v-model="dialogVisible" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-tree-select v-model="form.dept_id" :data="depts" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择部门" clearable check-strictly />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_id" placeholder="选择角色" clearable>
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, RefreshRight, Search, Refresh } from '@element-plus/icons-vue'
import { userApi } from '@/api/modules/user'
import { departmentApi } from '@/api/modules/department'
import { roleApi } from '@/api/modules/role'

const list = ref<any[]>([])
const depts = ref<any[]>([])
const roles = ref<any[]>([])
const query = ref({ username: '' })
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const formRef = ref()
const form = ref({ username: '', password: '', dept_id: null as number | null, role_id: null as number | null })

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

async function fetchList() {
  loading.value = true
  try {
    const params: any = {}
    if (query.value.username) params.username = query.value.username
    const { data } = await userApi.getList(params)
    list.value = data || []
  } catch {} finally { loading.value = false }
}

async function fetchDict() {
  try {
    const [d, r] = await Promise.all([departmentApi.getTree(), roleApi.getList()])
    depts.value = d.data || []; roles.value = r.data || []
  } catch {}
}

function handleSearch() { fetchList() }
function handleReset() { query.value.username = ''; fetchList() }

function showAdd() {
  isEdit.value = false
  form.value = { username: '', password: '', dept_id: null, role_id: null }
  dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true; editId.value = row.id
  form.value = { username: row.username, password: '', dept_id: row.dept_id, role_id: row.role_id }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch { return }
  try {
    const payload: any = { ...form.value }
    if (!payload.password) delete payload.password
    if (isEdit.value) {
      await userApi.update(editId.value, payload)
    } else {
      await userApi.create(payload)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false; fetchList()
  } catch {}
}

async function handleResetPwd(row: any) {
  await ElMessageBox.confirm(`确认重置用户「${row.username}」的密码？新密码为「${row.username}123」`, '重置密码', { type: 'warning' })
  try {
    const { data } = await userApi.resetPassword(row.id)
    ElMessage.success(data.message || '密码已重置')
  } catch {}
}

async function handleDel(row: any) {
  await ElMessageBox.confirm(`确认删除用户「${row.username}」？`, '提示', { type: 'warning' })
  try {
    await userApi.remove(row.id)
    ElMessage.success('删除成功'); fetchList()
  } catch {}
}

onMounted(() => { fetchList(); fetchDict() })
</script>