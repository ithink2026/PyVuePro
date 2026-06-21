<template>
  <div class="page">
    <!-- 在线人数统计卡片 -->
    <el-card shadow="hover" class="online-card">
      <div class="online-wrap">
        <div class="online-icon"><el-icon :size="40"><Monitor /></el-icon></div>
        <div class="online-body">
          <div class="online-label">在线人数</div>
          <div class="online-num">{{ onlineCount }}</div>
        </div>
      </div>
    </el-card>

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
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" min-width="60" align="center" />
        <el-table-column prop="username" label="用户名" min-width="120" show-overflow-tooltip />
        <el-table-column prop="name" label="姓名" min-width="100" show-overflow-tooltip />
        <el-table-column prop="id_card" label="身份证号" min-width="180" show-overflow-tooltip />
        <el-table-column prop="phone" label="手机号" min-width="130" show-overflow-tooltip />
        <el-table-column prop="bank_card" label="银行卡号" min-width="190" show-overflow-tooltip />
        <el-table-column prop="bank_card_name" label="银行卡名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="bank_card_balance" label="银行卡余额" min-width="130" align="right">
          <template #default="{ row }">
            {{ row.bank_card_balance != null ? '¥' + Number(row.bank_card_balance).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">{{ row.created_at?.split('.')[0]?.replace('T',' ') }}</template>
        </el-table-column>
         <el-table-column label="状态" min-width="90" fixed="right" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              :loading="switchingId === row.id"
              @change="(val: boolean) => handleToggle(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="120">
          <template #default="{ row }">
            <el-button size="small" :icon="RefreshRight" @click="handleResetPwd(row)">重置密码</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RefreshRight, Search, Refresh, Monitor } from '@element-plus/icons-vue'
import { h5UserApi } from '@/api/modules/h5User'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useAuthStore } from '@/stores/auth'

const list = ref<any[]>([])
const query = ref({ username: '' })
const loading = ref(false)
const switchingId = ref(0)

const authStore = useAuthStore()
const { count: onlineCount, connect: wsConnect, disconnect: wsDisconnect } = useWebSocket()

async function fetchList() {
  loading.value = true
  try {
    const params: any = {}
    if (query.value.username) params.username = query.value.username
    const { data } = await h5UserApi.getList(params)
    list.value = data || []
  } catch {} finally { loading.value = false }
}

function handleSearch() { fetchList() }
function handleReset() { query.value.username = ''; fetchList() }

async function handleToggle(row: any, val: boolean) {
  switchingId.value = row.id
  try {
    const { data } = await h5UserApi.toggleStatus(row.id, val)
    row.is_active = data.is_active
    ElMessage.success(data.message)
  } catch {
    // 失败回滚开关状态（仅视觉回滚，element-plus switch v-model 不绑定 row.is_active）
  } finally { switchingId.value = 0 }
}

async function handleResetPwd(row: any) {
  await ElMessageBox.confirm(`确认重置用户「${row.username}」的密码？新密码为「${row.username}123」`, '重置密码', { type: 'warning' })
  try {
    const { data } = await h5UserApi.resetPassword(row.id)
    ElMessage.success(data.message || '密码已重置')
  } catch {}
}

onMounted(() => {
  fetchList()
  if (authStore.token) {
    wsConnect(authStore.token)
  }
})

onBeforeUnmount(() => {
  wsDisconnect()
})
</script>

<style lang="less" scoped>
.online-card {
  border-radius: 6px;
  margin-bottom: 16px;
  max-width: 360px;
}
.online-wrap {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px 0;
}
.online-icon {
  width: 72px;
  height: 72px;
  border-radius: 6px;
  background: #ecf5ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.online-label {
  font-size: 14px;
  color: #909399;
}
.online-num {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  margin-top: 4px;
}
</style>
