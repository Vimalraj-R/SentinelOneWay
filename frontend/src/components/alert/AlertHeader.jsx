import { ArrowLeft, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function AlertHeader({ alert }) {
  const navigate = useNavigate();

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'high':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      case 'medium':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'low':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-red-500/10 text-red-400';
      case 'investigating':
        return 'bg-yellow-500/10 text-yellow-400';
      case 'resolved':
        return 'bg-green-500/10 text-green-400';
      default:
        return 'bg-gray-500/10 text-gray-400';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      dateStyle: 'medium',
      timeStyle: 'medium'
    });
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back</span>
      </button>

      {/* Alert Title and Badges */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-3">{alert.threat}</h1>
          <div className="flex items-center gap-3">
            <span
              className={`inline-flex px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(
                alert.severity
              )}`}
            >
              {alert.severity}
            </span>
            <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(alert.status)}`}>
              {alert.status}
            </span>
            <div className="flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-full">
              <CheckCircle className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-gray-300">
                Confidence: {(alert.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        {/* Detection Time */}
        <div className="text-right">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Clock className="w-4 h-4" />
            <span className="text-sm">Detected</span>
          </div>
          <p className="text-white font-medium">{formatTimestamp(alert.detectedAt)}</p>
        </div>
      </div>

      {/* Alert ID */}
      <div className="pt-4 border-t border-gray-800">
        <span className="text-gray-400 text-sm">Alert ID: </span>
        <span className="text-gray-300 font-mono text-sm">{alert.network.flowId}</span>
      </div>
    </div>
  );
}
