import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom'; // <--- AGREGADO
import { useApp } from '../context/AppContext'; // <--- AGREGADO
import { fuentesAPI } from '../services/api';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Modal from '../components/ui/Modal';
import Badge from '../components/ui/Badge';
import { Plus, Edit, Trash2, Globe, CheckCircle, XCircle, AlertCircle, Crown } from 'lucide-react'; // <--- Crown agregado

export default function Fuentes() {
  const { limiteFuentes, loadingPlan } = useApp(); // <--- AGREGADO
  const [fuentes, setFuentes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    nombre: '',
    url: '',
  });

  useEffect(() => {
    cargarFuentes();
  }, []);

  const cargarFuentes = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fuentesAPI.listar();
      if (data && data.success === false && data.error && data.error.includes('No se pudo conectar')) {
        setError(data.error);
        setFuentes([]);
        return;
      }
      
      if (data && (data.success !== false)) {
        setFuentes(data.fuentes || []);
      } else {
        setError(data?.error || 'Error al cargar fuentes');
        setFuentes([]);
      }
    } catch (err) {
      setError(err.message || 'Error al cargar fuentes');
      setFuentes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // <--- AGREGADO: Verificar límite antes de crear
    if (limiteFuentes && !limiteFuentes.puede_agregar) {
      setError('Has alcanzado el límite de fuentes de tu plan. Actualiza tu plan para agregar más fuentes.');
      return;
    }

    if (!formData.nombre || !formData.url) {
      setError('Nombre y URL son requeridos');
      return;
    }

    try {
      new URL(formData.url);
    } catch {
      setError('URL inválida');
      return;
    }

    try {
      const data = await fuentesAPI.crear(formData.nombre, formData.url);

      if (data.success) {
        setSuccess('✅ Fuente agregada exitosamente con selectores por defecto');
        setModalAbierto(false);
        setFormData({ nombre: '', url: '' });
        cargarFuentes();
        
        setTimeout(() => {
          alert(
            'La fuente se creó con selectores HTML estándar.\n\n' +
            'Si el scraping no funciona correctamente, puedes:\n' +
            '1. Actualizar los selectores manualmente desde la lista de fuentes\n' +
            '2. Usar el botón "Editar" para personalizar los selectores CSS'
          );
        }, 500);
      } else {
        throw new Error(data.error || 'Error al crear fuente');
      }
    } catch (err) {
      setError(err.message || 'Error al agregar fuente');
    }
  };

  const handleEliminar = async (id, nombre) => {
    if (!window.confirm(`¿Eliminar la fuente "${nombre}"?`)) return;

    try {
      const data = await fuentesAPI.eliminar(id);
      if (data.success) {
        setSuccess('Fuente eliminada');
        cargarFuentes();
      }
    } catch (err) {
      setError('Error al eliminar fuente');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // <--- AGREGADO: Verificar si llegó al límite
  const puedeAgregarFuente = !limiteFuentes || limiteFuentes.puede_agregar;
  const enLimite = limiteFuentes && !limiteFuentes.puede_agregar;

  return (
    <div className="space-y-6">
      {/* <--- AGREGADO: Banner de advertencia de límite */}
      {enLimite && (
        <div className="bg-yellow-500/10 border-2 border-yellow-500/50 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-6 h-6 text-yellow-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-yellow-400 font-semibold text-lg mb-2">
                Has alcanzado el límite de fuentes
              </h3>
              <p className="text-gray-300 mb-4">
                Tienes {limiteFuentes.actuales} fuentes activas y tu plan permite {limiteFuentes.limite === -1 ? 'ilimitadas' : limiteFuentes.limite} fuentes.
                Para agregar más fuentes, actualiza tu plan.
              </p>
              <Link to="/planes">
                <Button className="gap-2 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600">
                  <Crown className="w-4 h-4" />
                  Ver Planes Premium
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Fuentes de Noticias</h1>
          <p className="text-gray-400 mt-1">
            Gestiona las fuentes de scraping
            {/* <--- AGREGADO: Mostrar contador */}
            {limiteFuentes && (
              <span className="ml-2">
                ({limiteFuentes.actuales} de {limiteFuentes.limite === -1 ? '∞' : limiteFuentes.limite} fuentes)
              </span>
            )}
          </p>
        </div>

        {/* <--- MODIFICADO: Botón deshabilitado si llegó al límite */}
        <Button 
          onClick={() => setModalAbierto(true)} 
          className="gap-2"
          disabled={!puedeAgregarFuente || loadingPlan}
          title={!puedeAgregarFuente ? 'Límite de fuentes alcanzado. Actualiza tu plan.' : ''}
        >
          <Plus className="w-4 h-4" />
          Nueva Fuente
        </Button>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-red-500 font-medium">Error</h3>
            <p className="text-red-400 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-500/10 border border-green-500/50 rounded-lg p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-green-500 font-medium">Éxito</h3>
            <p className="text-green-400 text-sm mt-1">{success}</p>
          </div>
        </div>
      )}

      {/* Lista de Fuentes */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary mx-auto"></div>
          <p className="text-gray-400 mt-4">Cargando fuentes...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {fuentes.map((fuente) => (
            <div
              key={fuente.id}
              className="bg-dark-card border border-dark-border rounded-xl p-6 hover:border-accent-primary/50 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-accent-primary/10 rounded-lg flex items-center justify-center">
                    <Globe className="w-5 h-5 text-accent-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {fuente.nombre}
                    </h3>
                    <Badge variant={fuente.activo ? 'success' : 'error'}>
                      {fuente.activo ? (
                        <>
                          <CheckCircle className="w-3 h-3" />
                          Activa
                        </>
                      ) : (
                        <>
                          <XCircle className="w-3 h-3" />
                          Inactiva
                        </>
                      )}
                    </Badge>
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-400 mb-4 break-all">
                {fuente.url}
              </p>

              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  className="flex-1 gap-2"
                  onClick={() => {
                    alert('Funcionalidad de edición completa próximamente');
                  }}
                >
                  <Edit className="w-4 h-4" />
                  Editar
                </Button>
                <Button
                  variant="error"
                  size="sm"
                  onClick={() => handleEliminar(fuente.id, fuente.nombre)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={modalAbierto}
        onClose={() => {
          setModalAbierto(false);
          setFormData({ nombre: '', url: '' });
          setError('');
        }}
        title="Nueva Fuente de Noticias"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-blue-500/10 border border-blue-500/50 rounded-lg p-4">
            <p className="text-sm text-blue-400">
              ℹ️ Solo necesitas el nombre y la URL. Los selectores CSS se asignarán automáticamente.
              Si el scraping no funciona, podrás editarlos después.
            </p>
          </div>

          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Nombre de la Fuente *
            </label>
            <Input
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              placeholder="Ej: Los Andes Puno"
              required
            />
          </div>

          {/* URL */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              URL del Sitio Web *
            </label>
            <Input
              name="url"
              value={formData.url}
              onChange={handleChange}
              placeholder="https://ejemplo.com"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Incluye el protocolo (https://)
            </p>
          </div>

          {/* Botones */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setModalAbierto(false);
                setFormData({ nombre: '', url: '' });
                setError('');
              }}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button type="submit" className="flex-1">
              Agregar Fuente
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}