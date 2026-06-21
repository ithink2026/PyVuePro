<template>
  <div class="page">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" :model="query" class="search-form">
        <el-form-item label="角色名称">
          <el-input v-model="query.name" placeholder="请输入角色名称" clearable @keyup.enter="handleSearch" />
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
          <el-button type="primary" :icon="Plus" @click="showAdd">新增角色</el-button>
        </div>
      </template>
      <el-table :data="list" border stripe>
        <el-table-column prop="name" label="角色名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="code" label="角色编码" min-width="150" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="dark" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_system" label="系统角色" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_system" type="warning" effect="dark" size="small">系统</el-tag>
            <span v-else style="color:#909399">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="200">
          <template #default="{ row }">
            <span class="op-btns">
            <el-button size="small" :disabled="row.is_system && !authStore.isSuperAdmin" @click="showEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" :disabled="row.is_system" @click="handleDel(row)">删除</el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog :title="isEdit ? '编辑角色' : '新增角色'" v-model="dialogVisible" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" placeholder="如: operator" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="角色描述" />
        </el-form-item>
        <el-form-item label="菜单权限">
          <div class="perm-box">
            <el-tree
              ref="treeRef"
              :data="menuTree"
              show-checkbox
              node-key="id"
              :default-checked-keys="checkedKeys"
              default-expand-all
              :props="{ label: 'name', children: 'children' }"
              highlight-current
            />
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="status" active-text="启用" inactive-text="禁用" />
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
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { roleApi } from '@/api/modules/role'

const authStore = useAuthStore()

const list = ref<any[]>([])
const menuTree = ref<any[]>([])
const query = ref({ name: '' })
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const checkedKeys = ref<number[]>([])
const treeRef = ref()
const formRef = ref()
const form = ref({ name: '', code: '', description: '' })
const status = ref(true)

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '角色编码仅支持字母、数字和下划线，且以字母或下划线开头', trigger: 'blur' },
  ],
}

async function fetchList() {
  try {
    const params: any = {}
    if (query.value.name) params.name = query.value.name
    const { data } = await roleApi.getList(params)
    list.value = data || []
  } catch {}
}

async function fetchMenus() {
  try {
    const { data } = await roleApi.getAssignableMenus()
    menuTree.value = data || []
  } catch {}
}

function handleSearch() { fetchList() }
function handleReset() { query.value.name = ''; fetchList() }

function showAdd() {
  isEdit.value = false; form.value = { name: '', code: '', description: '' }
  status.value = true; checkedKeys.value = []
  dialogVisible.value = true
  nextTick(() => treeRef.value?.setCheckedKeys([]))
}

function showEdit(row: any) {
  isEdit.value = true; editId.value = row.id
  form.value = { name: row.name, code: row.code, description: row.description || '' }
  status.value = row.status === 1
  try { checkedKeys.value = JSON.parse(row.menu_ids || '[]') } catch { checkedKeys.value = [] }
  dialogVisible.value = true
  nextTick(() => treeRef.value?.setCheckedKeys(checkedKeys.value))
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch { return }
  try {
    const keys = treeRef.value?.getCheckedKeys() || []
    const halfKeys = treeRef.value?.getHalfCheckedKeys() || []
    const allKeys = [...keys, ...halfKeys]
    const payload = { ...form.value, menu_ids: JSON.stringify(allKeys), status: status.value ? 1 : 0 }
    if (isEdit.value) {
      await roleApi.update(editId.value, payload)
    } else {
      await roleApi.create(payload)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false; fetchList()
  } catch {}
}

async function handleDel(row: any) {
  if (row.is_system) { ElMessage.warning('系统角色不可删除'); return }
  await ElMessageBox.confirm(`确认删除角色「${row.name}」？`, '提示', { type: 'warning' })
  try {
    await roleApi.remove(row.id)
    ElMessage.success('删除成功'); fetchList()
  } catch {}
}

onMounted(() => { fetchList(); fetchMenus() })
</script>