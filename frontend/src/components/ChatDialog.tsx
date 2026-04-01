import { useEffect, useMemo, useRef, useState } from 'react'
import { MessageCircle, Send, X } from 'lucide-react'

import { botApi, type Bot } from '../lib/api'
import { ALERT, BUTTON, CARD, INPUT, TEXT } from '../lib/constants'
import { cn } from '../lib/utils'
import { useAuthStore } from '../stores/authStore'
import { type WsEventMessage, useWebSocket } from '../hooks/useWebSocket'

interface ChatDialogProps {
  bot: Bot
  onClose: () => void
}

interface LocalMessage {
  id: string
  type: 'outbound' | 'bot' | 'system'
  content: string
  timestamp: string
  ackId?: string
  ackError?: string
}

function normalizeContent(content: string): string {
  if (/\[CQ:[^\]]+\]/.test(content)) {
    return '[CQ 消息占位]'
  }
  return content
}

export default function ChatDialog({ bot, onClose }: ChatDialogProps) {
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState<LocalMessage[]>([])
  const [latestError, setLatestError] = useState('')
  const [freshBotStatus, setFreshBotStatus] = useState<Bot['status'] | null>(null)
  const lastSystemRef = useRef<{ content: string; time: number } | null>(null)
  const messageListRef = useRef<HTMLDivElement | null>(null)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  const shouldShowSystem = (content: string) => {
    const now = Date.now()
    const last = lastSystemRef.current
    if (last && last.content === content && now - last.time < 15000) {
      return false
    }
    lastSystemRef.current = { content, time: now }
    return true
  }

  const handleMessage = (message: WsEventMessage) => {
    if (message.type === 'system') {
      const content = message.content || '系统消息'
      if (!shouldShowSystem(content)) {
        return
      }
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          type: 'system',
          content,
          timestamp: new Date().toISOString(),
        },
      ])
      return
    }

    if (message.type === 'bot_message') {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          type: 'bot',
          content: normalizeContent(message.content || ''),
          timestamp: message.timestamp || new Date().toISOString(),
          ackId: message.correlation_id,
        },
      ])
      return
    }

    if (message.type === 'ack' && message.ack_id && message.status === 'error') {
      const nextError = message.error || '消息发送失败'
      setLatestError(nextError)
      setMessages((prev) =>
        prev.map((item) =>
          item.ackId === message.ack_id
            ? {
                ...item,
                ackError: nextError,
              }
            : item
        )
      )
    }
  }

  const { status, error: wsError, isKicked, sendJson } = useWebSocket(bot.id, handleMessage)

  useEffect(() => {
    if (status !== 'open') return

    let cancelled = false
    const refreshBotStatus = async () => {
      try {
        const res = await botApi.get(bot.id)
        if (!cancelled) {
          setFreshBotStatus(res.data.status)
        }
      } catch {
        // Keep last known bot status when refresh fails.
      }
    }
    void refreshBotStatus()

    return () => {
      cancelled = true
    }
  }, [status, bot.id])

  const botStatus = freshBotStatus ?? bot.status

  const canChat = isAuthenticated && status === 'open' && botStatus === 'online' && !isKicked
  const inputPlaceholder = useMemo(() => {
    if (!isAuthenticated) return '请先登录后再使用聊天'
    if (isKicked) return '聊天已在其他窗口打开，请手动恢复'
    if (status !== 'open') return '连接中，暂不可发送'
    if (botStatus !== 'online') return '机器人离线，暂不可发送'
    return '输入消息...'
  }, [isAuthenticated, isKicked, status, botStatus])

  const handleSend = () => {
    if (!canChat) return
    const content = draft.trim()
    if (!content) return

    const ackId = crypto.randomUUID()
    const sent = sendJson({
      v: 1,
      type: 'message',
      content,
      ack_id: ackId,
    })

    if (!sent) {
      setLatestError('连接未就绪，消息发送失败')
      return
    }

    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        type: 'outbound',
        content,
        timestamp: new Date().toISOString(),
        ackId,
      },
    ])
    setDraft('')
    setLatestError('')
  }

  useEffect(() => {
    const container = messageListRef.current
    if (!container) return
    container.scrollTop = container.scrollHeight
  }, [messages])

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center px-4">
      <div className={cn(CARD.base, 'w-full max-w-2xl h-[80vh] flex flex-col')}>
        <div className="flex items-center justify-between border-b border-gray-200 pb-4">
          <div className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-blue-600" aria-hidden="true" />
            <div>
              <h2 className={TEXT.h3}>{bot.nickname}</h2>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className={cn(BUTTON.base, BUTTON.ghost, BUTTON.sm)}
            aria-label="关闭聊天窗口"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        {(latestError || wsError || isKicked) && (
          <div className={cn(ALERT.error, 'mt-3')} role="alert">
            {latestError || wsError || '聊天已在其他窗口打开，请前往新窗口继续'}
          </div>
        )}

        <div ref={messageListRef} className="flex-1 overflow-y-auto mt-4 space-y-3">
          {messages.length === 0 && <p className={TEXT.bodySmall}>发送消息开始对话。</p>}

          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'max-w-[80%] rounded-lg px-3 py-2',
                message.type === 'outbound' && 'ml-auto bg-blue-50 border border-blue-200',
                message.type === 'bot' && 'bg-gray-50 border border-gray-200',
                message.type === 'system' && 'bg-yellow-50 border border-yellow-200 max-w-full'
              )}
            >
              <p className={TEXT.bodySmall}>{message.content}</p>
              {message.ackError && <p className={TEXT.error}>{message.ackError}</p>}
            </div>
          ))}
        </div>

        <div className="mt-4 border-t border-gray-200 pt-4 flex gap-2">
          {/*
            Keep input state aligned with send button: when socket is not ready,
            both should be disabled to avoid misleading editable state.
          */}
          <input
            type="text"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder={inputPlaceholder}
            className={cn(INPUT.base, 'flex-1')}
            disabled={!canChat}
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={!canChat || !draft.trim()}
            className={cn(BUTTON.base, BUTTON.primary, BUTTON.md)}
          >
            <Send className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  )
}
