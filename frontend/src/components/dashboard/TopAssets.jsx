import { Server, AlertCircle } from 'lucide-react';

export default function TopAssets({ assets }) {
  const getRiskColor = (risk) => {
    switch (risk.toLowerCase()) {
      case 'critical':
        return 'text-red-400 bg-red-500/10';
      case 'high':
        return 'text-orange-400 bg-orange-500/10';
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/10';
      case 'low':
        return 'text-green-400 bg-green-500/10';
      default:
        return 'text-gray-400 bg-gray-500/10';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-white font-semibold">Top Targeted Assets</h3>
        <Server className="w-5 h-5 text-gray-400" />
      </div>

      <div className="space-y-3">
        {assets.map((asset, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-white font-medium">{asset.hostname}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${getRiskColor(asset.risk)}`}>
                  {asset.risk}
                </span>
              </div>
              <span className="text-gray-400 text-sm font-mono">{asset.ip}</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <span className="text-red-400 font-semibold">{asset.alerts}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
