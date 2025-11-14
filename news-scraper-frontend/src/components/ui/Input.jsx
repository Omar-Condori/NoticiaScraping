// Export por defecto para Input
export default function Input({ 
  label, 
  error, 
  className = '', 
  icon: Icon,
  ...props 
}) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-300">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2">
            <Icon className="w-5 h-5 text-gray-400" />
          </div>
        )}
        <input
          className={`
            w-full bg-dark-hover border border-dark-border rounded-lg 
            px-4 py-2.5 text-white placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary
            transition-all duration-200
            ${Icon ? 'pl-11' : ''}
            ${error ? 'border-accent-danger' : ''}
            ${className}
          `}
          {...props}
        />
      </div>
      {error && (
        <p className="text-sm text-accent-danger">{error}</p>
      )}
    </div>
  );
}

// Named exports adicionales para Select y Textarea
export function Select({ label, error, className = '', children, ...props }) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-300">
          {label}
        </label>
      )}
      <select
        className={`
          w-full bg-dark-hover border border-dark-border rounded-lg 
          px-4 py-2.5 text-white
          focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary
          transition-all duration-200
          ${error ? 'border-accent-danger' : ''}
          ${className}
        `}
        {...props}
      >
        {children}
      </select>
      {error && (
        <p className="text-sm text-accent-danger">{error}</p>
      )}
    </div>
  );
}

export function Textarea({ label, error, className = '', ...props }) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-300">
          {label}
        </label>
      )}
      <textarea
        className={`
          w-full bg-dark-hover border border-dark-border rounded-lg 
          px-4 py-2.5 text-white placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary
          transition-all duration-200 resize-none
          ${error ? 'border-accent-danger' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="text-sm text-accent-danger">{error}</p>
      )}
    </div>
  );
}