export default function Skeleton({ className = '', variant = 'default' }) {
  const variants = {
    default: 'h-4 w-full',
    title: 'h-8 w-3/4',
    text: 'h-4 w-full',
    circle: 'h-12 w-12 rounded-full',
    card: 'h-48 w-full'
  };

  return (
    <div className={`
      ${variants[variant]} ${className}
      bg-dark-hover rounded animate-pulse
    `} />
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-dark-card border border-dark-border rounded-xl p-6">
      <Skeleton variant="title" className="mb-4" />
      <Skeleton variant="text" className="mb-2" />
      <Skeleton variant="text" className="w-4/5 mb-2" />
      <Skeleton variant="text" className="w-2/3" />
    </div>
  );
}

export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <Skeleton className="w-1/4" />
          <Skeleton className="w-2/4" />
          <Skeleton className="w-1/4" />
        </div>
      ))}
    </div>
  );
}