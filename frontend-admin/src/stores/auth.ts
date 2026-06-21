import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '')
  const isSuperAdmin = ref<boolean>(false)
  const sidebarVersion = ref<number>(0)

  function setToken(access: string, refresh: string) {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function setAdminInfo(superAdmin: boolean) {
    isSuperAdmin.value = superAdmin
  }

  function refreshSidebar() {
    sidebarVersion.value++
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    isSuperAdmin.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  function isLoggedIn() {
    return !!token.value
  }

  return { token, refreshToken, isSuperAdmin, sidebarVersion, setToken, setAdminInfo, refreshSidebar, logout, isLoggedIn }
})
