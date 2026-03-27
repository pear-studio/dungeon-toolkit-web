interface RobotCardSkeletonProps {
  count?: number
  layout?: 'grid' | 'list'
}

/**
 * 机器人卡片加载骨架
 */
export default function RobotCardSkeleton({ count = 3, layout = 'grid' }: RobotCardSkeletonProps) {
  const containerClass = layout === 'grid' 
    ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4'
    : 'space-y-4'

  return (
    <div className={containerClass}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="border border-gray-200 rounded-lg p-4 animate-pulse">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-gray-100 rounded-lg" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-100 rounded w-2/3" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}