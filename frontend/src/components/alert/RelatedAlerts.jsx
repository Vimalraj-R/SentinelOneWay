import { Link } from 'react-router-dom';
import { AlertTriangle, ExternalLink } from 'lucide-react';

export default function RelatedAlerts({ alerts }) {
  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'text-red-400';
      case 'high':
        return 'text-orange-400';
      case 'medium':
        return 'text-yellow-400';
      case 'low':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <AlertTriangle className="w-5 h-5 text-orange-400" />
        <h2 className="text-xl font-semibold text-white">Related Alerts</h2>
      </div>

      {alerts.length === 0 ? (
        <p className="text-gray-400 text-center py-4">No related alerts found</p>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <Link
              key={alert.id}
              to={`/alert/${alert.id}`}
              className="block p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-gray-600 hover:bg-gray-800 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-white font-medium">{alert.threat}</span>
                    <span className={`text-sm font-medium ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-gray-400">
                    <span className="font-mono">{alert.time}</span>
                    <span>→</span>
                    <span className="font-mono">{alert.target}</span>
                  </div>
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
