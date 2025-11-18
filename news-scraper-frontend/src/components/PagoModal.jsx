import { useState } from 'react';
import { X, CreditCard, Smartphone, DollarSign, Check, Loader, AlertCircle } from 'lucide-react';
import { pagosAPI } from '../services/api'; // ← CORREGIDO

export default function PagoModal({ plan, onClose, onSuccess }) {
  const [metodoPago, setMetodoPago] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagoCreado, setPagoCreado] = useState(null);
  const [qrData, setQrData] = useState(null);

  const metodosPago = [
    {
      id: 'yape',
      nombre: 'Yape',
      descripcion: 'Pago con código QR',
      icon: Smartphone,
      color: 'bg-purple-500',
      disponible: true,
    },
    {
      id: 'paypal',
      nombre: 'PayPal',
      descripcion: 'Pago internacional seguro',
      icon: DollarSign,
      color: 'bg-blue-500',
      disponible: true,
    },
    {
      id: 'stripe',
      nombre: 'Tarjeta',
      descripcion: 'Visa, Mastercard, etc.',
      icon: CreditCard,
      color: 'bg-green-500',
      disponible: true,
    },
  ];

  const handleSelectMetodo = async (metodo) => {
    setMetodoPago(metodo);
    setError(null);
    
    if (metodo === 'yape') {
      await procesarPagoYape();
    }
  };

  const procesarPagoYape = async () => {
    try {
      setLoading(true);
      setError(null);

      // ← CORREGIDO: pagosAPI.crear()
      const response = await pagosAPI.crear({
        plan_id: plan.id,
        metodo_pago: 'yape'
      });
      
      if (response.data.success) {
        setPagoCreado(response.data);
        setQrData(response.data.qr_data);
      } else {
        setError(response.data.error || 'Error al crear el pago');
      }
    } catch (error) {
      console.error('Error procesando pago Yape:', error);
      setError(error.response?.data?.error || 'Error al procesar el pago');
    } finally {
      setLoading(false);
    }
  };

  const confirmarPagoYape = async () => {
    try {
      setLoading(true);
      setError(null);

      // ← CORREGIDO: pagosAPI.verificarYape()
      const response = await pagosAPI.verificarYape({
        pago_id: pagoCreado.pago_id
      });
      
      if (response.data.success) {
        alert('¡Comprobante enviado! Tu pago será verificado en las próximas 24 horas.');
        onSuccess();
      } else {
        setError(response.data.error || 'Error al verificar el pago');
      }
    } catch (error) {
      console.error('Error confirmando pago Yape:', error);
      setError(error.response?.data?.error || 'Error al confirmar el pago');
    } finally {
      setLoading(false);
    }
  };

  const procesarPagoPayPal = async () => {
    try {
      setLoading(true);
      setError(null);

      // ← CORREGIDO: pagosAPI.crear()
      const response = await pagosAPI.crear({
        plan_id: plan.id,
        metodo_pago: 'paypal'
      });
      
      if (response.data.success && response.data.approval_url) {
        window.location.href = response.data.approval_url;
      } else {
        setError(response.data.error || 'Error al crear el pago con PayPal');
      }
    } catch (error) {
      console.error('Error procesando pago PayPal:', error);
      setError(error.response?.data?.error || 'Error al procesar el pago con PayPal');
      setLoading(false);
    }
  };

  const procesarPagoStripe = async () => {
    try {
      setLoading(true);
      setError(null);

      // ← CORREGIDO: pagosAPI.crear()
      const response = await pagosAPI.crear({
        plan_id: plan.id,
        metodo_pago: 'stripe'
      });
      
      if (response.data.success && response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else {
        setError(response.data.error || 'Error al crear el pago con Stripe');
      }
    } catch (error) {
      console.error('Error procesando pago Stripe:', error);
      setError(error.response?.data?.error || 'Error al procesar el pago con Stripe');
      setLoading(false);
    }
  };

  const handleContinuar = () => {
    if (metodoPago === 'paypal') {
      procesarPagoPayPal();
    } else if (metodoPago === 'stripe') {
      procesarPagoStripe();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-light-card dark:bg-dark-card border border-light-border dark:border-dark-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-light-card dark:bg-dark-card border-b border-light-border dark:border-dark-border p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">Completar Pago</h2>
            <p className="text-gray-400 text-sm mt-1">
              Plan: {plan.nombre} - ${parseFloat(plan.precio).toFixed(2)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-400" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Error */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-red-400 font-semibold">Error</h4>
                <p className="text-gray-300 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Selección de Método de Pago */}
          {!qrData && (
            <>
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">
                  Selecciona tu método de pago
                </h3>
                <div className="grid gap-3">
                  {metodosPago.map((metodo) => {
                    const Icon = metodo.icon;
                    const isSelected = metodoPago === metodo.id;

                    return (
                      <button
                        key={metodo.id}
                        onClick={() => handleSelectMetodo(metodo.id)}
                        disabled={!metodo.disponible || loading}
                        className={`
                          relative p-4 rounded-lg border-2 transition-all duration-200
                          ${
                            isSelected
                              ? 'border-accent-primary bg-accent-primary/10'
                              : 'border-light-border dark:border-dark-border hover:border-accent-primary/50'
                          }
                          ${!metodo.disponible ? 'opacity-50 cursor-not-allowed' : ''}
                        `}
                      >
                        <div className="flex items-center gap-4">
                          <div className={`w-12 h-12 ${metodo.color} rounded-lg flex items-center justify-center`}>
                            <Icon className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1 text-left">
                            <h4 className="text-white font-semibold">{metodo.nombre}</h4>
                            <p className="text-gray-400 text-sm">{metodo.descripcion}</p>
                          </div>
                          {isSelected && (
                            <div className="w-6 h-6 bg-accent-primary rounded-full flex items-center justify-center">
                              <Check className="w-4 h-4 text-white" />
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Botón Continuar */}
              {metodoPago && metodoPago !== 'yape' && (
                <button
                  onClick={handleContinuar}
                  disabled={loading}
                  className="w-full py-3 bg-gradient-to-r from-accent-primary to-accent-secondary text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Procesando...
                    </>
                  ) : (
                    <>
                      Continuar con {metodoPago === 'paypal' ? 'PayPal' : 'Stripe'}
                    </>
                  )}
                </button>
              )}
            </>
          )}

          {/* Vista de Yape (QR) */}
          {qrData && (
            <div className="space-y-6">
              <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-6 text-center space-y-4">
                <Smartphone className="w-12 h-12 text-purple-400 mx-auto" />
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Escanea el código QR</h3>
                  <p className="text-gray-300 text-sm">
                    Abre tu app de Yape y escanea este código para completar el pago
                  </p>
                </div>

                {/* QR Code */}
                <div className="bg-white p-6 rounded-lg inline-block">
                  <div className="w-48 h-48 flex items-center justify-center">
                    {qrData.qr_base64 ? (
                      <img 
                        src={`data:image/png;base64,${qrData.qr_base64}`}
                        alt="QR Code Yape"
                        className="w-full h-full"
                      />
                    ) : (
                      <div className="text-center text-gray-500 text-sm">
                        Código QR no disponible
                      </div>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="text-3xl font-bold text-white">
                    S/ {parseFloat(plan.precio).toFixed(2)}
                  </div>
                  <p className="text-gray-400 text-sm">
                    Monto a pagar
                  </p>
                </div>
              </div>

              {/* Instrucciones */}
              <div className="bg-light-hover dark:bg-dark-hover rounded-lg p-4">
                <h4 className="text-white font-semibold mb-3">Instrucciones:</h4>
                <ol className="space-y-2 text-gray-300 text-sm list-decimal list-inside">
                  <li>Abre tu aplicación de Yape</li>
                  <li>Escanea el código QR mostrado arriba</li>
                  <li>Confirma el pago en tu app</li>
                  <li>Haz clic en "Ya realicé el pago" abajo</li>
                </ol>
              </div>

              {/* Botón Confirmar Pago */}
              <button
                onClick={confirmarPagoYape}
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-accent-primary to-accent-secondary text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Verificando...
                  </>
                ) : (
                  <>
                    <Check className="w-5 h-5" />
                    Ya realicé el pago
                  </>
                )}
              </button>

              <p className="text-xs text-gray-500 text-center">
                Tu pago será verificado en las próximas 24 horas y tu plan se activará automáticamente
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}