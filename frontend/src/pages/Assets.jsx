/**
 * Assets Page - Network asset inventory
 *
 * Loads real assets from GET /api/assets and displays risk profiling.
 */
import { useState } from 'react';
import { Server, Shield, AlertTriangle, Search } from 'lucide-react';
import { assetsApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';

const RISK_LEVELS = ['Critical', 'High', 'Medium', 'Low'];

export default function Assets() {
  const [searchTerm, setSearchTerm] = useState('');

  const { data, loading, error, refetch } = useApi(() =>
    assetsApi.getAssets({ limit: 250 })
  );

  const assets = data?.assets || [];

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

  const getTypeLabel = (type) => {
    const map = {
      server: 'Server',
      workstation: 'Workstation',
      network_device: 'Network Device',
      database: 'Database',
      application: 'Application',
      storage: 'Storage',
      infrastructure: 'Infrastructure'
    };
    return map[type] || type || 'Unknown';
  };

  const filteredAssets = assets.filter(asset => {
    const query = searchTerm.toLowerCase().trim();
    if (!query) return true;
    return (
      (asset.hostname || '').toLowerCase().includes(query) ||
      (asset.ip_address || '').toLowerCase().includes(query) ||
      (asset.criticality || '').toLowerCase().includes(query)
    );
  });

  const countByRisk = (level) =>
    assets.filter(a => (a.criticality || '').toLowerCase() === level.toLowerCase()).length;

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" message="Loading network assets..." />
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="p-6">
        <ErrorMessage message={error} onRetry={refetch} />
      </div>
    );
  }

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
            {countByRisk('Critical')}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-orange-500/30">
          <div className="text-gray-400 text-sm">High Risk</div>
          <div className="text-2xl font-bold text-orange-400 mt-1">
            {countByRisk('High')}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-blue-500/30">
          <div className="text-gray-400 text-sm">Active Monitoring</div>
          <div className="text-2xl font-bold text-blue-400 mt-1">{assets.length}</div>
        </div>
      </div>

      {/* Search */}
      {assets.length > 0 && (
        <div className="max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by hostname, IP, or risk level..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      )}

      {/* Assets Grid */}
      {filteredAssets.length === 0 ? (
        <EmptyState
          type="assets"
          title={searchTerm ? 'No Matching Assets' : 'No Assets Found'}
          description={searchTerm
            ? 'No assets match your search. Try a different filter.'
            : 'Assets are automatically discovered through passive network traffic analysis.'}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAssets.map((asset) => (
            <div
              key={asset.id}
              className={`bg-gray-800 rounded-lg p-5 border transition-colors ${getRiskColor(asset.criticality)}`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                    <Server className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">{asset.hostname || 'Unknown'}</h3>
                    <p className="text-gray-400 text-sm">{asset.ip_address}</p>
                  </div>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-2 mb-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Type:</span>
                  <span className="text-white font-medium">{getTypeLabel(asset.asset_type)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Risk Score:</span>
                  <span className={`font-medium ${getRiskTextColor(asset.criticality)}`}>
                    {asset.risk_score}/100
                  </span>
                </div>
              </div>

              {/* Risk Badge */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-700">
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${getRiskColor(asset.criticality)}`}>
                  <Shield className="w-4 h-4" />
                  <span className={`text-sm font-medium ${getRiskTextColor(asset.criticality)}`}>
                    {asset.criticality} Risk
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Banner */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <p className="text-blue-300 text-sm">
          <strong>Asset Discovery:</strong> Assets are automatically discovered through passive network traffic analysis.
          No active scanning or probing is performed. Criticality and risk scores are computed by the detection engine.
        </p>
      </div>
    </div>
  );
}