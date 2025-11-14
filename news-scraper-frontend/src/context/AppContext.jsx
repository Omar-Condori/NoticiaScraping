import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp debe usarse dentro de AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  // ==================== ESTADO DE AUTENTICACIÓN ====================
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // ==================== ESTADO DE PLANES ====================
  const [planActual, setPlanActual] = useState(null);
  const [limiteFuentes, setLimiteFuentes] = useState(null);
  const [limiteScraping, setLimiteScraping] = useState(null);
  const [loadingPlan, setLoadingPlan] = useState(false);

  // Cargar token y usuario desde localStorage al iniciar
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // Cargar información del plan cuando el usuario inicia sesión
  useEffect(() => {
    if (user && token) {
      cargarInformacionPlan();
    }
  }, [user, token]);

  // ==================== FUNCIONES DE AUTENTICACIÓN ====================
  
  const login = async (nombre_usuario, contrasena) => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nombre_usuario, contrasena }),
      });

      const data = await response.json();

      if (!response.ok) {
        console.error('Error en login:', data);
        throw new Error(data.error || 'Error en el login');
      }

      // Asegurar que el usuario tenga rol
      if (data.usuario && !data.usuario.rol) {
        data.usuario.rol = 'usuario';
      }

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.usuario));
      
      setToken(data.access_token);
      setUser(data.usuario);

      return { success: true };
    } catch (error) {
      console.error('Error completo en login:', error);
      return { success: false, error: error.message };
    }
  };

  const register = async (nombre_usuario, email, contrasena) => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nombre_usuario, email, contrasena }),
      });

      const data = await response.json();

      if (!response.ok) {
        console.error('Error en registro:', data);
        throw new Error(data.error || 'Error en el registro');
      }

      // Asegurar que el usuario tenga rol
      if (data.usuario && !data.usuario.rol) {
        data.usuario.rol = 'usuario';
      }

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.usuario));
      
      setToken(data.access_token);
      setUser(data.usuario);

      return { success: true };
    } catch (error) {
      console.error('Error completo en registro:', error);
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setPlanActual(null);
    setLimiteFuentes(null);
    setLimiteScraping(null);
    navigate('/login');
  };

  const getProfile = async () => {
    if (!token) return null;

    try {
      const response = await fetch('http://localhost:8001/api/v1/auth/perfil', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          logout();
        }
        throw new Error('Error obteniendo perfil');
      }

      const data = await response.json();
      return data.usuario;
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  };

  // ==================== FUNCIONES DE PLANES ====================

  const cargarInformacionPlan = async () => {
    if (!token) return;

    setLoadingPlan(true);
    try {
      // Obtener plan actual
      const responsePlan = await fetch('http://localhost:8001/api/v1/suscripciones/mi-plan', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (responsePlan.ok) {
        const dataPlan = await responsePlan.json();
        setPlanActual(dataPlan.suscripcion);
        setLimiteFuentes(dataPlan.limite_info);
      }

      // Obtener estadísticas de scraping
      const responseStats = await fetch('http://localhost:8001/api/v1/scraping/estadisticas', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (responseStats.ok) {
        const dataStats = await responseStats.json();
        setLimiteScraping(dataStats);
      }
    } catch (error) {
      console.error('Error cargando información del plan:', error);
    } finally {
      setLoadingPlan(false);
    }
  };

  const actualizarPlan = async () => {
    await cargarInformacionPlan();
  };

  const value = {
    // Autenticación
    user,
    token,
    loading,
    login,
    register,
    logout,
    getProfile,
    isAuthenticated: !!token,
    
    // Planes y límites
    planActual,
    limiteFuentes,
    limiteScraping,
    loadingPlan,
    cargarInformacionPlan,
    actualizarPlan,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};