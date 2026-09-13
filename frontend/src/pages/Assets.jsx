/**
 * Assets Page - Network asset inventory
 */
import { Server, Shield, AlertTriangle, Search } from 'lucide-react';

export default function Assets() {
  const assets = [
    { id: 1, ip: '192.168.1.10', hostname: 'web-server-01', type: 'Server', risk_level: 'Medium', alerts: 3, last_seen: '2 min ago' },
    { id: 2, ip: '192.168.1.20', hostname: 'db-primary', type: 'Database', risk_level: 'High', alerts: 5, last_seen: '1 min ago' },
    { id: 3, ip: '192.168.1.30', hostname: 'app-server-01', type: 'Application', risk_level: 'Low', alerts: 0, last_seen: '5 min ago' },
    { id: 4, ip: '192.168.1.40', hostname: 'firewall-01', type: 'Network', risk_level: 'Critical', alerts: 12, last_seen: 'Just now' },
    { id: 5, ip: '192.168.1.50', hostname: 'workstation-05', type: 'Workstation', risk_level: 'Medium', alerts: 2, last_seen: '10 min ago' },
    { id: 6, ip: '192.168.1.60', hostname: 'mail-server', type: 'Server', risk_level: 'Low', alerts: 1, last_seen: '3 min ago' },
    { id: 7, ip: '192.168.1.70', hostname: 'backup-server', type: 'Storage', risk_level: 'Low', alerts: 0, last_seen: '15 min ago' },
    { id: 8, ip: '192.168.1.80', hostname: 'dns-server', type: 'Infrastructure', risk_level: 'Medium', alerts: 4, last_seen: '2 min ago' },
  ];

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Critical': return 'border-red-500 bg-red-500/10';
      case 'High': return 'border-orange-500 bg-orange-500/10';
      case 'Medium': return 'border-yellow-500 bg-yellow-500/10';
      case 'Low': return 'border-green-500 bg-green-500/10';
      default: return 'border-gray-500 bg-gray-500/10';
    }
  };

  const getRiskTextColor = (risk) => {
    switch (risk) {
      case 'Critical': return 'text-red-400';
      case 'High': return 'text-orange-400';
      case 'Medium': return 'text-yellow-400';
      case 'Low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Server className="w-8 h-8 text-purple-400" />
          Network Assets
        </h1>
        <p className="text-gray-400 mt-1">
          Network asset inventory and risk profiling
        </p>
      </div>

      {/* Passive Monitoring Banner */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg px-4 py-2">
        <div className="flex items-center gap-2 text-sm">
          <Shield className="w-4 h-4 text-blue-400 flex-shrink-0" />
          <span className="text-blue-300 font-medium">Passive Monitoring</span>
          <span className="text-gray-400">•</span>
          <span className="text-gray-400">
            Read-only network observation. No active blocking or response.
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Total Assets</div>
          <div className="text-2xl font-bold text-white mt-1">{assets.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-500/30">
          <div className="text-gray-400 text-sm">Critical Risk</div>
          <div className="text-2xl font-bold text-red-400 mt-1">
            {assets.filter(a => a.risk_level === 'Critical').length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-orange-500/30">
          <div className="text-gray-400 text-sm">High Risk</div>
          <div className="text-2xl font-bold text-orange-400 mt-1">
            {assets.filter(a => a.risk_level === 'High').length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-blue-500/30">
          <div className="text-gray-400 text-sm">Active Monitoring</div>
          <div className="text-2xl font-bold text-blue-400 mt-1">
            {assets.length}
          </div>
        </div>
      </div>

      {/* Assets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {assets.map((asset) => (
          <div
            key={asset.id}
            className={`bg-gray-800 rounded-lg p-5 border hover:border-blue-500 transition-colors cursor-pointer ${getRiskColor(asset.risk_level)}`}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <Server className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-white font-semibold">{asset.hostname}</h3>
                  <p className="text-gray-400 text-sm">{asset.ip}</p>
                </div>
              </div>
            </div>

            {/* Details */}
            <div className="space-y-2 mb-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Type:</span>
                <span className="text-white font-medium">{asset.type}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Last Seen:</span>
                <span className="text-white font-medium">{asset.last_seen}</span>
              </div>
            </div>

            {/* Risk Badge */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-700">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${getRiskColor(asset.risk_level)}`}>
                <Shield className="w-4 h-4" />
                <span className={`text-sm font-medium ${getRiskTextColor(asset.risk_level)}`}>
                  {asset.risk_level} Risk
                </span>
              </div>

              {asset.alerts > 0 && (
                <div className="flex items-center gap-1 text-red-400">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="text-sm font-medium">{asset.alerts} alerts</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Info Banner */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <p className="text-blue-300 text-sm">
          <strong>Asset Discovery:</strong> Assets are automatically discovered through passive network traffic analysis.
          No active scanning or probing is performed.
        </p>
      </div>
    </div>
  );
}
