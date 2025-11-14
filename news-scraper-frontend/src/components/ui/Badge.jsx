export default function Badge({ children, variant = 'default', className = '' }) {
  const variants = {
    default: 'bg-dark-hover text-gray-300',
    primary: 'bg-accent-primary/20 text-accent-primary',
    success: 'bg-accent-success/20 text-accent-success',
    warning: 'bg-accent-warning/20 text-accent-warning',
    danger: 'bg-accent-danger/20 text-accent-danger',
    error: 'bg-red-500/20 text-red-400', // Agregado para compatibilidad
    secondary: 'bg-accent-secondary/20 text-accent-secondary'
  };

  return (
    <span className={`
      inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium
      ${variants[variant]} ${className}
    `}>
      {children}
    </span>
  );
}