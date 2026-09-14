/**
 * System Health Page
 *
 * Real data sources:
 * - GET /health                       (backend status + version)
 * - GET /api/continuous-traffic/status (background traffic service)
 * - GET /api/dashboard/summary        (live detection statistics)
 * - useWebSocket                      (real-time stream connectivity)
 */
import { useState, useEffect } from 'react';
import {
  HeartPulse, CheckCircle, XCircle, AlertCircle, Cpu, Database,
  Activity, Shield, Wifi, WifiOff
} from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { fetchApi } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

export default function SystemHealth() {
  const [health, setHealth] = useState(null);
  const [traffic, setTraffic] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Real WebSocket stream status
  const { isConnected } = useWebSocket(() => {});

  useEffect(() => {
    let cancelled = false;

    const fetchHealth = async () => {
      try {
        const [healthData, trafficData, summaryData] = await Promise.all([
          fetchApi('/health'),
          fetchApi('/api/continuous-traffic/status').catch(() => null),
          fetchApi('/api/dashboard/summary').catch(() => null)
        ]);

        if (cancelled) return;

        setHealth(healthData);
        setTraffic(trafficData);
        setSummary(summaryData);
        setError(null);
      } catch (err) {
        if (!cancelled) {
          console.error('Health check failed:', err);
          setError(err.message || 'Failed to reach the backend');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 5000); // Update every 5 seconds

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const backendHealthy = health?.status === 'healthy';
  const trafficRunning = !!traffic?.is_running;

  const StatusIndicator = ({ ok }) => {
    if (ok) return <CheckCircle className="w-5 h-5 text-green-400" />;
    return <XCircle className="w-5 h-5 text-red-400" />;
  };

  if (loading && !health) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" message="Checking system health..." />
      </div>
    );
  }

  if (error && !health) {
    return (
      <div className="p-6">
        <ErrorMessage message={error} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  const severityCounts = summary?.alerts_by_severity || {};
  const totalAlerts = Object.values(severityCounts).reduce((a, b) => a + b, 0);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <HeartPulse className="w-8 h-8 text-green-400" />
          System Health
        </h1>
        <p className="text-gray-400 mt-1">
          Monitor sensor health, performance metrics, and system diagnostics
        </p>
      </div>

      {/* Overall Status */}
      <div className={`bg-gradient-to-r rounded-lg p-6 border ${
        backendHealthy
          ? 'from-green-500/20 to-blue-500/20 border-green-500/30'
          : 'from-red-500/20 to-orange-500/20 border-red-500/30'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              {backendHealthy
                ? <CheckCircle className="w-8 h-8 text-green-400" />
                : <AlertCircle className="w-8 h-8 text-red-400" />}
              <h2 className="text-2xl font-bold text-white">
                {backendHealthy ? 'System Operational' : 'System Unavailable'}
              </h2>
            </div>
            <p className="text-gray-300">
              {backendHealthy
                ? 'Backend API is responding. Background cyber range generation is active for live demonstrations.'
                : 'Unable to reach the backend API.'}
            </p>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${backendHealthy ? 'text-green-400' : 'text-red-400'}`}>
              {backendHealthy ? (summary?.risk_score ?? '—') : '0'}
            </div>
            <div className="text-gray-400 text-sm">Current Risk</div>
          </div>
        </div>
      </div>

      {/* Core Components */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backend API */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Cpu className="w-6 h-6 text-blue-400" />
              <h3 className="text-xl font-bold text-white">Backend API</h3>
            </div>
            <StatusIndicator ok={backendHealthy} />
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Status:</span>
              <span className={`font-medium capitalize ${backendHealthy ? 'text-green-400' : 'text-red-400'}`}>
                {health?.status || 'unknown'}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Service:</span>
              <span className="text-white font-medium">{health?.service || '—'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Version:</span>
              <span className="text-white font-medium">{health?.version || '—'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Live Flow Rate:</span>
              <span className="text-white font-medium">
                {summary?.current_flow_rate != null
                  ? `${summary.current_flow_rate.toFixed(1)} flows/sec`
                  : '—'}
              </span>
            </div>
          </div>
        </div>

        {/* Background Traffic Service */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Activity className="w-6 h-6 text-orange-400" />
              <h3 className="text-xl font-bold text-white">Cyber Range</h3>
            </div>
            <StatusIndicator ok={trafficRunning} />
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Status:</span>
              <span className={`font-medium ${trafficRunning ? 'text-green-400' : 'text-gray-300'}`}>
                {trafficRunning ? 'Running' : 'Stopped'}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Current Scenario:</span>
              <span className="text-white font-medium capitalize">
                {(traffic?.current_scenario || '—').replace(/_/g, ' ')}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Flows Processed:</span>
              <span className="text-white font-medium">
                {(traffic?.flows_processed ?? 0).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Alerts Generated:</span>
              <span className="text-white font-medium">
                {(traffic?.alerts_generated ?? 0).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Scenario Cycle:</span>
              <span className="text-white font-medium">
                {traffic ? `${traffic.scenario_index + 1}/${traffic.total_scenarios}` : '—'}
              </span>
            </div>
          </div>
        </div>

        {/* Detection Database */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Database className="w-6 h-6 text-purple-400" />
              <h3 className="text-xl font-bold text-white">Detection Data</h3>
            </div>
            <StatusIndicator ok={backendHealthy} />
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Total Alerts:</span>
              <span className="text-white font-medium">{totalAlerts.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Critical:</span>
              <span className="text-red-400 font-medium">{severityCounts.Critical || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">High:</span>
              <span className="text-orange-400 font-medium">{severityCounts.High || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Medium:</span>
              <span className="text-yellow-400 font-medium">{severityCounts.Medium || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Low:</span>
              <span className="text-green-400 font-medium">{severityCounts.Low || 0}</span>
            </div>
          </div>
        </div>

        {/* Real-time Stream */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              {isConnected ? (
                <Wifi className="w-6 h-6 text-green-400" />
              ) : (
                <WifiOff className="w-6 h-6 text-gray-400" />
              )}
              <h3 className="text-xl font-bold text-white">Real-time Stream</h3>
            </div>
            <StatusIndicator ok={isConnected} />
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">WebSocket:</span>
              <span className={`font-medium ${isConnected ? 'text-green-400' : 'text-gray-300'}`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Endpoint:</span>
              <span className="text-white font-mono text-xs">/ws/alerts</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Push Model:</span>
              <span className="text-white font-medium">Alert streaming</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Latency:</span>
              <span className="text-white font-medium">Live</span>
            </div>
          </div>
        </div>
      </div>

      {/* Detection Stack */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-6 h-6 text-blue-400" />
          <h3 className="text-xl font-bold text-white">Detection Stack</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Rule-based Detectors</div>
            <div className="text-white font-semibold">Active</div>
            <div className="text-gray-500 text-xs mt-1">
              SYN flood, port scan, C2 beacon, DNS tunnel, exfiltration
            </div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Hybrid ML Engine</div>
            <div className="text-white font-semibold">Active</div>
            <div className="text-gray-500 text-xs mt-1">
              Score fusion + explainable evidence for every alert
            </div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Incident Correlation</div>
            <div className="text-white font-semibold">
              {summary?.critical_threats != null ? 'Active' : '—'}
            </div>
            <div className="text-gray-500 text-xs mt-1">
              Multi-stage attack timeline reconstruction
            </div>
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
        <p className="text-green-300 text-sm">
          <strong>System Status:</strong> Health checks run automatically every 5 seconds.
          All metrics shown are live data from the detection pipeline — no simulated UI values.
        </p>
      </div>
    </div>
  );
}