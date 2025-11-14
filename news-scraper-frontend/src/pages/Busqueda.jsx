import { useState, useEffect } from 'react';
import { useBusqueda } from '../hooks/useNoticias';
import { fuentesAPI } from '../services/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/StatsCard';
import Button from '../components/ui/Button';
import Input, { Select } from '../components/ui/Input';
import Badge from '../components/ui/Badge';
import { Search, X, ExternalLink, Tags } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function Busqueda() {
  const { resultados, loading, buscar, buscarPorPalabras, limpiar } = useBusqueda();
  const [fuentesActivas, setFuentesActivas] = useState([]);
  
  const [query, setQuery] = useState('');
  const [fuenteId, setFuenteId] = useState('');
  const [fechaDesde, setFechaDesde] = useState('');
  const [fechaHasta, setFechaHasta] = useState('');
  const [limite, setLimite] = useState(50);
  const [palabrasClave, setPalabrasClave] = useState('');
  const [tipoBusqueda, setTipoBusqueda] = useState('simple'); // simple | palabras

  // Cargar fuentes activas
  useEffect(() => {
    const cargarFuentes = async () => {
      try {
        const response = await fuentesAPI.listar(true);
        if (response.success) {
          setFuentesActivas(response.fuentes || []);
        }
      } catch (err) {
        console.error('Error cargando fuentes:', err);
        setFuentesActivas([]);
      }
    };
    cargarFuentes();
  }, []);

  const handleBuscar = async (e) => {
    e.preventDefault();
    
    if (tipoBusqueda === 'palabras') {
      const palabras = palabrasClave
        .split(',')
        .map(p => p.trim())
        .filter(p => p.length > 0);
      
      if (palabras.length === 0) return;
      await buscarPorPalabras(palabras, limite);
    } else {
      const params = {
        q: query || undefined,
        fuente_id: fuenteId || undefined,
        fecha_desde: fechaDesde || undefined,
        fecha_hasta: fechaHasta || undefined,
        limite,
        orden: 'DESC'
      };
      
      await buscar(params);
    }
  };

  const handleLimpiar = () => {
    setQuery('');
    setFuenteId('');
    setFechaDesde('');
    setFechaHasta('');
    setPalabrasClave('');
    limpiar();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Búsqueda Avanzada</h1>
        <p className="text-gray-400">Busca noticias con filtros personalizados</p>
      </div>

      {/* Formulario de Búsqueda */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros de Búsqueda</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleBuscar} className="space-y-4">
            {/* Tipo de Búsqueda */}
            <div className="flex gap-2">
              <Button
                type="button"
                variant={tipoBusqueda === 'simple' ? 'primary' : 'secondary'}
                size="sm"
                icon={Search}
                onClick={() => setTipoBusqueda('simple')}
              >
                Búsqueda Simple
              </Button>
              <Button
                type="button"
                variant={tipoBusqueda === 'palabras' ? 'primary' : 'secondary'}
                size="sm"
                icon={Tags}
                onClick={() => setTipoBusqueda('palabras')}
              >
                Palabras Clave
              </Button>
            </div>

            {tipoBusqueda === 'simple' ? (
              <>
                {/* Búsqueda Simple */}
                <Input
                  label="Buscar en título y resumen"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ej: política, tecnología, deportes..."
                  icon={Search}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Select
                    label="Fuente"
                    value={fuenteId}
                    onChange={(e) => setFuenteId(e.target.value)}
                  >
                    <option value="">Todas las fuentes</option>
                    {fuentesActivas.map(fuente => (
                      <option key={fuente.id} value={fuente.id}>
                        {fuente.nombre}
                      </option>
                    ))}
                  </Select>

                  <Select
                    label="Cantidad de resultados"
                    value={limite}
                    onChange={(e) => setLimite(parseInt(e.target.value))}
                  >
                    <option value={25}>25 resultados</option>
                    <option value={50}>50 resultados</option>
                    <option value={100}>100 resultados</option>
                    <option value={200}>200 resultados</option>
                  </Select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Fecha desde"
                    type="date"
                    value={fechaDesde}
                    onChange={(e) => setFechaDesde(e.target.value)}
                  />

                  <Input
                    label="Fecha hasta"
                    type="date"
                    value={fechaHasta}
                    onChange={(e) => setFechaHasta(e.target.value)}
                  />
                </div>
              </>
            ) : (
              <>
                {/* Búsqueda por Palabras Clave */}
                <Input
                  label="Palabras clave (separadas por comas)"
                  value={palabrasClave}
                  onChange={(e) => setPalabrasClave(e.target.value)}
                  placeholder="Ej: política, economía, tecnología"
                  icon={Tags}
                />

                <Select
                  label="Cantidad de resultados"
                  value={limite}
                  onChange={(e) => setLimite(parseInt(e.target.value))}
                >
                  <option value={25}>25 resultados</option>
                  <option value={50}>50 resultados</option>
                  <option value={100}>100 resultados</option>
                  <option value={200}>200 resultados</option>
                </Select>

                <div className="bg-accent-primary/10 border border-accent-primary/20 rounded-lg p-4">
                  <p className="text-sm text-accent-primary">
                    💡 Se mostrarán noticias que contengan al menos una de las palabras clave
                  </p>
                </div>
              </>
            )}

            <div className="flex gap-3">
              <Button
                type="submit"
                variant="primary"
                icon={Search}
                loading={loading}
                className="flex-1"
              >
                Buscar
              </Button>
              <Button
                type="button"
                variant="secondary"
                icon={X}
                onClick={handleLimpiar}
              >
                Limpiar
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Resultados */}
      {resultados.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Resultados</CardTitle>
                <CardDescription>Se encontraron {resultados.length} noticias</CardDescription>
              </div>
              <Badge variant="primary">{resultados.length} resultados</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {resultados.map((noticia) => (
                <div
                  key={noticia.id}
                  className="p-4 bg-dark-hover rounded-lg border border-dark-border hover:border-accent-primary/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <Badge variant="secondary">{noticia.fuente}</Badge>
                        <span className="text-xs text-gray-500">
                          {format(new Date(noticia.fecha_scraping), "dd MMM yyyy, HH:mm", { locale: es })}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
                        {noticia.titulo}
                      </h3>
                      <p className="text-sm text-gray-400 line-clamp-3">
                        {noticia.resumen}
                      </p>
                    </div>
                    <a
                      href={noticia.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-shrink-0 p-2 hover:bg-dark-card rounded-lg transition-colors"
                    >
                      <ExternalLink className="w-5 h-5 text-gray-400 hover:text-accent-primary" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Estado Vacío */}
      {!loading && resultados.length === 0 && (query || palabrasClave) && (
        <Card>
          <CardContent className="text-center py-12">
            <Search className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">
              No se encontraron resultados para tu búsqueda
            </p>
          </CardContent>
        </Card>
      )}

      {/* Estado Inicial */}
      {!loading && resultados.length === 0 && !query && !palabrasClave && (
        <Card>
          <CardContent className="text-center py-12">
            <Search className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-2">Utiliza los filtros para buscar noticias</p>
            <p className="text-sm text-gray-500">
              Puedes buscar por texto, filtrar por fuente o rango de fechas
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};