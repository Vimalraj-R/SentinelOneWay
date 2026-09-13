/**
 * Empty State Component
 * Clear, helpful empty states across the application
 */
import { Shield, Activity, Clock, AlertTriangle } from 'lucide-react';

export default function EmptyState({
  type = 'default',
  title,
  description,
  icon: CustomIcon,
  action
}) {
  const configs = {
    alerts: {
      icon: Shield,
      title: title || 'No Threats Detected',
      description: description || 'Network traffic appears normal. Monitoring continues.',
      color: 'text-green-400'
    },
    incidents: {
      icon: Clock,
      title: title || 'No Multi-Stage Attacks',
      description: description || 'No correlated attack patterns detected.',
      color: 'text-blue-400'
    },
    traffic: {
      icon: Activity,
      title: title || 'No Traffic Data',
      description: description || 'Waiting for network flow data...',
      color: 'text-gray-400'
    },
    error: {
      icon: AlertTriangle,
      title: title || 'Unable to Load Data',
      description: description || 'Check backend connection and try again.',
      color: 'text-yellow-400'
    },
    default: {
      icon: Activity,
      title: title || 'No Data Available',
      description: description || 'Nothing to display at this time.',
      color: 'text-gray-400'
    }
  };

  const config = configs[type] || configs.default;
  const Icon = CustomIcon || config.icon;

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <Icon className={`w-16 h-16 mb-4 ${config.color} opacity-50`} />
      <h3 className="text-lg font-semibold text-white mb-2">
        {config.title}
      </h3>
      <p className="text-gray-400 max-w-md mb-4">
        {config.description}
      </p>
      {action && (
        <div className="mt-4">
          {action}
        </div>
      )}
    </div>
  );
}
