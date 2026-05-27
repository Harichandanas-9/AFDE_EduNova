export default function LoadingSkeleton({ rows = 3, className = '' }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton h-4 w-full" style={{ width: `${85 + Math.random() * 15}%` }} />
      ))}
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="glass p-6 space-y-3">
      <div className="skeleton h-5 w-2/3" />
      <div className="skeleton h-3 w-full" />
      <div className="skeleton h-3 w-4/5" />
      <div className="skeleton h-3 w-3/5" />
    </div>
  )
}
