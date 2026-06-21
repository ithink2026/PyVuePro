<template>
  <el-container class="layout">
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar">
      <div class="logo" v-show="!collapsed">RBAC+WS系统</div>
      <div class="logo logo-mini" v-show="collapsed">补</div>
      <el-menu
        :default-active="currentPath"
        :collapse="collapsed"
        router
        background-color="#fff"
        text-color="#606266"
        active-text-color="#1b5e8a"
      >
        <template v-for="item in menuTree" :key="item.id">
          <el-sub-menu v-if="item.children && item.children.length" :index="String(item.id)">
            <template #title>
              <el-icon><component :is="iconMap[item.icon] || Setting" /></el-icon>
              <span>{{ item.name }}</span>
            </template>
            <el-menu-item v-for="child in item.children" :key="child.id" :index="child.path">
              <el-icon><component :is="iconMap[child.icon]" /></el-icon>
              <span>{{ child.name }}</span>
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :index="item.path">
            <el-icon><component :is="iconMap[item.icon] || Setting" /></el-icon>
            <span>{{ item.name }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div class="topbar-left">
          <el-icon class="collapse-btn" :size="20" @click="collapsed = !collapsed">
            <Fold v-if="!collapsed" /><Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path ? { path: item.path } : undefined">
              {{ item.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <el-dropdown trigger="hover" @command="handleCommand" popper-class="user-dropdown-popper">
            <span class="user-info" style="outline:none">
              <span class="avatar-circle">{{ avatarChar }}</span>
              <span class="user-name">{{ username }}</span>
              <span class="user-role">{{ roleName }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <div class="dd-header">
                    <span class="avatar-circle dd-avatar">{{ avatarChar }}</span>
                    <div>
                      <div class="dd-name">{{ username }}</div>
                      <div class="dd-role">{{ roleName }}{{ isSuperAdmin ? ' (超管)' : '' }}</div>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item divided command="changePwd">
                  <el-icon><Lock /></el-icon>修改密码
                </el-dropdown-item>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="420px" destroy-on-close>
      <el-form :model="pwdForm" label-width="80px" :rules="pwdRules" ref="pwdFormRef">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="handleChangePwd" class="gradient-btn">确定</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  HomeFilled, Setting, Switch, Fold, Expand, Monitor,
  User, UserFilled, Menu, List, Key, Avatar, OfficeBuilding,
  ArrowDown, Lock, SwitchButton,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { adminApi } from '@/api/modules/admin'
import { menuApi } from '@/api/modules/menu'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const collapsed = ref(false)
const username = ref('')
const isSuperAdmin = ref(false)
const roleName = ref('')
const menuTree = ref<any[]>([])

const pwdDialogVisible = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref()
const pwdForm = reactive({ old_password: '', new_password: '', confirm: '' })

const validateConfirm = (_rule: any, value: string, callback: any) => {
  if (value !== pwdForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少6位', trigger: 'blur' },
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

const iconMap: Record<string, any> = {
  HomeFilled, Setting, Switch, Monitor, User, UserFilled, Menu, List, Key, Avatar, OfficeBuilding,
}

const currentPath = computed(() => route.path)
const avatarChar = computed(() => username.value.charAt(0).toUpperCase())

const breadcrumbs = computed(() => {
  const path = route.path
  if (path === '/dashboard') return []
  const crumbs: { name: string; path: string }[] = []
  for (const item of menuTree.value) {
    if (item.children) {
      for (const child of item.children) {
        if (child.path === path) {
          if (item.path) crumbs.push({ name: item.name, path: item.path })
          crumbs.push({ name: child.name, path: child.path })
          return crumbs
        }
      }
    }
    if (item.path === path) {
      crumbs.push({ name: item.name, path: item.path })
      return crumbs
    }
  }
  return crumbs
})

async function loadUserInfo() {
  try {
    const { data } = await adminApi.getUserInfo()
    username.value = data.username
    isSuperAdmin.value = data.is_super_admin
    authStore.setAdminInfo(data.is_super_admin)
    roleName.value = data.role_name || (data.is_super_admin ? '超级管理员' : '')
  } catch {}
}

async function loadMenus() {
  try {
    const { data } = await menuApi.getSidebar()
    menuTree.value = data
  } catch {}
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (cmd === 'changePwd') {
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm = ''
    pwdDialogVisible.value = true
  }
}

async function handleChangePwd() {
  try {
    await pwdFormRef.value?.validate()
  } catch {
    return
  }
  pwdLoading.value = true
  try {
    await adminApi.changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    })
    ElMessage.success('密码修改成功')
    pwdDialogVisible.value = false
  } catch { /* 错误由拦截器统一处理 */ }
  finally { pwdLoading.value = false }
}

onMounted(() => { loadUserInfo(); loadMenus() })

watch(() => authStore.sidebarVersion, () => { loadMenus() })
watch(() => route.path, () => { loadMenus() })
</script>

<style lang="less" scoped>
.layout { height: 100vh; margin: 0; padding: 0; overflow: hidden; }
.layout > .el-container { flex: 1; min-width: 0; }
.sidebar {
  background: #fff !important;
  transition: width 0.3s; overflow-x: hidden;
  border-right: 1px solid #e8eaed;
}
.logo {
  height: 64px; line-height: 64px; text-align: center;
  color: #1b5e8a; font-size: 17px; font-weight: 700;
  border-bottom: 1px solid #e8eaed; letter-spacing: 2px;
}
.logo-mini { font-size: 22px; letter-spacing: 0; }
.topbar {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; box-shadow: 0 1px 6px rgba(27,94,138,0.08);
  padding: 0 20px; z-index: 10; height: 56px;
}
.topbar-left { display: flex; align-items: center; gap: 16px; }
.collapse-btn { cursor: pointer; color: #666; }
.collapse-btn:hover { color: #1b5e8a; }
.topbar-right { display: flex; align-items: center; }
.user-info {
  display: flex; align-items: center; gap: 8px;
  cursor: pointer; padding: 4px 12px; border-radius: 4px;
  transition: background 0.2s;
}
.user-info:hover { background: #f5f7fa; }
.avatar-circle {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, #1b5e8a, #153e5c);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600; flex-shrink: 0;
}
.user-name { font-size: 14px; color: #333; font-weight: 500; }
.user-role { font-size: 12px; color: #909399; }
.arrow { color: #999; font-size: 12px; }
.main { background: #f0f4fa; padding: 24px; overflow-y: auto; flex: 1; min-width: 0; }
.el-menu { border-right: none; }
.el-menu-item.is-active {
  background: linear-gradient(135deg, #e8f2fa, #d4e6f5) !important;
  border-right: 3px solid #1b5e8a;
  color: #1b5e8a !important;
}
:deep(.el-sub-menu__title:hover) { background: #f5f7fa !important; }
:deep(.el-menu-item:hover) { background: #f5f7fa !important; }

.dd-header { display: flex; align-items: center; gap: 10px; }
.dd-avatar { width: 40px; height: 40px; font-size: 16px; }
.dd-name { font-size: 15px; font-weight: 600; color: #303133; }
.dd-role { font-size: 12px; color: #909399; }

/* 渐变主按钮 */
.gradient-btn.el-button--primary {
  background: linear-gradient(135deg, #1b5e8a, #153e5c);
  border: none;
  box-shadow: 0 2px 8px rgba(27,94,138,0.3);
}
.gradient-btn.el-button--primary:hover {
  opacity: 0.92;
}
.gradient-btn.el-button--primary.is-loading {
  opacity: 0.65;
}
</style>

<style lang="less">
/* 移除 el-dropdown 内部触发器的焦点黑框 */
.el-dropdown .el-tooltip__trigger {
  outline: none !important;
  border: none !important;
}
</style>