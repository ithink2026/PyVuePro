import { ref } from 'vue'

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let reconnectDelay = 1000
const MAX_RECONNECT_DELAY = 30000
let heartbeatTimer: ReturnType<typeof setInterval> | null = null

export function useWebSocket() {
  const count = ref(0)

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
      reconnectDelay = 1000
      ws!.send(JSON.stringify({ type: 'auth', token }))
      startHeartbeat()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'online_count') {
          count.value = data.count
        }
      } catch {}
    }

    ws.onclose = () => {
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
  }

  return { count, connect, disconnect }
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