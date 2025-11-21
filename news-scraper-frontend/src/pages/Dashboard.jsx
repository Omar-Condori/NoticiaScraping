import { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, PieChart, Pie, Cell
} from 'recharts';
import {
  BarChart3, TrendingUp, Activity, Globe,
  MessageSquare, Zap, Smile, Frown, Meh, Brain, Lightbulb, AlertTriangle
} from 'lucide-react';
import Skeleton from '../components/ui/Skeleton';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const response = await dashboardAPI.obtenerResumen();
        if (response.data.success) {
          setData(response.data.data);
        } else {
          throw new Error('Error al cargar datos del dashboard');
        }
      } catch (err) {
        console.error('Error cargando dashboard:', err);
        setError('No se pudieron cargar las métricas personalizadas.');
      } finally {
        setLoading(false);
      }
    };

    cargarDatos();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80" />
          <Skeleton className="h-80" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-500/10 border border-red-500/50 rounded-xl text-red-500">
        {error}
      </div>
    );
  }

  if (!data) return null;

  // Datos para Gauge Chart (Termómetro)
  const gaugeValue = data.ia_insights?.termometro || 50;
  const gaugeData = [
    { name: 'Valor', value: gaugeValue },
    { name: 'Restante', value: 100 - gaugeValue }
  ];
  const gaugeColors = [gaugeValue > 60 ? '#10B981' : gaugeValue < 40 ? '#EF4444' : '#F59E0B', '#374151'];

  // Datos para Radar Chart (Mock o reales si hubiera)
  const radarData = [
    { subject: 'Política', A: 120, fullMark: 150 },
    { subject: 'Economía', A: 98, fullMark: 150 },
    { subject: 'Tecnología', A: 86, fullMark: 150 },
    { subject: 'Deportes', A: 99, fullMark: 150 },
    { subject: 'Salud', A: 85, fullMark: 150 },
    { subject: 'Cultura', A: 65, fullMark: 150 },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Brain className="w-8 h-8 text-purple-500" />
          Centro de Inteligencia
        </h1>
        <p className="text-gray-400 mt-1">Análisis predictivo y métricas en tiempo real</p>
      </div>

      {/* ==================== SECCIÓN DE PREDICCIÓN E IA (NUEVO) ==================== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* 1. Radar de Proyección (Momentum) */}
        <div className="lg:col-span-2 bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-3 py-1 bg-purple-500/20 text-purple-300 text-xs font-bold rounded-full border border-purple-500/30 uppercase tracking-wider">
                  IA Forecast
                </span>
                <span className="text-gray-400 text-xs">Proyección de Categorías</span>
              </div>
              <h3 className="text-xl font-bold text-white">Radar de Proyección</h3>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-500 opacity-50" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            {/* Gráfico Radar */}
            <div className="h-[250px] w-full relative">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data.prediccion?.datos_radar || []}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 'auto']} tick={false} axisLine={false} />
                  <Radar name="Volumen Hoy" dataKey="hoy" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
                  <Radar name="Proyección Mañana" dataKey="proyeccion" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#fff' }}
                    itemStyle={{ color: '#fff' }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Texto Predictivo */}
            <div>
              <p className="text-gray-300 text-lg leading-relaxed">
                El sistema predice que <span className="text-purple-400 font-bold text-xl">{data.prediccion?.tema || "..."}</span> dominará la conversación mañana debido a su inercia actual.
              </p>

              <div className="mt-6 space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-[#8884d8]"></div>
                  <span className="text-sm text-gray-400">Volumen Hoy</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-[#10B981]"></div>
                  <span className="text-sm text-gray-400">Proyección Mañana (Momentum)</span>
                </div>
              </div>

              {data.prediccion?.probabilidad > 0 && (
                <div className="mt-6 p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg flex items-center gap-3">
                  <Brain className="w-5 h-5 text-purple-400" />
                  <span className="text-purple-200 text-sm font-medium">
                    Confianza del modelo: {Math.round(data.prediccion.probabilidad)}%
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 2. Termómetro de Sentimiento Global (Gauge) */}
        <div className="bg-dark-card border border-dark-border rounded-2xl p-6 flex flex-col items-center justify-center relative">
          <h3 className="text-gray-300 font-medium mb-2 w-full text-left flex items-center gap-2">
            <Smile className="w-4 h-4 text-yellow-500" /> Humor de tus Fuentes
          </h3>

          <div className="h-[180px] w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={gaugeData}
                  cx="50%"
                  cy="70%"
                  startAngle={180}
                  endAngle={0}
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={0}
                  dataKey="value"
                  stroke="none"
                >
                  {gaugeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={gaugeColors[index]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute bottom-0 left-0 w-full text-center pb-4">
              <span className="text-3xl font-bold text-white">{gaugeValue}</span>
              <span className="text-gray-500 text-sm">/100</span>
              <p className={`text-sm font-medium mt-1 ${gaugeValue > 60 ? 'text-green-400' : gaugeValue < 40 ? 'text-red-400' : 'text-yellow-400'}`}>
                {gaugeValue > 60 ? 'Positivo' : gaugeValue < 40 ? 'Negativo' : 'Neutro'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ==================== SECCIÓN INFERIOR (SUGERENCIAS Y ALERTA S) ==================== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* 3. Auto-Clasificador Inteligente */}
        <div className="lg:col-span-2 bg-dark-card border border-dark-border rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-400" />
              Sugerencias de la IA
            </h3>
            <span className="text-xs text-gray-500">Basado en tu historial</span>
          </div>

          <div className="space-y-4">
            {data.ia_insights?.sugerencias?.length > 0 ? (
              data.ia_insights.sugerencias.map((sug) => (
                <div key={sug.id} className="flex items-start justify-between p-4 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                  <div>
                    <h4 className="text-white font-medium text-sm mb-1 line-clamp-1">{sug.titulo}</h4>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400 text-xs">Categoría actual: <span className="text-red-400">Sin categoría</span></span>
                      <span className="text-gray-600 text-xs">→</span>
                      <span className="text-green-400 text-xs font-bold">{sug.categoria_sugerida}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-xs font-bold text-purple-400">{sug.confianza}%</span>
                    <span className="text-[10px] text-gray-500">coincidencia</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No hay noticias sin categorizar o sugerencias disponibles.</p>
              </div>
            )}
          </div>
        </div>

        {/* 4. Alertas de Sentimiento */}
        <div className="bg-dark-card border border-dark-border rounded-2xl p-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-6">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            Alertas de Riesgo
          </h3>

          <div className="space-y-3">
            {data.ia_insights?.alertas?.length > 0 ? (
              data.ia_insights.alertas.slice(0, 3).map((alerta, idx) => (
                <div key={idx} className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                  <div className="flex items-start gap-3">
                    <div className="mt-1">
                      <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    </div>
                    <div>
                      <p className="text-red-200 text-sm font-medium">{alerta.mensaje}</p>
                      <span className="text-xs text-red-400/70 mt-1 block">Nivel de riesgo: {alerta.nivel}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                <Smile className="w-10 h-10 mb-2 opacity-20" />
                <p className="text-sm">No se detectan alertas de riesgo.</p>
                <p className="text-xs opacity-50">Tus fuentes parecen estables.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Gráficos Clásicos (Volumen y Nube) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Volumen por Hora */}
        <div className="bg-dark-card border border-dark-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Volumen de Noticias por Hora</h3>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.volumen_horas}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                <XAxis dataKey="hora" stroke="#9CA3AF" tick={{ fill: '#9CA3AF', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis stroke="#9CA3AF" tick={{ fill: '#9CA3AF', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#fff' }} itemStyle={{ color: '#fff' }} />
                <Line type="monotone" dataKey="cantidad" stroke="#3B82F6" strokeWidth={3} dot={{ r: 4, fill: '#3B82F6', strokeWidth: 2, stroke: '#1F2937' }} activeDot={{ r: 6, fill: '#60A5FA' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Nube de Palabras */}
        <div className="bg-dark-card border border-dark-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Nube de Palabras Clave</h3>
          <div className="h-[250px] flex flex-wrap content-center justify-center gap-3 overflow-hidden">
            {data.nube_palabras.map((word, index) => {
              const size = Math.max(0.8, Math.min(2.5, word.value / 10));
              const opacity = Math.max(0.4, Math.min(1, word.value / 20));
              const colors = ['text-blue-400', 'text-purple-400', 'text-green-400', 'text-pink-400', 'text-yellow-400'];
              const color = colors[index % colors.length];
              return (
                <span key={index} className={`${color} font-bold transition-all hover:scale-110 cursor-default`} style={{ fontSize: `${size}rem`, opacity: opacity }} title={`${word.text}: ${word.value} ocurrencias`}>
                  {word.text}
                </span>
              );
            })}
            {data.nube_palabras.length === 0 && <p className="text-gray-500">No hay suficientes datos para generar la nube.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}