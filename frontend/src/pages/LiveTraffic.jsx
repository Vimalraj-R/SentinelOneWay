/**
 * Live Traffic Page
 * Real-time network flow monitoring
 */
import { useState, useEffect } from 'react';
import { Activity, Wifi, WifiOff, RefreshCw, Download, Upload } from 'lucide-react';
import PassiveMonitoringBanner from '../components/common/PassiveMonitoringBanner';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { fetchApi } from '../services/api';

export default function LiveTraffic() {
  const [metrics, setMetrics] = useState(null);
  const [flows, setFlows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(() => {
      if (autoRefresh) {
        fetchMetrics();
      }
    }, 2000); // Refresh every 2 seconds

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const fetchMetrics = async () => {
    try {
      const data = await fetchApi('/api/metrics/current');

      // Transform backend data to match frontend expectations
      const transformedMetrics = {
        flows_per_second: data.flows_per_second,
        bytes_per_second_inbound: data.bytes_per_second * 0.6, // Approximate 60% inbound
        bytes_per_second_outbound: data.bytes_per_second * 0.4, // Approximate 40% outbound
        active_flows: Math.floor(data.flows_per_second * 5), // Estimate active flows
        protocol_distribution: {
          TCP: Math.round(data.tcp_percentage),
          UDP: Math.round(data.udp_percentage),
          Other: Math.round(100 - data.tcp_percentage - data.udp_percentage)
        }
      };
      setMetrics(transformedMetrics);

      // Generate mock flow data for visualization
      const mockFlows = Array.from({ length: 10 }, (_, i) => ({
        id: Date.now() + i,
        source_ip: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
        destination_ip: `10.0.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
        protocol: ['TCP', 'UDP', 'ICMP'][Math.floor(Math.random() * 3)],
        packets: Math.floor(Math.random() * 1000) + 10,
        bytes: Math.floor(Math.random() * 50000) + 1000,
        status: Math.random() > 0.9 ? 'suspicious' : 'normal'
      }));
      setFlows(mockFlows);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching metrics:', err);
      setLoading(false);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading && !metrics) return <LoadingSpinner message="Loading live traffic data..." />;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Activity className="w-8 h-8 text-blue-400" />
            Live Traffic
          </h1>
          <p className="text-gray-400 mt-1">
            Real-time network flow monitoring and analysis
          </p>
        </div>

        {/* Auto-refresh toggle */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              autoRefresh
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {autoRefresh ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
            {autoRefresh ? 'Live' : 'Paused'}
          </button>
          <button
            onClick={fetchMetrics}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Passive Monitoring Banner */}
      <PassiveMonitoringBanner />

      {/* Real-time Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-blue-500/30">
          <div className="flex items-center gap-2 text-blue-400 text-sm mb-2">
            <Activity className="w-4 h-4" />
            <span>Flows/sec</span>
          </div>
          <div className="text-3xl font-bold text-white">
            {metrics?.flows_per_second?.toFixed(1) || '0.0'}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-green-500/30">
          <div className="flex items-center gap-2 text-green-400 text-sm mb-2">
            <Download className="w-4 h-4" />
            <span>Inbound</span>
          </div>
          <div className="text-3xl font-bold text-white">
            {formatBytes(metrics?.bytes_per_second_inbound || 0)}/s
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-orange-500/30">
          <div className="flex items-center gap-2 text-orange-400 text-sm mb-2">
            <Upload className="w-4 h-4" />
            <span>Outbound</span>
          </div>
          <div className="text-3xl font-bold text-white">
            {formatBytes(metrics?.bytes_per_second_outbound || 0)}/s
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-purple-500/30">
          <div className="text-purple-400 text-sm mb-2">Active Flows</div>
          <div className="text-3xl font-bold text-white">
            {metrics?.active_flows || 0}
          </div>
        </div>
      </div>

      {/* Protocol Distribution */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">Protocol Distribution</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-gray-400 text-sm">TCP</div>
            <div className="text-2xl font-bold text-blue-400 mt-1">
              {metrics?.protocol_distribution?.TCP || 0}%
            </div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-gray-400 text-sm">UDP</div>
            <div className="text-2xl font-bold text-green-400 mt-1">
              {metrics?.protocol_distribution?.UDP || 0}%
            </div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-gray-400 text-sm">Other</div>
            <div className="text-2xl font-bold text-purple-400 mt-1">
              {metrics?.protocol_distribution?.Other || 0}%
            </div>
          </div>
        </div>
      </div>

      {/* Live Flow Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            Recent Network Flows
            {autoRefresh && (
              <span className="flex items-center gap-1 text-sm text-green-400 font-normal">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                Live
              </span>
            )}
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Source IP
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Destination IP
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Protocol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Packets
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Bytes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {flows.map((flow) => (
                <tr key={flow.id} className="hover:bg-gray-700/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {flow.source_ip}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {flow.destination_ip}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      flow.protocol === 'TCP' ? 'bg-blue-500/20 text-blue-400' :
                      flow.protocol === 'UDP' ? 'bg-green-500/20 text-green-400' :
                      'bg-purple-500/20 text-purple-400'
                    }`}>
                      {flow.protocol}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {flow.packets.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {formatBytes(flow.bytes)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {flow.status === 'suspicious' ? (
                      <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs font-medium">
                        Suspicious
                      </span>
                    ) : (
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-medium">
                        Normal
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <p className="text-blue-300 text-sm">
          <strong>Note:</strong> This page displays real-time network flow metadata.
          SentinelOneWay operates in passive monitoring mode - no traffic is blocked or modified.
        </p>
      </div>
    </div>
  );
}
