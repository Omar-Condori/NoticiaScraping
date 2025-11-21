import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { Check, X, Clock } from 'lucide-react';

const PaymentTable = ({ pagos, onAprobar }) => {
  const getEstadoBadge = (estado) => {
    const badges = {
      'aprobado': { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400', icon: <Check className="w-3 h-3" /> },
      'pendiente': { bg: 'bg-gray-500/10', border: 'border-gray-500/30', text: 'text-gray-400', icon: <Clock className="w-3 h-3" /> },
      'pendiente_verificacion': { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', icon: <Clock className="w-3 h-3" /> },
      'rechazado': { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', icon: <X className="w-3 h-3" /> }
    };

    const textos = {
      'aprobado': 'Aprobado',
      'pendiente': 'Pendiente',
      'pendiente_verificacion': 'En verificación',
      'rechazado': 'Rechazado'
    };

    const badge = badges[estado] || badges['pendiente'];

    return (
      <span className={`px-3 py-1 inline-flex items-center gap-1.5 text-xs font-medium rounded-full border ${badge.bg} ${badge.border} ${badge.text}`}>
        {badge.icon}
        {textos[estado] || estado}
      </span>
    );
  };

  const getMetodoPagoBadge = (metodo) => {
    const badges = {
      'yape': { color: 'bg-purple-500/10 border-purple-500/30 text-purple-400', emoji: '📱' },
      'paypal': { color: 'bg-blue-500/10 border-blue-500/30 text-blue-400', emoji: '💰' },
      'stripe': { color: 'bg-green-500/10 border-green-500/30 text-green-400', emoji: '💳' }
    };

    const badge = badges[metodo.toLowerCase()] || { color: 'bg-gray-500/10 border-gray-500/30 text-gray-400', emoji: '💵' };

    return (
      <span className={`px-2 py-1 inline-flex items-center gap-1 text-xs font-medium rounded border ${badge.color} capitalize`}>
        <span>{badge.emoji}</span>
        {metodo}
      </span>
    );
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-dark-border">
        <h3 className="text-lg font-semibold text-white">
          💳 {onAprobar ? 'Pagos Pendientes de Aprobación' : 'Historial de Pagos'}
        </h3>
        <p className="text-sm text-gray-400 mt-1">
          {pagos.length} pago{pagos.length !== 1 ? 's' : ''} {onAprobar ? 'esperando verificación' : 'registrado(s)'}
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-dark-border">
          <thead className="bg-dark-hover">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Usuario
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Plan
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Monto
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Método
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Fecha
              </th>
              {onAprobar && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Acciones
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-border">
            {pagos.length === 0 ? (
              <tr>
                <td colSpan={onAprobar ? 8 : 7} className="px-6 py-12 text-center">
                  <div className="text-gray-500">
                    <p className="text-4xl mb-2">📭</p>
                    <p className="text-sm">No hay pagos para mostrar</p>
                  </div>
                </td>
              </tr>
            ) : (
              pagos.map((pago) => (
                <tr
                  key={pago.id}
                  className={`transition-colors ${pago.estado === 'pendiente_verificacion'
                    ? 'bg-orange-500/5 hover:bg-orange-500/10'
                    : 'hover:bg-dark-hover'
                    }`}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-300">
                    #{pago.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-white">
                      {pago.usuario}
                    </div>
                    {pago.email && (
                      <div className="text-xs text-gray-500">{pago.email}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    <span className="font-medium">{pago.plan}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-accent-primary">
                    S/ {pago.monto.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {getMetodoPagoBadge(pago.metodo_pago)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getEstadoBadge(pago.estado)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                    {formatDistanceToNow(new Date(pago.fecha_pago), {
                      addSuffix: true,
                      locale: es
                    })}
                  </td>
                  {onAprobar && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {(pago.estado === 'pendiente_verificacion' || pago.estado === 'pendiente') ? (
                        <button
                          onClick={() => onAprobar(pago.id)}
                          className="group relative inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white rounded-lg text-xs font-medium transition-all duration-200 shadow-lg hover:shadow-green-500/50"
                        >
                          <Check className="w-4 h-4" />
                          <span>Aprobar Pago</span>
                        </button>
                      ) : (
                        <span className="text-xs text-gray-500">-</span>
                      )}
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PaymentTable;