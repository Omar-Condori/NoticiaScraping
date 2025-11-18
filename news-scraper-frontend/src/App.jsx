import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import AdminLayout from './components/Layout/AdminLayout';
import { AppProvider } from './context/AppContext';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import Noticias from './pages/Noticias';
import Fuentes from './pages/Fuentes';
import Estadisticas from './pages/Estadisticas';
import Busqueda from './pages/Busqueda';
import Scheduler from './pages/Scheduler';
import Planes from './pages/Planes';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AppProvider>
          <Routes>
            {/* ==================== RUTAS PÚBLICAS ==================== */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* ==================== RUTAS DE ADMINISTRADOR ==================== */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<AdminDashboard />} />
            </Route>

            {/* ==================== RUTAS DE USUARIO ==================== */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="noticias" element={<Noticias />} />
              <Route path="fuentes" element={<Fuentes />} />
              <Route path="estadisticas" element={<Estadisticas />} />
              <Route path="busqueda" element={<Busqueda />} />
              <Route path="scheduler" element={<Scheduler />} />
              <Route path="planes" element={<Planes />} />
            </Route>

            {/* ==================== RUTA 404 ==================== */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;