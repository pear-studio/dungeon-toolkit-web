import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

type ConnectionStatus = 'idle' | 'connecting' | 'open' | 'closed' | 'error'

export interface WsEventMessage {
  v?: number
  type: 'ack' | 'bot_message' | 'system'
  ack_id?: string
  status?: 'ok' | 'error'
  error?: string | null
  content?: string
  timestamp?: string
  correlation_id?: string
  code?: string
}

interface UseWebSocketResult {
  status: ConnectionStatus
  error: string
  isKicked: boolean
  sendJson: (payload: Record<string, unknown>) => boolean
}

function buildWsUrl(botId: string, token: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.host
  const encodedToken = encodeURIComponent(token)
  return `${protocol}://${host}/ws/chat/${botId}/?token=${encodedToken}`
}

export function useWebSocket(
  botId: string | null,
  onMessage: (message: WsEventMessage) => void
): UseWebSocketResult {
  const socketRef = useRef<WebSocket | null>(null)
  const shouldReconnectRef = useRef(true)
  const reconnectTimerRef = useRef<number | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const onMessageRef = useRef(onMessage)
  const [runtimeStatus, setRuntimeStatus] = useState<ConnectionStatus>('idle')
  const [runtimeError, setRuntimeError] = useState('')
  const [isKicked, setIsKicked] = useState(false)
  const token = localStorage.getItem('access_token')

  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  const clearReconnectTimer = useCallback(() => {
    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current)
      reconnectTimerRef.current = null
    }
  }, [])

  const closeSocket = useCallback(() => {
    const socket = socketRef.current
    socketRef.current = null
    if (socket) {
      socket.close()
    }
  }, [])

  useEffect(() => {
    if (!botId || !token) {
      return
    }

    let isMounted = true
    shouldReconnectRef.current = true
    reconnectAttemptsRef.current = 0

    const connect = () => {
      if (!isMounted) return
      setRuntimeStatus('connecting')
      setRuntimeError('')

      const ws = new WebSocket(buildWsUrl(botId, token))
      socketRef.current = ws

      ws.onopen = () => {
        if (!isMounted) return
        reconnectAttemptsRef.current = 0
        setIsKicked(false)
        setRuntimeStatus('open')
      }

      ws.onmessage = (event) => {
        if (!isMounted) return
        try {
          const message = JSON.parse(event.data) as WsEventMessage
          if (message.type === 'system' && message.code === 'FORCE_DISCONNECT') {
            setIsKicked(true)
            shouldReconnectRef.current = false
          }
          onMessageRef.current(message)
        } catch {
          setRuntimeError('收到无法识别的消息')
        }
      }

      ws.onerror = () => {
        if (!isMounted) return
        setRuntimeStatus('error')
        setRuntimeError('连接出现异常')
      }

      ws.onclose = (event) => {
        if (!isMounted) return
        setRuntimeStatus('closed')
        if (event.code === 4001) {
          setIsKicked(true)
          setRuntimeError('聊天已在其他窗口打开，请前往新窗口继续')
          return
        }
        if (!shouldReconnectRef.current) {
          return
        }
        const attempts = reconnectAttemptsRef.current
        if (attempts >= 3) {
          setRuntimeStatus('error')
          setRuntimeError('连接已断开，请稍后重试')
          return
        }
        reconnectAttemptsRef.current += 1
        const backoff = 800 * reconnectAttemptsRef.current
        reconnectTimerRef.current = window.setTimeout(connect, backoff)
      }
    }

    connect()

    return () => {
      isMounted = false
      shouldReconnectRef.current = false
      clearReconnectTimer()
      closeSocket()
    }
  }, [botId, token, clearReconnectTimer, closeSocket])

  const sendJson = useCallback((payload: Record<string, unknown>) => {
    const socket = socketRef.current
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return false
    }
    socket.send(JSON.stringify(payload))
    return true
  }, [])

  const status: ConnectionStatus = !botId ? 'idle' : token ? runtimeStatus : 'error'
  const error = !botId ? '' : token ? runtimeError : '请先登录后再使用聊天'

  return useMemo(
    () => ({
      status,
      error,
      isKicked,
      sendJson,
    }),
    [status, error, isKicked, sendJson]
  )
}
