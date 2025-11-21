import { useState, useEffect, useRef, useCallback } from 'react';
import { noticiasAPI, fuentesAPI, categoriasAPI, scrapingAPI, paisesAPI } from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Skeleton from '../components/ui/Skeleton';
import { RefreshCw, AlertCircle, Filter, Tag } from 'lucide-react';

// ✅ CATEGORÍAS OFICIALES DE NOTICIAS
const CATEGORIAS_NOTICIAS = [
  'Política',
  'Economía',
  'Deportes',
  'Internacional',
  'Tecnología',
  'Espectáculos',
  'Salud',
  'Cultura',
  'Ciencia',
  'Policiales',
  'Medio Ambiente',
  'Estilo de Vida',
  'Viajes',
  'Motor',
  'Opinión'
];

export default function Dashboard() {
  const [noticias, setNoticias] = useState([]);
  const [fuentes, setFuentes] = useState([]);
  const [categorias] = useState(CATEGORIAS_NOTICIAS); // ✅ Categorías fijas
  const [paises, setPaises] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState('');

  // Filtros
  const [fuenteSeleccionada, setFuenteSeleccionada] = useState('');
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState('');
  const [paisSeleccionado, setPaisSeleccionado] = useState('');
  const [limite, setLimite] = useState(20);

  // Estado para scroll infinito
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const observerTarget = useRef(null);

  // ✅ FUNCIÓN CORREGIDA: cargarNoticias
  const cargarNoticias = useCallback(async (reset = false) => {
    if (!hasMore && !reset) return;

    const isInitialLoad = reset || offset === 0;

    if (isInitialLoad) {
      setLoading(true);
      setOffset(0);
    } else {
      setLoadingMore(true);
    }

    setError('');

    try {
      const currentOffset = reset ? 0 : offset;

      // ✅ CORRECCIÓN: Construir objeto de parámetros
      const params = {
        limite: limite,
        offset: currentOffset
      };

      // Solo agregar fuente_id si está seleccionada
      if (fuenteSeleccionada && fuenteSeleccionada !== '') {
        params.fuente_id = parseInt(fuenteSeleccionada, 10);
      }

      // Solo agregar categoría si está seleccionada
      if (categoriaSeleccionada && categoriaSeleccionada !== '') {
        params.categoria = categoriaSeleccionada;
      }

      // Solo agregar país si está seleccionado
      if (paisSeleccionado && paisSeleccionado !== '') {
        params.pais = paisSeleccionado;
      }

      // ✅ Llamar a la API con objeto de parámetros
      const response = await noticiasAPI.obtener(params);
      const data = response.data;

      // Si hay error de conexión, mostrar mensaje pero no lanzar excepción
      if (data && data.success === false && data.error && data.error.includes('No se pudo conectar')) {
        setError(data.error);
        setNoticias([]);
        setHasMore(false);
        return;
      }

      if (!data || data.success === false) {
        throw new Error(data?.error || 'Error cargando noticias');
      }

      if (reset) {
        setNoticias(data.noticias || []);
      } else {
        setNoticias(prev => [...prev, ...(data.noticias || [])]);
      }

      // Si recibimos menos noticias que el límite, no hay más
      setHasMore((data.noticias || []).length === limite);
      setOffset(prev => reset ? limite : prev + limite);
    } catch (err) {
      console.error('Error en cargarNoticias:', err);
      setError(err.message || 'Error al cargar las noticias');
      setNoticias([]);
      setHasMore(false);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [limite, fuenteSeleccionada, categoriaSeleccionada, offset, hasMore]);

  // Intersection Observer para scroll infinito
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading && !loadingMore && hasMore) {
          cargarNoticias();
        }
      },
      { threshold: 0.1 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [cargarNoticias, loading, loadingMore, hasMore]);

  // ✅ CARGAR FUENTES Y CATEGORÍAS - MEJORADO
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        // Cargar fuentes y países (categorías son fijas)
        const [fuentesResponse, paisesResponse] = await Promise.all([
          fuentesAPI.listar(true),
          paisesAPI.obtener()
        ]);

        // ✅ Acceder a response.data
        if (fuentesResponse?.data && fuentesResponse.data.success !== false) {
          setFuentes(fuentesResponse.data.fuentes || []);
        } else {
          setFuentes([]);
        }

        // ✅ CARGAR PAÍSES
        if (paisesResponse?.data && paisesResponse.data.success !== false) {
          setPaises(paisesResponse.data.paises || []);
        } else {
          setPaises([]);
        }
      } catch (err) {
        console.error('Error cargando datos:', err);
        setFuentes([]);
        setPaises([]);
      }
    };

    cargarDatos();
  }, []);


  // Cargar noticias iniciales
  useEffect(() => {
    cargarNoticias(true);
  }, []);

  // Recargar cuando cambien los filtros
  useEffect(() => {
    setOffset(0);
    setHasMore(true);
    cargarNoticias(true);
  }, [fuenteSeleccionada, categoriaSeleccionada, paisSeleccionado, limite]);


  // ✅ FUNCIÓN CORREGIDA: ejecutarScraping con mejor manejo de errores
  const ejecutarScraping = async () => {
    setScraping(true);
    setError('');

    try {
      // ✅ CORRECCIÓN: Construir objeto de parámetros
      const params = {
        limite: 5
      };

      // Solo agregar fuente si está seleccionada
      if (fuenteSeleccionada && fuenteSeleccionada !== '') {
        params.fuente_id = parseInt(fuenteSeleccionada, 10);
      }

      const response = await scrapingAPI.ejecutar(params);
      const data = response.data;

      if (data.success) {
        // Recargar noticias después del scraping
        setOffset(0);
        setHasMore(true);
        await cargarNoticias(true);
      } else {
        throw new Error(data.error || 'Error en el scraping');
      }
    } catch (err) {
      console.error('Error en ejecutarScraping:', err);

      // ✅ MOSTRAR EL MENSAJE DEL BACKEND (incluye mensaje de límite alcanzado)
      if (err.response?.status === 403) {
        // Error 403 - Límite alcanzado
        const backendMessage = err.response?.data?.mensaje || err.response?.data?.error;
        if (backendMessage) {
          setError(backendMessage);
        } else {
          setError('Has alcanzado el límite de scraping de tu plan. Actualiza tu plan para continuar.');
        }
      } else if (err.response?.data?.mensaje) {
        setError(err.response.data.mensaje);
      } else if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError(err.message || 'Error al ejecutar el scraping');
      }
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">
            Panel principal de noticias
          </p>
        </div>

        <Button
          onClick={ejecutarScraping}
          disabled={scraping}
          className="gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
          {scraping ? 'Scrapeando...' : 'Scrapear Ahora'}
        </Button>
      </div>

      {/* Filtros */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-accent-primary" />
          <h2 className="text-lg font-semibold text-white">Filtros</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Selector de Fuente */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Fuente
            </label>
            <select
              value={fuenteSeleccionada}
              onChange={(e) => setFuenteSeleccionada(e.target.value)}
              className="w-full px-4 py-2 bg-dark-hover border border-dark-border rounded-lg text-white focus:ring-2 focus:ring-accent-primary focus:border-transparent"
            >
              <option value="">Todas las fuentes</option>
              {fuentes.map((fuente) => (
                <option key={fuente.id} value={fuente.id}>
                  {fuente.nombre}
                </option>
              ))}
            </select>
          </div>

          {/* Selector de Categoría */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <div className="flex items-center gap-2">
                <Tag className="w-4 h-4" />
                Categoría
              </div>
            </label>
            <select
              value={categoriaSeleccionada}
              onChange={(e) => setCategoriaSeleccionada(e.target.value)}
              className="w-full px-4 py-2 bg-dark-hover border border-dark-border rounded-lg text-white focus:ring-2 focus:ring-accent-primary focus:border-transparent"
            >
              <option value="">Todas las categorías</option>
              {categorias.map((categoria) => (
                <option key={categoria} value={categoria}>
                  {categoria}
                </option>
              ))}
            </select>
          </div>

          {/* Selector de País */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              País
            </label>
            <select
              value={paisSeleccionado}
              onChange={(e) => setPaisSeleccionado(e.target.value)}
              className="w-full px-4 py-2 bg-dark-hover border border-dark-border rounded-lg text-white focus:ring-2 focus:ring-accent-primary focus:border-transparent"
            >
              <option value="">Todos los países</option>
              {paises.map((pais) => (
                <option key={pais} value={pais}>
                  {pais}
                </option>
              ))}
            </select>
          </div>

          {/* Límite por página */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Noticias por carga
            </label>
            <Input
              type="number"
              min="5"
              max="50"
              value={limite}
              onChange={(e) => setLimite(Number(e.target.value))}
            />
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-red-500 font-medium">Error</h3>
            <p className="text-red-400 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Grid de Noticias */}
      {loading && noticias.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-96" />
          ))}
        </div>
      ) : noticias.length === 0 ? (
        <div className="bg-dark-card border border-dark-border rounded-xl p-12 text-center">
          <p className="text-gray-400 text-lg">
            No hay noticias disponibles
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Ejecuta un scraping para cargar noticias
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {noticias.map((noticia, index) => (
              <Card key={`${noticia.id}-${index}`} noticia={noticia} />
            ))}
          </div>

          {/* Elemento observador para scroll infinito */}
          <div ref={observerTarget} className="flex justify-center py-8">
            {loadingMore && (
              <div className="flex items-center gap-2 text-gray-400">
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Cargando más noticias...</span>
              </div>
            )}
            {!hasMore && noticias.length > 0 && (
              <p className="text-gray-500">No hay más noticias</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}