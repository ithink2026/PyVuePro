import { ref } from 'vue'

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let reconnectDelay = 1000
const MAX_RECONNECT_DELAY = 30000
let heartbeatTimer: ReturnType<typeof setInterval> | null = null

export function useWebSocket() {
  const connected = ref(false)

  function connect(token: string) {
    if (ws) {
      ws.onclose = null
      ws.close()
      ws = null
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/admin`

    ws = new WebSocket(url)

    ws.onopen = () => {
      connected.value = true
      reconnectDelay = 1000
      ws!.send(JSON.stringify({ type: 'auth', token }))
      startHeartbeat()
    }

    ws.onmessage = () => {
      // 预留消息处理
    }

    ws.onclose = () => {
      connected.value = false
      stopHeartbeat()
      scheduleReconnect(token)
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    stopHeartbeat()
    if (ws) {
      ws.onclose = null
      ws.close()
      ws = null
    }
    connected.value = false
  }

  return { connected, connect, disconnect }
}

function startHeartbeat() {
  heartbeatTimer = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
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
    const { connect } = useWebSocket()
    connect(token)
  }, reconnectDelay)
}