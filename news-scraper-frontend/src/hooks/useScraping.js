import { useState } from 'react';
import { scrapingAPI } from '../services/api';
import toast from 'react-hot-toast';

export const useScraping = () => {
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);

  const ejecutar = async (params = {}) => {
    setLoading(true);
    
    const toastId = toast.loading('Ejecutando scraping...');
    
    try {
      const response = await scrapingService.ejecutar(params);
      setResultado(response);
      
      toast.success(
        `✅ ${response.total_noticias} noticias obtenidas`,
        { id: toastId }
      );
      
      return response;
    } catch (error) {
      toast.error(
        `Error: ${error.message}`,
        { id: toastId }
      );
      return null;
    } finally {
      setLoading(false);
    }
  };

  const ejecutarFuente = async (fuenteId, limite = 5) => {
    return await ejecutar({ fuente_id: fuenteId, limite });
  };

  const ejecutarTodas = async (limite = 5) => {
    return await ejecutar({ limite });
  };

  return {
    ejecutar,
    ejecutarFuente,
    ejecutarTodas,
    loading,
    resultado
  };
};