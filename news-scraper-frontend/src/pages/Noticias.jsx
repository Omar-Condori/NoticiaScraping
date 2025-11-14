// Similar a Dashboard.jsx, con las mismas actualizaciones
import { useState, useEffect } from 'react';
import { noticiasAPI, fuentesAPI, categoriasAPI } from '../services/api';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Skeleton from '../components/ui/Skeleton';
import { AlertCircle, Filter, Tag, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import Button from '../components/ui/Button';

export default function Noticias() {
  const [noticias, setNoticias] = useState([]);
  const [fuentes, setFuentes] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Filtros
  const [fuenteSeleccionada, setFuenteSeleccionada] = useState('');
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState('');
  const [limite, setLimite] = useState(12);
  
  // Paginación
  const [paginaActual, setPaginaActual] = useState(1);
  const [totalNoticias, setTotalNoticias] = useState(0);
  const [totalPaginas, setTotalPaginas] = useState(0);

  const cargarNoticias = async () => {
    setLoading(true);
    setError('');

    try {
      const offset = (paginaActual - 1) * limite;
      // Convertir fuenteSeleccionada a número si existe y no está vacío
      const fuenteId = fuenteSeleccionada && fuenteSeleccionada !== '' ? parseInt(fuenteSeleccionada, 10) : null;
      
      const data = await noticiasAPI.obtener(
        limite,
        offset,
        fuenteId,
        categoriaSeleccionada || null
      );

      // Si hay error de conexión, mostrar mensaje pero no lanzar excepción
      if (data && data.success === false && data.error && data.error.includes('No se pudo conectar')) {
        setError(data.error);
        setNoticias([]);
        setTotalNoticias(0);
        setTotalPaginas(0);
        return;
      }
      
      if (data && data.success !== false) {
        setNoticias(data.noticias || []);
        setTotalNoticias(data.total || 0);
        setTotalPaginas(data.total_paginas || 0);
      } else {
        setError(data?.error || 'Error cargando noticias');
        setNoticias([]);
        setTotalNoticias(0);
        setTotalPaginas(0);
      }
    } catch (err) {
      setError(err.message || 'Error al cargar las noticias');
      setNoticias([]);
      setTotalNoticias(0);
      setTotalPaginas(0);
    } finally {
      setLoading(false);
    }
  };

  // Cargar fuentes y categorías
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const [fuentesData, categoriasData] = await Promise.all([
          fuentesAPI.listar(true),
          categoriasAPI.obtener(),
        ]);

        if (fuentesData && fuentesData.success !== false) {
          setFuentes(fuentesData.fuentes || []);
        } else {
          setFuentes([]);
        }

        if (categoriasData && categoriasData.success !== false) {
          setCategorias(categoriasData.categorias || []);
        } else {
          setCategorias([]);
        }
      } catch (err) {
        console.error('Error cargando datos:', err);
        setFuentes([]);
        setCategorias([]);
      }
    };

    cargarDatos();
  }, []);

  // Cargar noticias cuando cambie la página o los filtros
  useEffect(() => {
    cargarNoticias();
  }, [paginaActual, limite, fuenteSeleccionada, categoriaSeleccionada]);

  // Resetear a página 1 cuando cambien los filtros
  useEffect(() => {
    setPaginaActual(1);
  }, [fuenteSeleccionada, categoriaSeleccionada, limite]);

  const handleExportar = async (formato) => {
    try {
      const blob = await noticiasAPI.exportar(formato, 100, fuenteSeleccionada || null);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `noticias.${formato}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Error al exportar noticias');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Noticias Guardadas</h1>
          <p className="text-gray-400 mt-1">
            {totalNoticias > 0 ? (
              <>Mostrando {noticias.length} de {totalNoticias} noticias (Página {paginaActual} de {totalPaginas})</>
            ) : (
              'No hay noticias disponibles'
            )}
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={() => handleExportar('json')}
            variant="secondary"
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            JSON
          </Button>
          <Button
            onClick={() => handleExportar('csv')}
            variant="secondary"
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            CSV
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-accent-primary" />
          <h2 className="text-lg font-semibold text-white">Filtros</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                <option key={fuente.id} value={String(fuente.id)}>
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

          {/* Límite */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Noticias por página
            </label>
            <select
              value={limite}
              onChange={(e) => setLimite(Number(e.target.value))}
              className="w-full px-4 py-2 bg-dark-hover border border-dark-border rounded-lg text-white focus:ring-2 focus:ring-accent-primary focus:border-transparent"
            >
              <option value={6}>6</option>
              <option value={12}>12</option>
              <option value={24}>24</option>
              <option value={48}>48</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error */}
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
          <p className="text-gray-400 text-lg">No hay noticias disponibles</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {noticias.map((noticia, index) => (
              <Card key={`${noticia.id}-${index}`} noticia={noticia} />
            ))}
          </div>

          {/* Paginación */}
          {totalPaginas > 1 && (
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-dark-border">
              <div className="text-sm text-gray-400">
                Página {paginaActual} de {totalPaginas}
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setPaginaActual(prev => Math.max(1, prev - 1))}
                  disabled={paginaActual === 1 || loading}
                  className="gap-2"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Anterior
                </Button>
                
                {/* Números de página */}
                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(5, totalPaginas) }, (_, i) => {
                    let pageNum;
                    if (totalPaginas <= 5) {
                      pageNum = i + 1;
                    } else if (paginaActual <= 3) {
                      pageNum = i + 1;
                    } else if (paginaActual >= totalPaginas - 2) {
                      pageNum = totalPaginas - 4 + i;
                    } else {
                      pageNum = paginaActual - 2 + i;
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPaginaActual(pageNum)}
                        disabled={loading}
                        className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                          paginaActual === pageNum
                            ? 'bg-accent-primary text-white'
                            : 'bg-dark-hover text-gray-300 hover:bg-dark-border'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                
                <Button
                  variant="secondary"
                  onClick={() => setPaginaActual(prev => Math.min(totalPaginas, prev + 1))}
                  disabled={paginaActual === totalPaginas || loading}
                  className="gap-2"
                >
                  Siguiente
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}