import { Bot as BotIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import { TEXT } from '../lib/constants'
import { cn } from '../lib/utils'

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
      <p className={cn(TEXT.body, "mb-2")}>{title}</p>
      {description && <p className={cn(TEXT.caption, "mb-6")}>{description}</p>}
      {action}
    </div>
  )
}