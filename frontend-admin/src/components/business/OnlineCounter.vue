<template>
  <el-card class="online-counter">
    <template #header>
      <span>H5 端在线人数</span>
    </template>
    <div class="count">{{ count }}</div>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useWebSocket } from '@/hooks/useWebSocket'

const authStore = useAuthStore()
const { count, connect, disconnect } = useWebSocket()

onMounted(() => {
  connect(authStore.token)
})

onUnmounted(() => {
  disconnect()
})
</script>

<style lang="less" scoped>
.online-counter {
  width: 300px;
}
.count {
  font-size: 48px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
}
</style>