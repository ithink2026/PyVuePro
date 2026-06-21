<template>
  <div class="page">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" :model="query" class="search-form">
        <el-form-item label="部门名称">
          <el-input v-model="query.name" placeholder="请输入部门名称" clearable @keyup.enter="handleSearch" />
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
          <el-button type="primary" :icon="Plus" @click="showAdd">新增部门</el-button>
        </div>
      </template>
      <el-table :data="filteredTree" row-key="id" default-expand-all border stripe>
        <el-table-column prop="name" label="部门名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sort" label="排序" min-width="80" align="center" />
        <el-table-column label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="dark" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">{{ row.created_at?.split('.')[0]?.replace('T',' ') }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="180">
          <template #default="{ row }">
            <span class="op-btns">
            <el-button size="small" :icon="Edit" @click="showEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="handleDel(row)">删除</el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog :title="isEdit ? '编辑部门' : '新增部门'" v-model="dialogVisible" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-tree-select v-model="form.parent_id" :data="treeData" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="无（顶级部门）" clearable check-strictly />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" :max="9999" controls-position="right" />
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { departmentApi } from '@/api/modules/department'

const treeData = ref<any[]>([])
const query = ref({ name: '' })
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const formRef = ref()
const form = ref({ name: '', parent_id: null as number | null, sort: 0 })
const status = ref(true)

const rules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '部门名称长度在 2 到 50 个字符', trigger: 'blur' },
  ],
}

function filterTree(list: any[], keyword: string): any[] {
  if (!keyword) return list
  const kw = keyword.toLowerCase()
  return list.reduce((acc: any[], node: any) => {
    const match = node.name.toLowerCase().includes(kw)
    const children = node.children ? filterTree(node.children, kw) : []
    if (match || children.length) {
      acc.push({ ...node, children: children.length ? children : node.children || [] })
    }
    return acc
  }, [])
}

const filteredTree = computed(() => filterTree(treeData.value, query.value.name))

async function fetch() {
  try {
    const { data } = await departmentApi.getTree()
    treeData.value = data || []
  } catch {}
}

function handleSearch() {}
function handleReset() { query.value.name = '' }

function showAdd() {
  isEdit.value = false; form.value = { name: '', parent_id: null, sort: 0 }
  status.value = true; dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true; editId.value = row.id
  form.value = { name: row.name, parent_id: row.parent_id, sort: row.sort }
  status.value = row.status === 1; dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch { return }
  try {
    const payload = { ...form.value, status: status.value ? 1 : 0 }
    if (isEdit.value) {
      await departmentApi.update(editId.value, payload)
    } else {
      await departmentApi.create(payload)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false; fetch()
  } catch {}
}

async function handleDel(row: any) {
  await ElMessageBox.confirm(`确认删除部门「${row.name}」？`, '提示', { type: 'warning' })
  try {
    await departmentApi.remove(row.id)
    ElMessage.success('删除成功'); fetch()
  } catch {}
}

onMounted(fetch)
</script>