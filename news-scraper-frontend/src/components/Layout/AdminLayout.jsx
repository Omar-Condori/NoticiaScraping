import { Outlet, NavLink } from 'react-router-dom';
import { BarChart3, LogOut, Crown, Shield } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export default function AdminLayout() {
  const { user, logout } = useApp();

  const menuItems = [
    { path: '/admin', icon: BarChart3, label: 'Panel Admin', end: true },
  ];

  return (
    <div className="min-h-screen bg-light-bg dark:bg-dark-bg flex">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-light-card dark:bg-dark-card border-r border-light-border dark:border-dark-border flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-light-border dark:border-dark-border">
          <Shield className="w-8 h-8 text-yellow-400" />
          <span className="ml-3 text-xl font-bold text-white">Admin Panel</span>
        </div>

        {/* Menu */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-white shadow-lg'
                    : 'text-gray-400 hover:bg-light-hover dark:hover:bg-dark-hover hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* User Info */}
        <div className="p-4 border-t border-light-border dark:border-dark-border">
          <div className="flex items-center gap-3 mb-3 p-3 bg-yellow-500/10 rounded-lg">
            <div className="w-10 h-10 bg-yellow-500 rounded-full flex items-center justify-center">
              <Crown className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium text-sm truncate">
                {user?.nombre_usuario}
              </p>
              <p className="text-xs text-yellow-400 flex items-center gap-1">
                <Shield className="w-3 h-3" />
                Administrador
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors font-medium"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm">Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 flex-1 p-8">
        <Outlet />
      </main>
    </div>
  );
}