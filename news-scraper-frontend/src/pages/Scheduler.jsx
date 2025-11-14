import { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { useScheduler } from '../hooks/useScheduler';
import { fuentesAPI } from '../services/api';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/StatsCard';
import Button from '../components/ui/Button';
import Input, { Select } from '../components/ui/Input';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import { TableSkeleton } from '../components/ui/Skeleton';
import { Plus, Play, Pause, Trash2, Clock, RefreshCw } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function Scheduler() {
  const { tareas, loading, crear, eliminar, pausar, reanudar, recargar } = useScheduler();
  const [fuentesActivas, setFuentesActivas] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    intervalo_minutos: 60,
    fuente_id: '',
    limite: 5
  });

  // Cargar fuentes activas
  useEffect(() => {
    const cargarFuentes = async () => {
      try {
        const response = await fuentesAPI.listar(true);
        if (response.success) {
          setFuentesActivas(response.fuentes || []);
        }
      } catch (err) {
        console.error('Error cargando fuentes:', err);
        setFuentesActivas([]);
      }
    };
    cargarFuentes();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const data = {
      nombre: formData.nombre,
      intervalo_minutos: parseInt(formData.intervalo_minutos),
      limite: parseInt(formData.limite)
    };

    if (formData.fuente_id) {
      data.fuente_id = parseInt(formData.fuente_id);
    }

    const success = await crear(data);
    if (success) {
      setModalOpen(false);
      setFormData({
        nombre: '',
        intervalo_minutos: 60,
        fuente_id: '',
        limite: 5
      });
    }
  };

  const handlePauseResume = async (tarea) => {
    if (tarea.activa) {
      await pausar(tarea.nombre);
    } else {
      await reanudar(tarea.nombre);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <TableSkeleton rows={5} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Scheduler</h1>
          <p className="text-gray-400">{tareas.length} tareas programadas</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            icon={RefreshCw}
            onClick={recargar}
          >
            Recargar
          </Button>
          <Button
            variant="primary"
            icon={Plus}
            onClick={() => setModalOpen(true)}
          >
            Nueva Tarea
          </Button>
        </div>
      </div>

      {/* Lista de Tareas */}
      {tareas.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-4">No hay tareas programadas</p>
            <Button
              variant="primary"
              icon={Plus}
              onClick={() => setModalOpen(true)}
            >
              Crear Primera Tarea
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {tareas.map((tarea) => (
            <Card key={tarea.nombre} hover>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <Clock className="w-5 h-5 text-accent-primary" />
                      <CardTitle className="text-lg">{tarea.nombre}</CardTitle>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant={tarea.activa ? 'success' : 'warning'}>
                        {tarea.activa ? 'Activa' : 'Pausada'}
                      </Badge>
                      <Badge variant="primary">
                        cada {tarea.intervalo_minutos} min
                      </Badge>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => handlePauseResume(tarea)}
                      className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
                      title={tarea.activa ? 'Pausar' : 'Reanudar'}
                    >
                      {tarea.activa ? (
                        <Pause className="w-4 h-4 text-accent-warning" />
                      ) : (
                        <Play className="w-4 h-4 text-accent-success" />
                      )}
                    </button>
                    <button
                      onClick={() => eliminar(tarea.nombre)}
                      className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4 text-gray-400 hover:text-accent-danger" />
                    </button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  {tarea.fuente_id && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Fuente:</span>
                      <span className="text-gray-300">
                        {fuentesActivas.find(f => f.id === tarea.fuente_id)?.nombre || 'ID ' + tarea.fuente_id}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-500">Límite:</span>
                    <span className="text-gray-300">{tarea.limite} noticias</span>
                  </div>
                  {tarea.proxima_ejecucion && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Próxima ejecución:</span>
                      <span className="text-gray-300">
                        {format(new Date(tarea.proxima_ejecucion), "dd MMM, HH:mm", { locale: es })}
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modal de Nueva Tarea */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Nueva Tarea Programada"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nombre de la tarea *"
            value={formData.nombre}
            onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
            required
            placeholder="Ej: scraping_diario"
          />

          <Input
            label="Intervalo (minutos) *"
            type="number"
            min="1"
            value={formData.intervalo_minutos}
            onChange={(e) => setFormData({ ...formData, intervalo_minutos: e.target.value })}
            required
            placeholder="60"
          />

          <Select
            label="Fuente (opcional)"
            value={formData.fuente_id}
            onChange={(e) => setFormData({ ...formData, fuente_id: e.target.value })}
          >
            <option value="">Todas las fuentes</option>
            {fuentesActivas.map(fuente => (
              <option key={fuente.id} value={fuente.id}>
                {fuente.nombre}
              </option>
            ))}
          </Select>

          <Input
            label="Noticias por ejecución *"
            type="number"
            min="1"
            max="50"
            value={formData.limite}
            onChange={(e) => setFormData({ ...formData, limite: e.target.value })}
            required
            placeholder="5"
          />

          <div className="bg-accent-warning/10 border border-accent-warning/20 rounded-lg p-4">
            <p className="text-sm text-accent-warning">
              ⚠️ La tarea se ejecutará automáticamente cada {formData.intervalo_minutos} minutos
            </p>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setModalOpen(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" variant="primary">
              Crear Tarea
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};