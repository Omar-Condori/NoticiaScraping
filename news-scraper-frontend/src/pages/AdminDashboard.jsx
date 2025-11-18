import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import StatsCard from '../components/admin/StatsCard';
import UserTable from '../components/admin/UserTable';
import PaymentTable from '../components/admin/PaymentTable';
import RevenueChart from '../components/admin/RevenueChart';
import api from '../services/api';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // ✅ Inicializar con valores por defecto para evitar undefined
  const [resumen, setResumen] = useState({
    usuarios: { total: 0, activos: 0, semana: 0 },
    ingresos: { total: 0, mes_actual: 0 },
    suscripciones: { activas: 0 },
    pagos: { pendientes: 0 }
  });
  
  const [distribucion, setDistribucion] = useState([]);
  const [ingresos, setIngresos] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [pagosRecientes, setPagosRecientes] = useState([]);
  const [pagosPendientes, setPagosPendientes] = useState([]);
  const [vistaActual, setVistaActual] = useState('general');

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      setError(null);

      // Verificar que sea admin
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.rol !== 'admin') {
        navigate('/');
        return;
      }

      // Cargar todos los datos en paralelo
      const [
        resumenRes,
        distribucionRes,
        ingresosRes,
        usuariosRes,
        pagosRecientesRes,
        pagosPendientesRes
      ] = await Promise.all([
        api.admin.obtenerResumen(),
        api.admin.obtenerUsuariosPorPlan(),
        api.admin.obtenerIngresosMensuales(),
        api.admin.obtenerUsuariosRecientes(),
        api.admin.obtenerPagosRecientes(),
        api.admin.obtenerPagosPendientes()
      ]);

      // ✅ Validar que los datos existan antes de setear
      if (resumenRes?.data?.resumen) {
        setResumen(resumenRes.data.resumen);
      }
      
      setDistribucion(distribucionRes?.data?.distribucion || []);
      setIngresos(ingresosRes?.data?.ingresos || []);
      setUsuarios(usuariosRes?.data?.usuarios || []);
      setPagosRecientes(pagosRecientesRes?.data?.pagos || []);
      setPagosPendientes(pagosPendientesRes?.data?.pagos || []);

    } catch (error) {
      console.error('Error cargando datos admin:', error);
      setError(error.message || 'Error al cargar datos');
      
      if (error.response?.status === 403) {
        alert('No tienes permisos de administrador');
        navigate('/');
      }
    } finally {
      setLoading(false);
    }
  };

  const aprobarPago = async (pagoId) => {
    if (!window.confirm('¿Estás seguro de aprobar este pago?')) return;

    try {
      await api.admin.aprobarPago(pagoId);
      alert('✅ Pago aprobado exitosamente');
      cargarDatos();
    } catch (error) {
      console.error('Error aprobando pago:', error);
      alert('❌ Error al aprobar el pago');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-accent-primary mx-auto"></div>
          <p className="mt-4 text-gray-400">Cargando panel de administración...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-white mb-2">Error al cargar datos</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          <button
            onClick={cargarDatos}
            className="px-6 py-2 bg-accent-primary text-white rounded-lg hover:bg-accent-secondary transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Panel de Administración</h1>
        <p className="text-gray-400 mt-1">Sistema de Scraping de Noticias</p>
      </div>

      {/* Navegación de pestañas */}
      <div className="bg-dark-card border-b border-dark-border rounded-t-xl">
        <nav className="flex space-x-8 px-6">
          <button
            onClick={() => setVistaActual('general')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              vistaActual === 'general'
                ? 'border-accent-primary text-accent-primary'
                : 'border-transparent text-gray-400 hover:text-white hover:border-gray-600'
            }`}
          >
            📊 General
          </button>
          <button
            onClick={() => setVistaActual('usuarios')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              vistaActual === 'usuarios'
                ? 'border-accent-primary text-accent-primary'
                : 'border-transparent text-gray-400 hover:text-white hover:border-gray-600'
            }`}
          >
            👥 Usuarios
          </button>
          <button
            onClick={() => setVistaActual('pagos')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              vistaActual === 'pagos'
                ? 'border-accent-primary text-accent-primary'
                : 'border-transparent text-gray-400 hover:text-white hover:border-gray-600'
            }`}
          >
            💳 Pagos
            {pagosPendientes.length > 0 && (
              <span className="ml-2 bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
                {pagosPendientes.length}
              </span>
            )}
          </button>
        </nav>
      </div>

      {/* Contenido principal */}
      <div>
        {/* Vista General */}
        {vistaActual === 'general' && (
          <div className="space-y-6">
            {/* Tarjetas de estadísticas */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatsCard
                title="Total Usuarios"
                value={resumen?.usuarios?.total || 0}
                icon="👥"
                subtitle={`${resumen?.usuarios?.activos || 0} activos`}
                color="blue"
              />
              <StatsCard
                title="Ingresos Totales"
                value={`S/ ${(resumen?.ingresos?.total || 0).toFixed(2)}`}
                icon="💰"
                subtitle={`S/ ${(resumen?.ingresos?.mes_actual || 0).toFixed(2)} este mes`}
                color="green"
              />
              <StatsCard
                title="Suscripciones Activas"
                value={resumen?.suscripciones?.activas || 0}
                icon="⭐"
                subtitle="Planes pagos"
                color="purple"
              />
              <StatsCard
                title="Pagos Pendientes"
                value={resumen?.pagos?.pendientes || 0}
                icon="⏳"
                subtitle="Requieren verificación"
                color="orange"
              />
            </div>

            {/* Distribución por planes */}
            {distribucion.length > 0 && (
              <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">
                  📦 Distribución de Usuarios por Plan
                </h3>
                <div className="space-y-4">
                  {distribucion.map((item, index) => (
                    <div key={index}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-300">
                          {item.plan}
                        </span>
                        <span className="text-sm font-semibold text-white">
                          {item.total_usuarios} usuarios
                        </span>
                      </div>
                      <div className="w-full bg-dark-hover rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            item.plan.includes('Anual') ? 'bg-purple-500' :
                            item.plan.includes('Mensual') ? 'bg-blue-500' :
                            'bg-gray-500'
                          }`}
                          style={{
                            width: `${((item.total_usuarios / (resumen?.usuarios?.total || 1)) * 100)}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Gráfico de ingresos */}
            {ingresos.length > 0 && <RevenueChart ingresos={ingresos} />}

            {/* Últimos usuarios */}
            {usuarios.length > 0 && <UserTable usuarios={usuarios.slice(0, 5)} />}
          </div>
        )}

        {/* Vista Usuarios */}
        {vistaActual === 'usuarios' && (
          <div className="space-y-6">
            <div className="bg-dark-card border border-dark-border rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-4">
                👥 Gestión de Usuarios
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-500/10 border border-blue-500/30 p-4 rounded-lg">
                  <p className="text-sm text-blue-400 font-medium">Total Usuarios</p>
                  <p className="text-2xl font-bold text-blue-300">{resumen?.usuarios?.total || 0}</p>
                </div>
                <div className="bg-green-500/10 border border-green-500/30 p-4 rounded-lg">
                  <p className="text-sm text-green-400 font-medium">Usuarios Activos</p>
                  <p className="text-2xl font-bold text-green-300">{resumen?.usuarios?.activos || 0}</p>
                </div>
                <div className="bg-purple-500/10 border border-purple-500/30 p-4 rounded-lg">
                  <p className="text-sm text-purple-400 font-medium">Nuevos esta semana</p>
                  <p className="text-2xl font-bold text-purple-300">{resumen?.usuarios?.semana || 0}</p>
                </div>
              </div>
            </div>
            {usuarios.length > 0 && <UserTable usuarios={usuarios} />}
          </div>
        )}

        {/* Vista Pagos */}
        {vistaActual === 'pagos' && (
          <div className="space-y-6">
            {/* Pagos pendientes */}
            {pagosPendientes.length > 0 && (
              <>
                <div className="bg-orange-500/10 border-l-4 border-orange-500 p-4 rounded">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <span className="text-2xl">⚠️</span>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-orange-400">
                        Pagos Pendientes de Verificación
                      </h3>
                      <div className="mt-2 text-sm text-orange-300">
                        <p>Tienes {pagosPendientes.length} pago(s) esperando aprobación.</p>
                      </div>
                    </div>
                  </div>
                </div>

                <PaymentTable 
                  pagos={pagosPendientes} 
                  onAprobar={aprobarPago}
                />
              </>
            )}

            {/* Todos los pagos recientes */}
            {pagosRecientes.length > 0 && <PaymentTable pagos={pagosRecientes} />}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;