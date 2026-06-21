<template>
  <div class="login-page">
    <!-- 装饰背景 -->
    <div class="bg-shapes">
      <div class="shape s1" />
      <div class="shape s2" />
      <div class="shape s3" />
    </div>

    <!-- 品牌区 -->
    <div class="brand">
      <div class="brand-logo">
        <el-icon :size="32"><OfficeBuilding /></el-icon>
      </div>
      <div class="brand-title">RBAC+WS系统</div>
      <div class="brand-sub">企业级综合管理平台</div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="card-header">管理端登录</div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
            size="large"
            class="login-input"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            show-password
            :prefix-icon="Lock"
            size="large"
            class="login-input"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            {{ loading ? '登录中…' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 底部 -->
    <div class="footer">Copyright &copy; 2024 RBAC+WS系统</div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, OfficeBuilding } from '@element-plus/icons-vue'
import request from '@/api/request'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const formRef = ref()

const form = reactive({
  username: '',
  password: '',
})

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

async function handleLogin() {
  try { await formRef.value?.validate() } catch { return }
  loading.value = true
  try {
    const { data } = await request.post('/api/v1/auth/admin/login', form)
    authStore.setToken(data.access_token, data.refresh_token)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {} finally { loading.value = false }
}
</script>

<style lang="less" scoped>
.login-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(155deg, #0f1a2e 0%, #1a3050 40%, #1e4a6e 70%, #1b5e8a 100%);
  position: relative;
  overflow: hidden;
}

/* 装饰图形 */
.bg-shapes {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; overflow: hidden;
}
.shape {
  position: absolute;
  border-radius: 50%;
}
.s1 {
  width: 460px; height: 460px;
  background: radial-gradient(circle, rgba(77,168,218,0.12), transparent);
  top: -120px; right: -160px;
}
.s2 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(108,192,240,0.1), transparent);
  bottom: 80px; left: -100px;
}
.s3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(143,211,244,0.08), transparent);
  top: 55%; right: -60px;
}

/* 品牌 */
.brand {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}
.brand-logo {
  width: 72px; height: 72px; border-radius: 18px;
  background: linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.06));
  border: 1px solid rgba(255,255,255,0.15);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 20px;
  backdrop-filter: blur(8px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.brand-title {
  font-size: 24px; font-weight: 700; color: #fff;
  letter-spacing: 4px; margin-bottom: 8px;
}
.brand-sub {
  font-size: 14px; color: rgba(255,255,255,0.55);
}

/* 卡片 */
.login-card {
  width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 32px 36px 36px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.25);
  position: relative;
  z-index: 1;
}
.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #1b5e8a;
  text-align: center;
  margin-bottom: 28px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 22px;
}
.login-form :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.login-input :deep(.el-input__wrapper) {
  background: #f5f7fa;
  border-radius: 8px;
  box-shadow: none;
  border: 1px solid #e4e7ed;
  transition: border-color 0.2s, background 0.2s;
}
.login-input :deep(.el-input__wrapper:hover) {
  border-color: #1b5e8a;
}
.login-input :deep(.el-input__wrapper.is-focus) {
  border-color: #1b5e8a;
  background: #fff;
  box-shadow: 0 0 0 1px rgba(27,94,138,0.15);
}

/* 渐变按钮 */
.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  letter-spacing: 6px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #1b5e8a 0%, #153e5c 100%);
  border: none;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(27,94,138,0.35);
  transition: opacity 0.2s;
  &:hover { opacity: 0.92; }
  &:active { opacity: 0.82; }
}
.login-btn.is-loading {
  opacity: 0.65;
}

/* 底部 */
.footer {
  position: absolute;
  bottom: 28px;
  font-size: 12px;
  color: rgba(255,255,255,0.25);
  z-index: 1;
}
</style>
