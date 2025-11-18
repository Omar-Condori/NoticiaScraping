import { Navigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { user, loading } = useApp();

  // Mostrar loading mientras se verifica la autenticación
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-bg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary mx-auto"></div>
          <p className="mt-4 text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  // Si no hay usuario, redirigir a login
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Si requiere admin y el usuario NO es admin → redirigir a home
  if (requireAdmin && user.rol !== 'admin') {
    return <Navigate to="/" replace />;
  }

  // Si el usuario ES admin y está intentando acceder a rutas normales → redirigir a /admin
  if (!requireAdmin && user.rol === 'admin') {
    return <Navigate to="/admin" replace />;
  }

  // Todo OK, mostrar el componente
  return children;
};

export default ProtectedRoute;
