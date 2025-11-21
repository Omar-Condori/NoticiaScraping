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
  LogOut,
  User,
  Sun,
  Moon,
  Shield,
  Crown, // <--- AGREGADO
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import ChatBotWidget from '../ChatBotWidget';

const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Noticias', path: '/noticias', icon: Newspaper },
  { name: 'Fuentes', path: '/fuentes', icon: Globe },
  { name: 'Scheduler', path: '/scheduler', icon: Clock },
  { name: 'Estadísticas', path: '/estadisticas', icon: BarChart3 },
  { name: 'Búsqueda', path: '/busqueda', icon: Search },
  { name: 'Planes', path: '/planes', icon: Crown }, // <--- AGREGADO
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useApp();
  const { theme, toggleTheme } = useTheme();
  const isAdmin = user?.rol === 'admin';

  return (
    <div className="min-h-screen bg-light-bg dark:bg-dark-bg">
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
          fixed top-0 left-0 z-40 h-screen w-64 bg-light-card dark:bg-dark-card border-r border-light-border dark:border-dark-border
          transition-transform duration-300 lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-light-border dark:border-dark-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center rounded-lg">
              <Newspaper className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-semibold text-white">ScrapingNews</span>
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
                  ${isActive
                    ? 'bg-gradient-to-r from-accent-primary to-accent-secondary text-white shadow-lg'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-light-hover dark:hover:bg-dark-hover hover:text-gray-900 dark:hover:text-white'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Info del usuario y botón de logout */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-light-border dark:border-dark-border">
          <div className="bg-light-hover dark:bg-dark-hover rounded-lg p-3">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-accent-primary to-accent-secondary rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-white truncate">
                    {user?.nombre_usuario || 'Usuario'}
                  </p>
                  {isAdmin && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-accent-primary/20 text-accent-primary text-xs font-medium rounded-full">
                      <Shield className="w-3 h-3" />
                      Admin
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-400 truncate">
                  {user?.email || ''}
                </p>
                {user?.rol && !isAdmin && (
                  <p className="text-xs text-gray-500 truncate">
                    Rol: {user.rol}
                  </p>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={toggleTheme}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-light-card dark:bg-dark-card hover:bg-light-hover dark:hover:bg-dark-hover text-gray-700 dark:text-gray-300 rounded-lg transition-colors border border-light-border dark:border-dark-border"
                title={theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
              >
                {theme === 'dark' ? (
                  <>
                    <Sun className="w-4 h-4" />
                    <span className="text-sm font-medium">Claro</span>
                  </>
                ) : (
                  <>
                    <Moon className="w-4 h-4" />
                    <span className="text-sm font-medium">Oscuro</span>
                  </>
                )}
              </button>
              <button
                onClick={logout}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span className="text-sm font-medium">Salir</span>
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <header className="h-16 bg-light-card dark:bg-dark-card border-b border-light-border dark:border-dark-border sticky top-0 z-30 backdrop-blur-sm">
          <div className="h-full px-4 flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-light-hover dark:hover:bg-dark-hover text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <Menu className="w-6 h-6" />
            </button>

            <div className="flex items-center gap-3 ml-auto">
              {/* Botón de tema */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg hover:bg-light-hover dark:hover:bg-dark-hover text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                title={theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
              >
                {theme === 'dark' ? (
                  <Sun className="w-5 h-5" />
                ) : (
                  <Moon className="w-5 h-5" />
                )}
              </button>

              {/* Info del usuario */}
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-light-hover dark:bg-dark-hover rounded-lg">
                <div className="w-8 h-8 bg-gradient-to-br from-accent-primary to-accent-secondary rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-white">
                      {user?.nombre_usuario || 'Usuario'}
                    </span>
                    {isAdmin && (
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-accent-primary/20 text-accent-primary text-xs font-medium rounded">
                        <Shield className="w-3 h-3" />
                        Admin
                      </span>
                    )}
                  </div>
                  {user?.rol && !isAdmin && (
                    <span className="text-xs text-gray-500">Rol: {user.rol}</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>

      {/* Chatbot Widget Flotante */}
      <ChatBotWidget />
    </div>
  );
}