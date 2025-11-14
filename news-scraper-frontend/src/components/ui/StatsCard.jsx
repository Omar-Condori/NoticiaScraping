// Componente Card base para estadísticas
export function Card({ children, className = '', hover = false }) {
  return (
    <div className={`
      bg-dark-card border border-dark-border rounded-xl p-6
      ${hover ? 'hover:border-accent-primary/50 transition-all duration-300' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
}

// Header del Card
export function CardHeader({ children, className = '' }) {
  return (
    <div className={`mb-4 ${className}`}>
      {children}
    </div>
  );
}

// Título del Card
export function CardTitle({ children, className = '' }) {
  return (
    <h3 className={`text-lg font-semibold text-white ${className}`}>
      {children}
    </h3>
  );
}

// Descripción del Card
export function CardDescription({ children, className = '' }) {
  return (
    <p className={`text-sm text-gray-400 mt-1 ${className}`}>
      {children}
    </p>
  );
}

// Contenido del Card
export function CardContent({ children, className = '' }) {
  return (
    <div className={className}>
      {children}
    </div>
  );
}