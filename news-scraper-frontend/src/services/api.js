import axios from 'axios';

const API_URL = 'http://localhost:8001/api/v1';

// ==================== CONFIGURACIÓN DE AXIOS ====================
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// ==================== AUTH API ====================
export const authAPI = {
  register: (userData) => {
    return axios.post(`${API_URL}/auth/register`, userData);
  },
  
  login: (credentials) => {
    return axios.post(`${API_URL}/auth/login`, credentials);
  },
  
  perfil: () => {
    return axios.get(`${API_URL}/auth/perfil`, {
      headers: getAuthHeaders()
    });
  }
};

// ==================== NOTICIAS API ====================
export const noticiasAPI = {
  obtener: (params = {}) => {
    return axios.get(`${API_URL}/noticias`, {
      params,
      headers: getAuthHeaders()
    });
  },
  
  contar: () => {
    return axios.get(`${API_URL}/noticias/contar`);
  },
  
  limpiar: () => {
    return axios.delete(`${API_URL}/noticias`, {
      headers: getAuthHeaders()
    });
  },
  
  buscar: (params) => {
    return axios.get(`${API_URL}/noticias/buscar`, { params });
  },
  
  exportar: (formato = 'json', limite = 100) => {
    return axios.get(`${API_URL}/noticias/exportar`, {
      params: { formato, limite },
      headers: getAuthHeaders(),
      responseType: 'blob'
    });
  }
};

// ==================== CATEGORIAS API ====================
export const categoriasAPI = {
  obtener: () => {
    return axios.get(`${API_URL}/categorias`, {
      headers: getAuthHeaders()
    });
  }
};

// ==================== FUENTES API ====================
export const fuentesAPI = {
  listar: (soloActivas = false) => {
    return axios.get(`${API_URL}/fuentes`, {
      params: { activas: soloActivas },
      headers: getAuthHeaders()
    });
  },
  
  obtener: (id) => {
    return axios.get(`${API_URL}/fuentes/${id}`, {
      headers: getAuthHeaders()
    });
  },
  
  agregar: (fuenteData) => {
    return axios.post(`${API_URL}/fuentes`, fuenteData, {
      headers: getAuthHeaders()
    });
  },
  
  actualizar: (id, fuenteData) => {
    return axios.put(`${API_URL}/fuentes/${id}`, fuenteData, {
      headers: getAuthHeaders()
    });
  },
  
  eliminar: (id) => {
    return axios.delete(`${API_URL}/fuentes/${id}`, {
      headers: getAuthHeaders()
    });
  }
};

// ==================== SCRAPING API ====================
export const scrapingAPI = {
  ejecutar: (params = {}) => {
    return axios.post(`${API_URL}/scraping/ejecutar`, null, {
      params,
      headers: getAuthHeaders()
    });
  },
  
  estadisticas: () => {
    return axios.get(`${API_URL}/scraping/estadisticas`, {
      headers: getAuthHeaders()
    });
  }
};

// ==================== ESTADÍSTICAS API ====================
export const estadisticasAPI = {
  generales: () => {
    return axios.get(`${API_URL}/estadisticas`);
  },
  
  tendencias: (dias = 7) => {
    return axios.get(`${API_URL}/estadisticas/tendencias`, {
      params: { dias }
    });
  },
  
  topFuentes: (limite = 5) => {
    return axios.get(`${API_URL}/estadisticas/top-fuentes`, {
      params: { limite }
    });
  }
};

// ==================== SCHEDULER API ====================
export const schedulerAPI = {
  listarTareas: () => {
    return axios.get(`${API_URL}/scheduler/tareas`);
  },
  
  crearTarea: (tareaData) => {
    return axios.post(`${API_URL}/scheduler/tareas`, tareaData);
  },
  
  obtenerTarea: (nombre) => {
    return axios.get(`${API_URL}/scheduler/tareas/${nombre}`);
  },
  
  eliminarTarea: (nombre) => {
    return axios.delete(`${API_URL}/scheduler/tareas/${nombre}`);
  },
  
  pausarTarea: (nombre) => {
    return axios.post(`${API_URL}/scheduler/tareas/${nombre}/pausar`);
  },
  
  reanudarTarea: (nombre) => {
    return axios.post(`${API_URL}/scheduler/tareas/${nombre}/reanudar`);
  }
};

// ==================== PLANES API ====================
export const planesAPI = {
  listar: () => {
    return axios.get(`${API_URL}/planes`);
  },
  
  miPlan: () => {
    return axios.get(`${API_URL}/suscripciones/mi-plan`, {
      headers: getAuthHeaders()
    });
  },
  
  cambiarPlan: (planData) => {
    return axios.post(`${API_URL}/suscripciones/cambiar`, planData, {
      headers: getAuthHeaders()
    });
  }
};

// ==================== PAGOS API ====================
export const pagosAPI = {
  crear: (pagoData) => {
    return axios.post(`${API_URL}/pagos/crear`, pagoData, {
      headers: getAuthHeaders()
    });
  },
  
  verificarYape: (pagoData) => {
    return axios.post(`${API_URL}/pagos/verificar-yape`, pagoData, {
      headers: getAuthHeaders()
    });
  },
  
  misPagos: () => {
    return axios.get(`${API_URL}/pagos/mis-pagos`, {
      headers: getAuthHeaders()
    });
  }
};

// ==================== SUSCRIPCIONES API ====================
export const suscripcionesAPI = {
  miPlan: () => {
    return axios.get(`${API_URL}/suscripciones/mi-plan`, {
      headers: getAuthHeaders()
    });
  },
  
  cambiar: (suscripcionData) => {
    return axios.post(`${API_URL}/suscripciones/cambiar`, suscripcionData, {
      headers: getAuthHeaders()
    });
  }
};

// ==================== ADMIN API ====================
export const adminAPI = {
  obtenerResumen: () => {
    return axios.get(`${API_URL}/admin/stats/resumen`, {
      headers: getAuthHeaders()
    });
  },

  obtenerUsuariosPorPlan: () => {
    return axios.get(`${API_URL}/admin/stats/usuarios-por-plan`, {
      headers: getAuthHeaders()
    });
  },

  obtenerIngresosMensuales: (meses = 6) => {
    return axios.get(`${API_URL}/admin/stats/ingresos-mensuales`, {
      params: { meses },
      headers: getAuthHeaders()
    });
  },

  obtenerUsuariosRecientes: (limite = 10) => {
    return axios.get(`${API_URL}/admin/usuarios/recientes`, {
      params: { limite },
      headers: getAuthHeaders()
    });
  },

  obtenerPagosRecientes: (limite = 10) => {
    return axios.get(`${API_URL}/admin/pagos/recientes`, {
      params: { limite },
      headers: getAuthHeaders()
    });
  },

  obtenerPagosPendientes: () => {
    return axios.get(`${API_URL}/admin/pagos/pendientes`, {
      headers: getAuthHeaders()
    });
  },

  aprobarPago: (pagoId) => {
    return axios.post(`${API_URL}/admin/pagos/${pagoId}/aprobar`, {}, {
      headers: getAuthHeaders()
    });
  }
};

// ==================== EXPORTACIÓN DEFAULT (para compatibilidad) ====================
const api = {
  auth: authAPI,
  noticias: noticiasAPI,
  categorias: categoriasAPI,
  fuentes: fuentesAPI,
  scraping: scrapingAPI,
  estadisticas: estadisticasAPI,
  scheduler: schedulerAPI,
  planes: planesAPI,
  pagos: pagosAPI,
  suscripciones: suscripcionesAPI,
  admin: adminAPI
};

export default api;