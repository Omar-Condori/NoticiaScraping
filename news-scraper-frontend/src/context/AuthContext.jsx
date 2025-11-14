import { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  // 🔄 Cargar token y usuario desde localStorage al iniciar
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // 🔐 Función de Login
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
        throw new Error(data.error || 'Error en el login');
      }

      // Guardar token y usuario
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.usuario));
      
      setToken(data.access_token);
      setUser(data.usuario);

      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  // 📝 Función de Registro
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
        throw new Error(data.error || 'Error en el registro');
      }

      // Guardar token y usuario automáticamente después del registro
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.usuario));
      
      setToken(data.access_token);
      setUser(data.usuario);

      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  // 🚪 Función de Logout
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    navigate('/login');
  };

  // 👤 Obtener perfil del usuario
  const getProfile = async () => {
    if (!token) return null;

    try {
      const response = await fetch('http://localhost:8001/api/v1/auth/perfil', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        // Si el token expiró, hacer logout
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

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    getProfile,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};