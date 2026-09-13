import { Brain, AlertTriangle, TrendingUp, Zap } from 'lucide-react';

export default function AIInsightPanel({ insights }) {
  const getIcon = (type) => {
    switch (type) {
      case 'anomaly':
        return TrendingUp;
      case 'correlation':
        return Zap;
      case 'prediction':
        return AlertTriangle;
      default:
        return Brain;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'border-red-500/50 bg-red-500/5';
      case 'high':
        return 'border-orange-500/50 bg-orange-500/5';
      case 'warning':
        return 'border-yellow-500/50 bg-yellow-500/5';
      default:
        return 'border-blue-500/50 bg-blue-500/5';
    }
  };

  const getIconColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'text-red-400';
      case 'high':
        return 'text-orange-400';
      case 'warning':
        return 'text-yellow-400';
      default:
        return 'text-blue-400';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Brain className="w-5 h-5 text-purple-400" />
        <h3 className="text-white font-semibold">AI Insights</h3>
      </div>

      <div className="space-y-3">
        {insights.map((insight) => {
          const Icon = getIcon(insight.type);
          return (
            <div
              key={insight.id}
              className={`p-4 rounded-lg border ${getSeverityColor(insight.severity)}`}
            >
              <div className="flex items-start gap-3">
                <Icon className={`w-5 h-5 mt-0.5 ${getIconColor(insight.severity)}`} />
                <div className="flex-1">
                  <h4 className="text-white font-medium mb-1">{insight.title}</h4>
                  <p className="text-gray-400 text-sm mb-2">{insight.description}</p>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-gray-500">{insight.timestamp}</span>
                    <span className="text-gray-500">•</span>
                    <span className="text-gray-400">
                      Confidence: {(insight.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
