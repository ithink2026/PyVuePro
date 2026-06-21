<template>
  <div class="page">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" :model="query" class="search-form">
        <el-form-item label="菜单名称">
          <el-input v-model="query.name" placeholder="请输入菜单名称" clearable @keyup.enter="handleSearch" />
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
          <el-button type="primary" :icon="Plus" @click="showAdd(null)">新增根菜单</el-button>
        </div>
      </template>
      <el-table :data="filteredTree" row-key="id" default-expand-all border stripe>
        <el-table-column prop="name" label="菜单名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="类型" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="typeColor(row.type)" effect="dark" size="small">
              {{ { catalog: '目录', menu: '菜单', button: '按钮' }[row.type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" min-width="170" show-overflow-tooltip />
        <el-table-column prop="permission" label="权限标识" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sort" label="排序" min-width="80" align="center" />
        <el-table-column label="操作" fixed="right" min-width="280">
          <template #default="{ row }">
            <span class="op-btns">
            <el-button size="small" v-if="row.type !== 'button'" :icon="Plus" @click="showAdd(row)">子项</el-button>
            <el-button size="small" :icon="Edit" @click="showEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="handleDel(row)">删除</el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog :title="isEdit ? '编辑菜单' : '新增菜单'" v-model="dialogVisible" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="菜单名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type">
            <el-option label="目录" value="catalog" />
            <el-option label="菜单" value="menu" />
            <el-option label="按钮" value="button" />
          </el-select>
        </el-form-item>
        <el-form-item label="路径" v-if="form.type === 'menu'" prop="path">
          <el-input v-model="form.path" placeholder="/path" />
        </el-form-item>
        <el-form-item label="组件" v-if="form.type === 'menu'">
          <el-input v-model="form.component" placeholder="ComponentName" />
        </el-form-item>
        <el-form-item label="权限标识" v-if="form.type === 'button'" prop="permission">
          <el-input v-model="form.permission" placeholder="如: system:user:add" />
        </el-form-item>
        <el-form-item label="图标" v-if="form.type !== 'button'">
          <IconPicker v-model="form.icon" />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" :max="9999" controls-position="right" />
        </el-form-item>
        <el-form-item label="可见">
          <el-switch v-model="visible" />
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
import { menuApi } from '@/api/modules/menu'
import IconPicker from '@/components/business/IconPicker.vue'

const treeData = ref<any[]>([])
const query = ref({ name: '' })
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const formRef = ref()
const form = ref({ name: '', type: 'menu', path: '', component: '', permission: '', icon: '', sort: 0 })
const visible = ref(true)

const typeColor = (type: string) => type === 'catalog' ? 'primary' : type === 'menu' ? 'success' : 'warning'

const rules = {
  name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
    { min: 2, max: 50, message: '菜单名称长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  path: [
    { required: true, message: '请输入路径', trigger: 'blur' },
    { pattern: /^\//, message: '路径必须以 / 开头', trigger: 'blur' },
  ],
  permission: [
    { required: true, message: '请输入权限标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_:]*$/, message: '权限标识格式不正确', trigger: 'blur' },
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
    const { data } = await menuApi.getTree()
    treeData.value = data || []
  } catch {}
}

function handleSearch() {}
function handleReset() { query.value.name = '' }

function showAdd(parent: any) {
  isEdit.value = false
  form.value = { name: '', type: 'menu', path: '', component: '', permission: '', icon: '', sort: 0 }
  if (parent) (form.value as any)._parent_id = parent.id
  visible.value = true; dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true; editId.value = row.id
  form.value = { name: row.name, type: row.type, path: row.path || '', component: row.component || '', permission: row.permission || '', icon: row.icon || '', sort: row.sort }
  visible.value = row.visible === 1; dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch { return }
  const payload: any = { ...form.value, visible: visible.value ? 1 : 0, status: 1 }
  if (payload._parent_id) { payload.parent_id = payload._parent_id; delete payload._parent_id }
  try {
    if (isEdit.value) {
      await menuApi.update(editId.value, payload)
    } else {
      await menuApi.create(payload)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false; fetch()
  } catch {}
}

async function handleDel(row: any) {
  await ElMessageBox.confirm(`确认删除菜单「${row.name}」？`, '提示', { type: 'warning' })
  try {
    await menuApi.remove(row.id)
    ElMessage.success('删除成功'); fetch()
  } catch {}
}

onMounted(fetch)
</script>