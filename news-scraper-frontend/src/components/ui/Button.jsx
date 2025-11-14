import { Loader2 } from 'lucide-react';

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  loading = false,
  disabled = false,
  className = '',
  icon: Icon,
  ...props 
}) {
  const baseStyles = 'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-accent-primary hover:bg-accent-primary/90 text-white shadow-lg shadow-accent-primary/20',
    secondary: 'bg-light-card dark:bg-dark-card hover:bg-light-hover dark:hover:bg-dark-hover text-gray-700 dark:text-gray-200 border border-light-border dark:border-dark-border',
    success: 'bg-accent-success hover:bg-accent-success/90 text-white',
    danger: 'bg-accent-danger hover:bg-accent-danger/90 text-white',
    ghost: 'hover:bg-light-hover dark:hover:bg-dark-hover text-gray-700 dark:text-gray-300',
    error: 'bg-red-500 hover:bg-red-600 text-white' // Agregado para compatibilidad
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : Icon ? (
        <Icon className="w-4 h-4" />
      ) : null}
      {children}
    </button>
  );
}