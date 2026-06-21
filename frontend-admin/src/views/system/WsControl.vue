<template>
  <div class="fc-page">
    <el-row :gutter="20">
      <!-- H5 是否存在 -->
      <el-col :span="12">
        <el-card shadow="hover" class="fc-card">
          <div class="fc-item">
            <div class="fc-left">
              <div class="fc-icon icon-h5"><el-icon :size="28"><Monitor /></el-icon></div>
              <div class="fc-info">
                <div class="fc-title">H5 是否存在</div>
                <div class="fc-desc">控制 H5 端模块可用性，关闭后客户管理菜单自动隐藏，WebSocket 强制关闭</div>
              </div>
            </div>
            <div class="fc-action">
              <el-tag :type="h5Enabled ? 'success' : 'danger'" effect="dark" size="small" class="status-tag">
                {{ h5Enabled ? '存在' : '不存在' }}
              </el-tag>
              <el-switch v-model="h5Enabled" :loading="h5Switching" @change="handleH5Toggle" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- WebSocket 长连接 -->
      <el-col :span="12">
        <el-card shadow="hover" class="fc-card">
          <div class="fc-item">
            <div class="fc-left">
              <div class="fc-icon icon-ws"><el-icon :size="28"><Connection /></el-icon></div>
              <div class="fc-info">
                <div class="fc-title">WebSocket 长连接</div>
                <div class="fc-desc">控制 H5 端长连接通信，关闭后 H5 心跳停止</div>
              </div>
            </div>
            <div class="fc-action">
              <el-tag :type="wsEnabled ? 'success' : 'danger'" effect="dark" size="small" class="status-tag">
                {{ wsEnabled ? '运行中' : '已关闭' }}
              </el-tag>
              <el-tooltip :content="wsDisabledTip" :disabled="!wsDisabled" placement="top">
                <el-switch v-model="wsEnabled" :loading="wsSwitching" :disabled="wsDisabled" @change="handleWsToggle" />
              </el-tooltip>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- H5 登录方式 -->
      <el-col :span="24">
        <el-card shadow="hover" class="fc-card fc-card-full">
          <div class="fc-item">
            <div class="fc-left">
              <div class="fc-icon icon-login"><el-icon :size="28"><Setting /></el-icon></div>
              <div class="fc-info">
                <div class="fc-title">H5 登录方式</div>
                <div class="fc-desc">
                  当前：
                  <el-tag :type="loginMode === 'ip' ? 'primary' : 'success'" effect="dark" size="small">
                    {{ loginMode === 'ip' ? 'IP 登录（自动识别用户身份，无需手动登录）' : '手机号登录（需注册/登录后使用）' }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="fc-action">
              <el-radio-group v-model="loginMode" :disabled="modeSwitching" @change="handleModeChange" size="large">
                <el-radio-button value="phone">手机号登录</el-radio-button>
                <el-radio-button value="ip">IP 登录</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, Monitor, Setting } from '@element-plus/icons-vue'
import { adminApi } from '@/api/modules/admin'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const h5Enabled = ref(true)
const h5Switching = ref(false)
const wsEnabled = ref(true)
const wsSwitching = ref(false)
const loginMode = ref<'ip' | 'phone'>('phone')
const modeSwitching = ref(false)

const wsDisabled = computed(() => !h5Enabled.value)
const wsDisabledTip = computed(() => !h5Enabled.value ? 'H5 未启用，请先开启「H5 是否存在」' : '')

async function load() {
  try {
    const [h5Res, wsRes, modeRes] = await Promise.all([
      adminApi.getH5Config(),
      adminApi.getWsConfig(),
      adminApi.getH5LoginConfig(),
    ])
    h5Enabled.value = h5Res.data.enabled
    wsEnabled.value = wsRes.data.enabled
    loginMode.value = modeRes.data.mode
  } catch {}
}

async function handleH5Toggle(val: boolean) {
  h5Switching.value = true
  try {
    const { data } = await adminApi.toggleH5(val)
    h5Enabled.value = data.enabled
    wsEnabled.value = data.ws_enabled
    ElMessage.success(val ? 'H5 端已启用' : 'H5 端已关闭，客户管理菜单已隐藏')
    authStore.refreshSidebar()
  } catch {
    h5Enabled.value = !val
  } finally { h5Switching.value = false }
}

async function handleWsToggle(val: boolean) {
  wsSwitching.value = true
  try {
    await adminApi.toggleWs(val)
    ElMessage.success(val ? 'WebSocket 已开启' : 'WebSocket 已关闭')
  } catch {
    wsEnabled.value = !val
  } finally { wsSwitching.value = false }
}

async function handleModeChange(val: 'ip' | 'phone') {
  modeSwitching.value = true
  try {
    await adminApi.toggleH5LoginMode(val)
    loginMode.value = val
    ElMessage.success(`H5 登录方式已切换为「${val === 'ip' ? 'IP 登录' : '手机号登录'}」`)
  } catch {
    loginMode.value = loginMode.value === 'ip' ? 'phone' : 'ip'
  } finally { modeSwitching.value = false }
}

onMounted(load)
</script>

<style lang="less" scoped>
.fc-page { width: 100%; }
.fc-card { border-radius: 6px; margin-bottom: 20px; }
.fc-card-full { margin-bottom: 0; }
.fc-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; }
.fc-left { display: flex; align-items: center; gap: 16px; }
.fc-icon {
  width: 56px; height: 56px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.icon-h5 { background: #fdf6ec; color: #e6a23c; }
.icon-ws { background: #ecf5ff; color: #409eff; }
.icon-login { background: #f0f9eb; color: #67c23a; }
.fc-title { font-size: 15px; font-weight: 600; color: #303133; margin-bottom: 4px; }
.fc-desc { font-size: 13px; color: #909399; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.fc-action { display: flex; align-items: center; gap: 12px; }
.status-tag { min-width: 56px; text-align: center; }
</style>
