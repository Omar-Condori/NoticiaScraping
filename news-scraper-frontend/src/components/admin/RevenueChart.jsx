import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const RevenueChart = ({ ingresos }) => {
  // Transformar datos para el gráfico
  const data = ingresos.map(item => ({
    mes: formatMes(item.mes),
    ingresos: item.ingresos,
    pagos: item.total_pagos
  }));

  function formatMes(mesStr) {
    const [year, month] = mesStr.split('-');
    const meses = {
      '01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr',
      '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Ago',
      '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'
    };
    return `${meses[month]} ${year}`;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          📈 Ingresos Mensuales
        </h3>
        <p className="text-sm text-gray-600">
          Últimos 6 meses
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="mes" />
          <YAxis />
          <Tooltip 
            formatter={(value, name) => {
              if (name === 'ingresos') return [`S/ ${value.toFixed(2)}`, 'Ingresos'];
              return [value, 'Pagos'];
            }}
          />
          <Legend />
          <Bar dataKey="ingresos" fill="#8b5cf6" name="Ingresos" />
          <Bar dataKey="pagos" fill="#3b82f6" name="Pagos" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RevenueChart;