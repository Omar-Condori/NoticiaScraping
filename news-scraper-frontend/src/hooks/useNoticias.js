import { useState } from 'react';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8001/api/v1';

export const useNoticias = (params = {}) => {
  const [noticias, setNoticias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);

  return {
    noticias,
    loading,
    error,
    total
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
      const queryParams = new URLSearchParams();
      
      if (params.q) queryParams.append('q', params.q);
      if (params.fuente_id) queryParams.append('fuente_id', params.fuente_id);
      if (params.fecha_desde) queryParams.append('fecha_desde', params.fecha_desde);
      if (params.fecha_hasta) queryParams.append('fecha_hasta', params.fecha_hasta);
      if (params.limite) queryParams.append('limite', params.limite);
      if (params.orden) queryParams.append('orden', params.orden);

      const url = `${API_URL}/noticias/buscar?${queryParams.toString()}`;
      
      console.log('🔍 URL de búsqueda:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const data = await response.json();
      
      console.log('📊 Respuesta del backend:', data);
      
      if (data.success) {
        setResultados(data.resultados || []);
        toast.success(`Se encontraron ${data.resultados?.length || 0} resultados`);
        return data;
      } else {
        throw new Error(data.error || 'Error en búsqueda');
      }
    } catch (err) {
      console.error('❌ Error en búsqueda:', err);
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
      const response = await fetch(`${API_URL}/noticias/buscar/palabras-clave`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ palabras, limite })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setResultados(data.resultados || []);
        toast.success(`Se encontraron ${data.resultados?.length || 0} resultados`);
        return data;
      } else {
        throw new Error(data.error || 'Error en búsqueda');
      }
    } catch (err) {
      console.error('❌ Error en búsqueda por palabras:', err);
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
      const queryParams = new URLSearchParams({
        formato,
        ...params
      });

      const response = await fetch(`${API_URL}/noticias/exportar?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Error al exportar');
      }

      const blob = await response.blob();
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
