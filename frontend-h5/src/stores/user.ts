import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const refreshToken = ref('')

  // 从 storage 初始化
  try {
    token.value = uni.getStorageSync('access_token') || ''
    refreshToken.value = uni.getStorageSync('refresh_token') || ''
  } catch {}

  function setToken(access: string, refresh: string) {
    token.value = access
    refreshToken.value = refresh
    try { uni.setStorageSync('access_token', access) } catch {}
    try { uni.setStorageSync('refresh_token', refresh) } catch {}
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    try { uni.removeStorageSync('access_token') } catch {}
    try { uni.removeStorageSync('refresh_token') } catch {}
  }

  return { token, refreshToken, setToken, logout }
})