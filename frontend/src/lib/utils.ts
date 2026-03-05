import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * 合并 Tailwind CSS 类名的工具函数
 * 
 * 功能：
 * 1. 支持条件类名（来自 clsx）
 * 2. 智能合并冲突的 Tailwind 类（来自 tailwind-merge）
 * 
 * @example
 * cn('px-2 py-1', 'px-4')           // => 'py-1 px-4'（px-4 覆盖 px-2）
 * cn('text-red-500', isActive && 'text-blue-500')  // 条件类名
 * cn({ 'bg-red-500': isError })     // 对象语法
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}