import { useState, useEffect, useCallback } from 'react';
import { noticiasAPI } from '../services/api';
import toast from 'react-hot-toast';

export const useNoticias = (params = {}) => {
  const [noticias, setNoticias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);

  const cargarNoticias = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await noticiasService.obtener(params);
      setNoticias(response.noticias || []);
      setTotal(response.total || 0);
    } catch (err) {
      setError(err.message);
      toast.error(`Error al cargar noticias: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    cargarNoticias();
  }, [cargarNoticias]);

  const recargar = () => {
    cargarNoticias();
  };

  return {
    noticias,
    loading,
    error,
    total,
    recargar
  };
};

export const useBusqueda = () => {
  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const buscar = async (params) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await noticiasAPI.buscar(
        params.q,
        params.fuente_id,
        params.fecha_desde,
        params.fecha_hasta,
        params.limite
      );
      if (response.success) {
        setResultados(response.resultados || []);
        return response;
      } else {
        throw new Error(response.error || 'Error en búsqueda');
      }
    } catch (err) {
      setError(err.message);
      toast.error(`Error en búsqueda: ${err.message}`);
      setResultados([]);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const buscarPorPalabras = async (palabras, limite = 50) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8001/api/v1/noticias/buscar/palabras-clave', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ palabras, limite })
      });
      const data = await response.json();
      if (data.success) {
        setResultados(data.resultados || []);
        return data;
      } else {
        throw new Error(data.error || 'Error en búsqueda');
      }
    } catch (err) {
      setError(err.message);
      toast.error(`Error en búsqueda: ${err.message}`);
      setResultados([]);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const limpiar = () => {
    setResultados([]);
    setError(null);
  };

  return {
    resultados,
    loading,
    error,
    buscar,
    buscarPorPalabras,
    limpiar
  };
};

export const useExportacion = () => {
  const [loading, setLoading] = useState(false);

  const exportar = async (formato, params = {}) => {
    setLoading(true);
    
    try {
      const blob = await noticiasService.exportar({
        formato,
        ...params
      });
      
      // Crear URL y descargar
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `noticias.${formato}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(`Archivo ${formato.toUpperCase()} descargado`);
    } catch (err) {
      toast.error(`Error al exportar: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return {
    exportar,
    loading
  };
};