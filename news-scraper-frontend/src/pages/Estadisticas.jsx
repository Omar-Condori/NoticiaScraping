import { useState, useEffect } from 'react';
import { estadisticasAPI } from '../services/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/StatsCard';
import { Select } from '../components/ui/Input';
import Badge from '../components/ui/Badge';
import { CardSkeleton } from '../components/ui/Skeleton';
import { TrendingUp, Award, Calendar } from 'lucide-react';
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer 
} from 'recharts';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

export default function Estadisticas(){
  const [estadisticas, setEstadisticas] = useState(null);
  const [tendencias, setTendencias] = useState([]);
  const [topFuentes, setTopFuentes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [diasTendencias, setDiasTendencias] = useState(7);
  const [limiteFuentes, setLimiteFuentes] = useState(5);

  useEffect(() => {
    cargarDatos();
  }, [diasTendencias, limiteFuentes]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [statsRes, tendenciasRes, topRes] = await Promise.all([
        estadisticasAPI.generales(),
        estadisticasAPI.tendencias(diasTendencias),
        estadisticasAPI.topFuentes(limiteFuentes)
      ]);

      setEstadisticas(statsRes.estadisticas);
      setTendencias(tendenciasRes.tendencias || []);
      setTopFuentes(topRes.top_fuentes || []);
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  // Preparar datos para gráfico de pastel
  const pieData = estadisticas?.por_fuente?.slice(0, 5).map((fuente, index) => ({
    name: fuente.fuente,
    value: fuente.total,
    color: COLORS[index % COLORS.length]
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Estadísticas</h1>
        <p className="text-gray-400">Análisis detallado del sistema de scraping</p>
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card hover>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Total Noticias</p>
              <p className="text-3xl font-bold text-white">
                {estadisticas?.resumen?.total_noticias || 0}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-accent-primary" />
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Fuentes Activas</p>
              <p className="text-3xl font-bold text-white">
                {estadisticas?.resumen?.fuentes_activas || 0}
              </p>
            </div>
            <Award className="w-8 h-8 text-accent-success" />
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Últimas 24h</p>
              <p className="text-3xl font-bold text-white">
                {estadisticas?.resumen?.noticias_24h || 0}
              </p>
            </div>
            <Calendar className="w-8 h-8 text-accent-warning" />
          </div>
        </Card>

        <Card hover>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Esta Semana</p>
              <p className="text-3xl font-bold text-white">
                {estadisticas?.resumen?.noticias_semana || 0}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-accent-secondary" />
          </div>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tendencias */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Tendencias</CardTitle>
                <CardDescription>Noticias scrapeadas por día</CardDescription>
              </div>
              <Select
                value={diasTendencias}
                onChange={(e) => setDiasTendencias(parseInt(e.target.value))}
                className="w-32"
              >
                <option value={7}>7 días</option>
                <option value={14}>14 días</option>
                <option value={30}>30 días</option>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={tendencias}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" />
                <XAxis 
                  dataKey="fecha" 
                  stroke="#6b7280"
                  tickFormatter={(date) => format(new Date(date), 'dd MMM', { locale: es })}
                />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#121218', 
                    border: '1px solid #2a2a35',
                    borderRadius: '8px'
                  }}
                  labelStyle={{ color: '#fff' }}
                  labelFormatter={(date) => format(new Date(date), "dd 'de' MMMM", { locale: es })}
                />
                <Line 
                  type="monotone" 
                  dataKey="total" 
                  stroke="#6366f1" 
                  strokeWidth={3}
                  dot={{ fill: '#6366f1', r: 5 }}
                  name="Noticias"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Fuentes (Barras) */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Top Fuentes</CardTitle>
                <CardDescription>Ranking por cantidad de noticias</CardDescription>
              </div>
              <Select
                value={limiteFuentes}
                onChange={(e) => setLimiteFuentes(parseInt(e.target.value))}
                className="w-32"
              >
                <option value={5}>Top 5</option>
                <option value={10}>Top 10</option>
                <option value={15}>Top 15</option>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topFuentes} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" />
                <XAxis type="number" stroke="#6b7280" />
                <YAxis 
                  type="category" 
                  dataKey="nombre" 
                  stroke="#6b7280"
                  width={100}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#121218', 
                    border: '1px solid #2a2a35',
                    borderRadius: '8px'
                  }}
                />
                <Bar 
                  dataKey="total_noticias" 
                  fill="#10b981" 
                  radius={[0, 8, 8, 0]}
                  name="Noticias"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Distribución (Pastel) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Distribución por Fuente</CardTitle>
            <CardDescription>Proporción de noticias por fuente</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#121218', 
                    border: '1px solid #2a2a35',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Tabla de Fuentes */}
        <Card>
          <CardHeader>
            <CardTitle>Detalle de Fuentes</CardTitle>
            <CardDescription>Listado completo con métricas</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topFuentes.map((fuente, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 bg-dark-hover rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    >
                      {index + 1}
                    </div>
                    <div>
                      <p className="text-white font-medium">{fuente.nombre}</p>
                      <p className="text-xs text-gray-500">
                        {fuente.ultima_actualizacion && 
                          format(new Date(fuente.ultima_actualizacion), "dd MMM, HH:mm", { locale: es })
                        }
                      </p>
                    </div>
                  </div>
                  <Badge variant="primary">
                    {fuente.total_noticias} noticias
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};