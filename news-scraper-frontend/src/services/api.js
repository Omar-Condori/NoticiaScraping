const API_URL = 'http://localhost:8001/api/v1';

// Función helper para obtener el token y headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
};

// ==================== AUTENTICACIÓN ====================

export const authAPI = {
  login: async (nombre_usuario, contrasena) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre_usuario, contrasena }),
    });
    return response.json();
  },

  register: async (nombre_usuario, email, contrasena) => {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre_usuario, email, contrasena }),
    });
    return response.json();
  },

  getProfile: async () => {
    const response = await fetch(`${API_URL}/auth/perfil`, {
      headers: getAuthHeaders(),
    });
    return response.json();
  },
};

// ==================== SCRAPING ====================

export const scrapingAPI = {
  ejecutar: async (limite = 5, fuenteId = null) => {
    const params = new URLSearchParams({ limite: limite.toString() });
    if (fuenteId) params.append('fuente_id', fuenteId);

    const response = await fetch(`${API_URL}/scraping/ejecutar?${params}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    return response.json();
  },
};

// ==================== NOTICIAS ====================

export const noticiasAPI = {
  obtener: async (limite = 50, offset = 0, fuenteId = null, categoria = null) => {
    const params = new URLSearchParams({
      limite: limite.toString(),
      offset: offset.toString(),
    });
    if (fuenteId) params.append('fuente_id', fuenteId);
    if (categoria) params.append('categoria', categoria);

    try {
      const response = await fetch(`${API_URL}/noticias?${params}`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching noticias:', error);
      return {
        success: false,
        error: 'No se pudo conectar al servidor. Verifica que el backend esté corriendo.',
        noticias: [],
        total: 0
      };
    }
  },

  contar: async () => {
    const response = await fetch(`${API_URL}/noticias/contar`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  limpiar: async () => {
    const response = await fetch(`${API_URL}/noticias`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return response.json();
  },

  buscar: async (query, fuenteId, fechaDesde, fechaHasta, limite = 50) => {
    const params = new URLSearchParams({ limite: limite.toString() });
    if (query) params.append('q', query);
    if (fuenteId) params.append('fuente_id', fuenteId);
    if (fechaDesde) params.append('fecha_desde', fechaDesde);
    if (fechaHasta) params.append('fecha_hasta', fechaHasta);

    const response = await fetch(`${API_URL}/noticias/buscar?${params}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  exportar: async (formato = 'json', limite = 100, fuenteId = null) => {
    const params = new URLSearchParams({
      formato,
      limite: limite.toString(),
    });
    if (fuenteId) params.append('fuente_id', fuenteId);

    const response = await fetch(`${API_URL}/noticias/exportar?${params}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.blob();
  },
};

// ==================== CATEGORÍAS ====================

export const categoriasAPI = {
  obtener: async () => {
    try {
      const response = await fetch(`${API_URL}/categorias`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching categorias:', error);
      return {
        success: false,
        error: 'No se pudo conectar al servidor. Verifica que el backend esté corriendo.',
        categorias: []
      };
    }
  },
};

// ==================== FUENTES ====================

export const fuentesAPI = {
  listar: async (soloActivas = false) => {
    const params = new URLSearchParams();
    if (soloActivas) params.append('activas', 'true');

    try {
      const response = await fetch(`${API_URL}/fuentes?${params}`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching fuentes:', error);
      return {
        success: false,
        error: 'No se pudo conectar al servidor. Verifica que el backend esté corriendo.',
        fuentes: [],
        total: 0
      };
    }
  },

  obtener: async (id) => {
    const response = await fetch(`${API_URL}/fuentes/${id}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  crear: async (nombre, url) => {
    const response = await fetch(`${API_URL}/fuentes`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ nombre, url }),
    });
    return response.json();
  },

  actualizar: async (id, datos) => {
    const response = await fetch(`${API_URL}/fuentes/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(datos),
    });
    return response.json();
  },

  eliminar: async (id) => {
    const response = await fetch(`${API_URL}/fuentes/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return response.json();
  },
};

// ==================== ESTADÍSTICAS ====================

export const estadisticasAPI = {
  generales: async () => {
    const response = await fetch(`${API_URL}/estadisticas`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  tendencias: async (dias = 7) => {
    const response = await fetch(`${API_URL}/estadisticas/tendencias?dias=${dias}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  topFuentes: async (limite = 5) => {
    const response = await fetch(`${API_URL}/estadisticas/top-fuentes?limite=${limite}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },
};

// ==================== SCHEDULER ====================

export const schedulerAPI = {
  listarTareas: async () => {
    const response = await fetch(`${API_URL}/scheduler/tareas`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  crearTarea: async (nombre, intervaloMinutos, fuenteId = null, limite = 5) => {
    const response = await fetch(`${API_URL}/scheduler/tareas`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        nombre,
        intervalo_minutos: intervaloMinutos,
        fuente_id: fuenteId,
        limite,
      }),
    });
    return response.json();
  },

  obtenerTarea: async (nombre) => {
    const response = await fetch(`${API_URL}/scheduler/tareas/${nombre}`, {
      headers: getAuthHeaders()
    });
    return response.json();
  },

  eliminarTarea: async (nombre) => {
    const response = await fetch(`${API_URL}/scheduler/tareas/${nombre}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return response.json();
  },

  pausarTarea: async (nombre) => {
    const response = await fetch(`${API_URL}/scheduler/tareas/${nombre}/pausar`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return response.json();
  },

  reanudarTarea: async (nombre) => {
    const response = await fetch(`${API_URL}/scheduler/tareas/${nombre}/reanudar`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return response.json();
  },
};

// ==================== PLANES Y SUSCRIPCIONES ====================

// Obtener todos los planes disponibles
export const obtenerPlanes = async () => {
  try {
    const response = await fetch(`${API_URL}/planes`, {
      headers: getAuthHeaders()
    });
    return await response.json();
  } catch (error) {
    console.error('Error obteniendo planes:', error);
    throw error;
  }
};

// Obtener mi plan actual
export const obtenerMiPlan = async () => {
  try {
    const response = await fetch(`${API_URL}/suscripciones/mi-plan`, {
      headers: getAuthHeaders()
    });
    return await response.json();
  } catch (error) {
    console.error('Error obteniendo mi plan:', error);
    throw error;
  }
};

// Cambiar de plan
export const cambiarPlan = async (planId, pagoId) => {
  try {
    const response = await fetch(`${API_URL}/suscripciones/cambiar`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        plan_id: planId,
        pago_id: pagoId
      })
    });
    return await response.json();
  } catch (error) {
    console.error('Error cambiando plan:', error);
    throw error;
  }
};

// ==================== PAGOS ====================

// Crear un pago
export const crearPago = async (planId, metodoPago) => {
  try {
    const response = await fetch(`${API_URL}/pagos/crear`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        plan_id: planId,
        metodo_pago: metodoPago
      })
    });
    return await response.json();
  } catch (error) {
    console.error('Error creando pago:', error);
    throw error;
  }
};

// Verificar pago de Yape
export const verificarPagoYape = async (pagoId, comprobanteImg = null) => {
  try {
    const response = await fetch(`${API_URL}/pagos/verificar-yape`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        pago_id: pagoId,
        comprobante_img: comprobanteImg
      })
    });
    return await response.json();
  } catch (error) {
    console.error('Error verificando pago Yape:', error);
    throw error;
  }
};

// Obtener historial de pagos
export const obtenerMisPagos = async () => {
  try {
    const response = await fetch(`${API_URL}/pagos/mis-pagos`, {
      headers: getAuthHeaders()
    });
    return await response.json();
  } catch (error) {
    console.error('Error obteniendo pagos:', error);
    throw error;
  }
};

// ==================== ESTADÍSTICAS DE SCRAPING ====================

// Obtener estadísticas de scraping del usuario
export const obtenerEstadisticasScraping = async () => {
  try {
    const response = await fetch(`${API_URL}/scraping/estadisticas`, {
      headers: getAuthHeaders()
    });
    return await response.json();
  } catch (error) {
    console.error('Error obteniendo estadísticas de scraping:', error);
    throw error;
  }
};