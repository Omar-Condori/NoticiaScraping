import { useState, useEffect, useCallback } from 'react';
import { schedulerAPI } from '../services/api';
import toast from 'react-hot-toast';

export const useScheduler = () => {
  const [tareas, setTareas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const cargarTareas = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await schedulerAPI.listarTareas();
      if (response.success) {
        setTareas(response.tareas || []);
      } else {
        throw new Error(response.error || 'Error al cargar tareas');
      }
    } catch (err) {
      setError(err.message);
      toast.error(`Error al cargar tareas: ${err.message}`);
      setTareas([]); // Asegurar que tareas sea un array vacío
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    cargarTareas();
  }, [cargarTareas]);

  const crear = async (tarea) => {
    try {
      const response = await schedulerAPI.crearTarea(
        tarea.nombre,
        tarea.intervalo_minutos,
        tarea.fuente_id,
        tarea.limite
      );
      if (response.success) {
        toast.success('Tarea creada exitosamente');
        await cargarTareas();
        return true;
      } else {
        throw new Error(response.error || 'Error al crear tarea');
      }
    } catch (err) {
      toast.error(`Error al crear tarea: ${err.message}`);
      return false;
    }
  };

  const eliminar = async (nombre) => {
    try {
      const response = await schedulerAPI.eliminarTarea(nombre);
      if (response.success) {
        toast.success('Tarea eliminada');
        await cargarTareas();
        return true;
      } else {
        throw new Error(response.error || 'Error al eliminar');
      }
    } catch (err) {
      toast.error(`Error al eliminar: ${err.message}`);
      return false;
    }
  };

  const pausar = async (nombre) => {
    try {
      const response = await schedulerAPI.pausarTarea(nombre);
      if (response.success) {
        toast.success('Tarea pausada');
        await cargarTareas();
        return true;
      } else {
        throw new Error(response.error || 'Error al pausar');
      }
    } catch (err) {
      toast.error(`Error al pausar: ${err.message}`);
      return false;
    }
  };

  const reanudar = async (nombre) => {
    try {
      const response = await schedulerAPI.reanudarTarea(nombre);
      if (response.success) {
        toast.success('Tarea reanudada');
        await cargarTareas();
        return true;
      } else {
        throw new Error(response.error || 'Error al reanudar');
      }
    } catch (err) {
      toast.error(`Error al reanudar: ${err.message}`);
      return false;
    }
  };

  return {
    tareas,
    loading,
    error,
    crear,
    eliminar,
    pausar,
    reanudar,
    recargar: cargarTareas
  };
};