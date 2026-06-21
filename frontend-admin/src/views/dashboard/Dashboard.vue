<template>
  <div class="dashboard">
    <el-card shadow="hover" class="welcome-card">
      <template #header><div class="card-header"><el-icon :size="18"><HomeFilled /></el-icon><span>欢迎</span></div></template>
      <p>欢迎使用 RBAC+WS 管理后台，通过左侧菜单栏进行各项管理操作。</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { HomeFilled } from '@element-plus/icons-vue'
</script>

<style lang="less" scoped>
.dashboard { width: 100%; max-width: 800px; }
.welcome-card { border-radius: 6px; }
.welcome-card p { color: #909399; margin-top: 8px; font-size: 14px; }
.card-header { display: flex; align-items: center; gap: 8px; font-weight: 600; }
</style>
