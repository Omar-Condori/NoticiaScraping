import { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { obtenerPlanes } from '../services/api';
import { Crown, Check, Zap, Shield, Sparkles, AlertCircle } from 'lucide-react';
import PagoModal from '../components/PagoModal';

export default function Planes() {
  const { planActual, limiteFuentes, limiteScraping, actualizarPlan } = useApp();
  const [planes, setPlanes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showPagoModal, setShowPagoModal] = useState(false);

  useEffect(() => {
    cargarPlanes();
  }, []);

  const cargarPlanes = async () => {
    try {
      setLoading(true);
      const response = await obtenerPlanes();
      
      // Parsear las features desde JSON
      const planesConFeatures = response.planes.map(plan => ({
        ...plan,
        features: plan.features || []
      }));
      
      setPlanes(planesConFeatures);
    } catch (error) {
      console.error('Error cargando planes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = (plan) => {
    // No permitir "cambiar" al mismo plan
    if (planActual?.plan_id === plan.id) {
      return;
    }
    
    setSelectedPlan(plan);
    setShowPagoModal(true);
  };

  const handlePagoExitoso = async () => {
    setShowPagoModal(false);
    setSelectedPlan(null);
    await actualizarPlan();
  };

  const getBadgeStyle = (badgeColor) => {
    const styles = {
      gray: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
      blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      gold: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    };
    return styles[badgeColor] || styles.gray;
  };

  const getCardStyle = (destacado, isCurrentPlan) => {
    if (isCurrentPlan) {
      return 'border-green-500 ring-2 ring-green-500/20 bg-green-500/5';
    }
    if (destacado) {
      return 'border-accent-primary ring-2 ring-accent-primary/20 scale-105';
    }
    return 'border-light-border dark:border-dark-border hover:border-accent-primary/50';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent-primary/10 text-accent-primary rounded-full text-sm font-medium">
          <Crown className="w-4 h-4" />
          Elige el plan perfecto para ti
        </div>
        
        <h1 className="text-4xl font-bold text-white">
          Planes y Precios
        </h1>
        
        <p className="text-gray-400 max-w-2xl mx-auto">
          Comienza gratis y actualiza cuando necesites más funcionalidades. Todos los planes incluyen acceso completo a la plataforma.
        </p>
      </div>

      {/* Plan Actual Badge */}
      {planActual && (
        <div className="bg-light-card dark:bg-dark-card border border-green-500/30 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
              <Check className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-white font-medium">Plan Actual: {planActual.plan_nombre}</p>
              <p className="text-sm text-gray-400">
                {limiteFuentes?.limite === -1 ? 'Fuentes ilimitadas' : `${limiteFuentes?.actuales || 0} de ${limiteFuentes?.limite || 0} fuentes usadas`}
                {' · '}
                {limiteScraping?.limite_diario === -1 ? 'Scraping ilimitado' : `${limiteScraping?.usado_hoy || 0} de ${limiteScraping?.limite_diario || 0} noticias hoy`}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Planes Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {planes.map((plan) => {
          const isCurrentPlan = planActual?.plan_id === plan.id;
          const precio = parseFloat(plan.precio);
          const esGratis = precio === 0;
          const esMensual = precio > 0 && precio < 50;
          const esAnual = precio >= 50;

          // Calcular precio mensual para plan anual
          const precioMensual = esAnual ? (precio / 12).toFixed(2) : null;
          const ahorro = esAnual ? (9.99 * 12 - precio).toFixed(2) : null;

          return (
            <div
              key={plan.id}
              className={`
                relative bg-light-card dark:bg-dark-card rounded-xl border-2 p-6 
                transition-all duration-300 hover:shadow-xl
                ${getCardStyle(plan.destacado, isCurrentPlan)}
              `}
            >
              {/* Badge */}
              {plan.badge && (
                <div className={`
                  absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-xs font-bold border
                  ${getBadgeStyle(plan.badge_color)}
                `}>
                  {plan.badge}
                </div>
              )}

              {/* Current Plan Badge */}
              {isCurrentPlan && (
                <div className="absolute -top-3 right-4 px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full flex items-center gap-1">
                  <Check className="w-3 h-3" />
                  Plan Actual
                </div>
              )}

              <div className="space-y-6">
                {/* Header */}
                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-white">{plan.nombre}</h3>
                  <p className="text-gray-400 text-sm min-h-[40px]">{plan.descripcion}</p>
                </div>

                {/* Precio */}
                <div className="space-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-white">
                      ${precio.toFixed(2)}
                    </span>
                    <span className="text-gray-400">
                      /{esAnual ? 'año' : 'mes'}
                    </span>
                  </div>
                  
                  {/* Precio mensual equivalente para plan anual */}
                  {esAnual && precioMensual && (
                    <p className="text-sm text-gray-400">
                      Solo ${precioMensual}/mes
                    </p>
                  )}
                  
                  {/* Ahorro */}
                  {esAnual && ahorro && (
                    <div className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/10 text-green-400 rounded-full text-xs font-medium">
                      <Sparkles className="w-3 h-3" />
                      Ahorra ${ahorro} al año
                    </div>
                  )}
                </div>

                {/* Features */}
                <ul className="space-y-3">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-300 text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* Botón */}
                <button
                  onClick={() => handleSelectPlan(plan)}
                  disabled={isCurrentPlan || (esGratis && planActual)}
                  className={`
                    w-full py-3 rounded-lg font-semibold transition-all duration-200
                    ${
                      isCurrentPlan
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : plan.destacado
                        ? 'bg-gradient-to-r from-accent-primary to-accent-secondary text-white hover:shadow-lg hover:scale-105'
                        : 'bg-light-hover dark:bg-dark-hover text-white hover:bg-light-border dark:hover:bg-dark-border'
                    }
                  `}
                >
                  {isCurrentPlan ? (
                    'Plan Actual'
                  ) : esGratis && planActual ? (
                    'Ya tienes un plan'
                  ) : esGratis ? (
                    'Comenzar Gratis'
                  ) : plan.destacado ? (
                    'Actualizar Ahora'
                  ) : (
                    'Seleccionar Plan'
                  )}
                </button>

                {/* Nota para plan gratis */}
                {esGratis && !isCurrentPlan && (
                  <p className="text-xs text-gray-500 text-center">
                    No se requiere tarjeta de crédito
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Features Comparison */}
      <div className="bg-light-card dark:bg-dark-card border border-light-border dark:border-dark-border rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5 text-accent-primary" />
          Todos los planes incluyen
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="flex items-center gap-3">
            <Zap className="w-5 h-5 text-yellow-400" />
            <span className="text-gray-300">Scraping de noticias en tiempo real</span>
          </div>
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-blue-400" />
            <span className="text-gray-300">Análisis de sentimiento de noticias</span>
          </div>
          <div className="flex items-center gap-3">
            <Check className="w-5 h-5 text-green-400" />
            <span className="text-gray-300">Exportación de datos</span>
          </div>
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <span className="text-gray-300">Actualizaciones automáticas</span>
          </div>
        </div>
      </div>

      {/* FAQ / Info */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-2">
            <h4 className="text-white font-semibold">¿Necesitas ayuda para elegir?</h4>
            <p className="text-gray-300 text-sm">
              Comienza con el plan gratuito y actualiza cuando necesites más fuentes o scraping. 
              Puedes cambiar de plan en cualquier momento sin perder tus datos.
            </p>
          </div>
        </div>
      </div>

      {/* Modal de Pago */}
      {showPagoModal && selectedPlan && (
        <PagoModal
          plan={selectedPlan}
          onClose={() => {
            setShowPagoModal(false);
            setSelectedPlan(null);
          }}
          onSuccess={handlePagoExitoso}
        />
      )}
    </div>
  );
}