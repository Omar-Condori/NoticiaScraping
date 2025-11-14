import { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { useApp } from "../../context/AppContext";
import {
  LayoutDashboard,
  Newspaper,
  Globe,
  Clock,
  BarChart3,
  Search,
  Menu,
  LogOut, // ← NUEVO
  User, // ← NUEVO
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Noticias', path: '/noticias', icon: Newspaper },
  { name: 'Fuentes', path: '/fuentes', icon: Globe },
  { name: 'Scheduler', path: '/scheduler', icon: Clock },
  { name: 'Estadísticas', path: '/estadisticas', icon: BarChart3 },
  { name: 'Búsqueda', path: '/busqueda', icon: Search },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useApp();// ← NUEVO: Obtener info del usuario

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Sidebar Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-40 h-screen w-64 bg-dark-card border-r border-dark-border
          transition-transform duration-300 lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center rounded-lg">
              <Newspaper className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-semibold text-white">NewsAPI</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                  ${
                    isActive
                      ? 'bg-gradient-to-r from-accent-primary to-accent-secondary text-white shadow-lg'
                      : 'text-gray-400 hover:bg-dark-hover hover:text-white'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* ← NUEVO: Info del usuario y botón de logout */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-border">
          <div className="bg-dark-hover rounded-lg p-3">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-accent-primary to-accent-secondary rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.nombre_usuario || 'Usuario'}
                </p>
                <p className="text-xs text-gray-400 truncate">
                  {user?.email || ''}
                </p>
              </div>
            </div>
            <button
              onClick={logout}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm font-medium">Cerrar Sesión</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <header className="h-16 bg-dark-card border-b border-dark-border sticky top-0 z-30 backdrop-blur-sm">
          <div className="h-full px-4 flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-dark-hover text-gray-400 hover:text-white transition-colors"
            >
              <Menu className="w-6 h-6" />
            </button>

            {/* ← MODIFICADO: Mostrar usuario en mobile también */}
            <div className="flex items-center gap-4 ml-auto">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-dark-hover rounded-lg">
                <div className="w-8 h-8 bg-gradient-to-br from-accent-primary to-accent-secondary rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <span className="text-sm font-medium text-white">
                  {user?.nombre_usuario || 'Usuario'}
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}