import { useUserStore } from '@/stores/user'

let socketTask: UniApp.SocketTask | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let reconnectDelay = 1000
const MAX_RECONNECT_DELAY = 30000
let heartbeatTimer: ReturnType<typeof setInterval> | null = null

export function connectWebSocket(token: string) {
  if (socketTask) {
    try { socketTask.close() } catch {}
    socketTask = null
  }

  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = location.host
  const url = `${protocol}//${host}/ws/h5`

  socketTask = uni.connectSocket({ url, success: () => {} })

  socketTask.onOpen(() => {
    reconnectDelay = 1000
    socketTask!.send({ data: JSON.stringify({ type: 'auth', token }) })
    startHeartbeat()
  })

  socketTask.onMessage((res) => {
    try {
      const data = JSON.parse(res.data as string)
      if (data.type === 'pong') return
      if (data.type === 'kicked') {
        uni.showToast({ title: '账号已在其他设备登录', icon: 'none' })
        const userStore = useUserStore()
        userStore.logout()
      }
    } catch {}
  })

  socketTask.onClose(() => {
    stopHeartbeat()
    scheduleReconnect(token)
  })

  socketTask.onError(() => {
    socketTask?.close()
  })
}

function startHeartbeat() {
  heartbeatTimer = setInterval(() => {
    if (socketTask) {
      socketTask.send({ data: JSON.stringify({ type: 'ping' }) })
    }
  }, 30000)
}

function stopHeartbeat() {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

function scheduleReconnect(token: string) {
  if (reconnectTimer) return
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY)
    connectWebSocket(token)
  }, reconnectDelay)
}

export function disconnectWebSocket() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  stopHeartbeat()
  if (socketTask) {
    socketTask.close()
    socketTask = null
  }
}