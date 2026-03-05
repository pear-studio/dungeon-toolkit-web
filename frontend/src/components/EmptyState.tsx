import { Bot as BotIcon } from 'lucide-react'
import type { ReactNode } from 'react'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

/**
 * 空状态展示组件
 */
export default function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="text-center py-20">
      {icon || <BotIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" aria-hidden="true" />}
      <p className="text-gray-600 mb-2">{title}</p>
      {description && <p className="text-sm text-gray-500 mb-6">{description}</p>}
      {action}
    </div>
  )
}