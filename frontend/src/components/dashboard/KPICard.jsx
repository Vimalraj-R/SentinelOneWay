import { TrendingUp, TrendingDown } from 'lucide-react';

export default function KPICard({ data, icon: Icon }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'text-green-500 bg-green-500/10 border-green-500/20';
      case 'warning':
        return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'danger':
        return 'text-red-500 bg-red-500/10 border-red-500/20';
      default:
        return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
    }
  };

  const getTrendColor = (trend) => {
    const isPositive = trend.startsWith('+');
    if (data.status === 'success') {
      return isPositive ? 'text-green-500' : 'text-red-500';
    }
    return isPositive ? 'text-red-500' : 'text-green-500';
  };

  const TrendIcon = data.trend?.startsWith('+') ? TrendingUp : TrendingDown;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-lg border ${getStatusColor(data.status)}`}>
          <Icon className="w-6 h-6" />
        </div>
        {data.trend && (
          <div className={`flex items-center gap-1 text-sm font-medium ${getTrendColor(data.trend)}`}>
            <TrendIcon className="w-4 h-4" />
            <span>{data.trend}</span>
          </div>
        )}
      </div>
      <div>
        <h3 className="text-gray-400 text-sm font-medium mb-1">{data.label}</h3>
        <div className="flex items-baseline gap-2">
          <p className="text-white text-3xl font-bold">{data.value}</p>
          {data.unit && <span className="text-gray-500 text-sm">{data.unit}</span>}
        </div>
      </div>
    </div>
  );
}
