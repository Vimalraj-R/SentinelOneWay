import { useState, useCallback, useEffect } from 'react';
import { Shield, AlertTriangle, Activity, Zap, Wifi, WifiOff } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { useWebSocket } from '../hooks/useWebSocket';
import { dashboardApi, metricsApi } from '../services/api';
import KPICard from '../components/dashboard/KPICard';
import RiskGauge from '../components/dashboard/RiskGauge';
import TrafficChart from '../components/dashboard/TrafficChart';
import ThreatDistribution from '../components/dashboard/ThreatDistribution';
import SeverityDistribution from '../components/dashboard/SeverityDistribution';
import AlertsTable from '../components/dashboard/AlertsTable';
import TopAssets from '../components/dashboard/TopAssets';
import AIInsightPanel from '../components/dashboard/AIInsightPanel';
import MonitoringStatus from '../components/dashboard/MonitoringStatus';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { aiInsights, monitoringStatus } from '../data/mockData';

export default function Overview() {
  const [notifications, setNotifications] = useState([]);
  const [realtimeData, setRealtimeData] = useState(null);

  // Fetch dashboard summary
  const { data: dashboardData, loading: dashboardLoading, error: dashboardError, refetch: refetchDashboard } = useApi(
    () => dashboardApi.getSummary()
  );

  // Fetch metrics history for traffic chart
  const { data: metricsHistory, loading: metricsLoading, refetch: refetchMetrics } = useApi(
    () => metricsApi.getHistory({ hours: 24, limit: 24 })
  );

  // Keep the dashboard aligned with the backend's continuous traffic service.
  useEffect(() => {
    const refreshDashboard = setInterval(() => {
      refetchDashboard();
      refetchMetrics();
    }, 5000);

    return () => clearInterval(refreshDashboard);
    // The API hook functions are intentionally used by this stable polling loop.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handle incoming WebSocket alerts
  const handleWebSocketMessage = useCallback((alert) => {
    console.log('New alert received via WebSocket:', alert);

    // Update realtime data
    setRealtimeData(prev => ({
      lastAlert: alert,
      alertCount: (prev?.alertCount || 0) + 1
    }));

    // Show notification
    showNotification(alert);

    // Refresh dashboard data to get updated statistics
    refetchDashboard();
  }, [refetchDashboard]);

  // WebSocket connection
  const { isConnected, connectionStatus } = useWebSocket(handleWebSocketMessage);

  // Show notification for new alert
  const showNotification = (alert) => {
    const notification = {
      id: Date.now(),
      alert,
      timestamp: new Date()
    };

    setNotifications(prev => [notification, ...prev].slice(0, 3)); // Keep only last 3

    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  // Dismiss notification
  const dismissNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Show loading state while initial data loads
  if (dashboardLoading && !dashboardData) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" message="Loading dashboard data..." />
      </div>
    );
  }

  // Show error state if dashboard fetch failed
  if (dashboardError && !dashboardData) {
    return (
      <div className="p-6">
        <ErrorMessage message={dashboardError} onRetry={refetchDashboard} />
      </div>
    );
  }

  // Transform API data to match component expectations
  const kpiData = dashboardData ? {
    riskScore: {
      value: dashboardData.risk_score,
      trend: '+5',
      status: dashboardData.risk_score >= 70 ? 'danger' : dashboardData.risk_score >= 50 ? 'warning' : 'success',
      label: 'Network Risk Score'
    },
    activeAlerts: {
      value: dashboardData.active_alerts,
      trend: '+8',
      status: dashboardData.active_alerts > 20 ? 'danger' : dashboardData.active_alerts > 10 ? 'warning' : 'success',
      label: 'Active Alerts'
    },
    criticalThreats: {
      value: dashboardData.critical_threats,
      trend: dashboardData.critical_threats > 0 ? '+2' : '0',
      status: dashboardData.critical_threats > 0 ? 'danger' : 'success',
      label: 'Critical Threats'
    },
    flowRate: {
      value: `${(dashboardData.current_flow_rate / 1000).toFixed(1)}k`,
      trend: '+12%',
      status: 'success',
      label: 'Current Flow Rate',
      unit: 'flows/sec'
    }
  } : null;

  // Transform traffic data for chart
  const trafficData = metricsHistory?.metrics ? metricsHistory.metrics
    .slice()
    .reverse()
    .map(metric => {
      const date = new Date(metric.timestamp);
      return {
        time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
        flows: Math.round(metric.flows_per_second),
        threats: Math.round(Math.random() * 5) // TODO: Add threats count to metrics model
      };
    }) : [];

  // Transform severity distribution
  const severityDistribution = dashboardData?.alerts_by_severity ? [
    { severity: 'Critical', count: dashboardData.alerts_by_severity.Critical || 0, color: '#dc2626' },
    { severity: 'High', count: dashboardData.alerts_by_severity.High || 0, color: '#ea580c' },
    { severity: 'Medium', count: dashboardData.alerts_by_severity.Medium || 0, color: '#ca8a04' },
    { severity: 'Low', count: dashboardData.alerts_by_severity.Low || 0, color: '#16a34a' }
  ] : [];

  // Transform threat distribution (simplified from severity for now)
  const threatDistribution = dashboardData?.alerts_by_severity ? [
    { name: 'DDoS/Flood', value: Math.round((dashboardData.alerts_by_severity.Critical || 0) * 0.5), color: '#ef4444' },
    { name: 'Port Scan', value: Math.round((dashboardData.alerts_by_severity.High || 0) * 0.5), color: '#f97316' },
    { name: 'C2 Beacon', value: Math.round((dashboardData.alerts_by_severity.Critical || 0) * 0.3), color: '#eab308' },
    { name: 'DNS Tunnel', value: Math.round((dashboardData.alerts_by_severity.Medium || 0) * 0.5), color: '#3b82f6' },
    { name: 'Data Exfil', value: Math.round((dashboardData.alerts_by_severity.Critical || 0) * 0.2), color: '#8b5cf6' }
  ].filter(item => item.value > 0) : [];

  return (
    <div className="p-6 space-y-6">
      {/* Notifications */}
      {notifications.length > 0 && (
        <div className="fixed top-4 right-4 z-50 space-y-2">
          {notifications.map(notification => (
            <div
              key={notification.id}
              className="bg-gray-900 border-l-4 border-red-500 p-4 rounded-lg shadow-lg animate-slide-in-right max-w-md"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <span className="font-semibold text-white">
                      {notification.alert.threat_class.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-1">
                    {notification.alert.src_ip} → {notification.alert.dst_ip}:{notification.alert.dst_port}
                  </p>
                  <p className="text-xs text-gray-500">
                    Risk: {notification.alert.risk_score}/100 | Severity: {notification.alert.severity}
                  </p>
                </div>
                <button
                  onClick={() => dismissNotification(notification.id)}
                  className="text-gray-500 hover:text-gray-300 ml-2"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Page Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Network Overview</h1>
          <p className="text-gray-400">Real-time passive network threat intelligence and monitoring</p>
        </div>

        {/* Connection Status */}
        <div className="flex items-center gap-2">
          {isConnected ? (
            <>
              <Wifi className="w-5 h-5 text-green-500" />
              <span className="text-sm text-green-500 font-medium">Live</span>
            </>
          ) : connectionStatus === 'connecting' ? (
            <>
              <div className="w-5 h-5 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-yellow-500 font-medium">Connecting...</span>
            </>
          ) : (
            <>
              <WifiOff className="w-5 h-5 text-gray-500" />
              <span className="text-sm text-gray-500 font-medium">Disconnected</span>
            </>
          )}
        </div>
      </div>

      {/* KPI Cards */}
      {kpiData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard data={kpiData.riskScore} icon={Shield} />
          <KPICard data={kpiData.activeAlerts} icon={AlertTriangle} />
          <KPICard data={kpiData.criticalThreats} icon={Zap} />
          <KPICard data={kpiData.flowRate} icon={Activity} />
        </div>
      )}

      {/* Main Dashboard Grid */}
      {kpiData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
          {/* Risk Gauge */}
          <div className="lg:col-span-1 flex w-full">
            <RiskGauge score={kpiData.riskScore.value} />
          </div>

          {/* Traffic Chart */}
          <div className="lg:col-span-2 flex w-full">
            {metricsLoading && !metricsHistory ? (
              <div className="bg-gray-900 border border-gray-800 rounded-xl w-full h-full p-6 flex items-center justify-center">
                <LoadingSpinner message="Loading traffic data..." />
              </div>
            ) : (
              <TrafficChart data={trafficData} />
            )}
          </div>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ThreatDistribution data={threatDistribution} />
        <SeverityDistribution data={severityDistribution} />
      </div>

      {/* Alerts Table */}
      {dashboardData?.recent_alerts && (
        <AlertsTable alerts={dashboardData.recent_alerts} />
      )}

      {/* Bottom Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {dashboardData?.top_threatened_assets && (
          <TopAssets assets={dashboardData.top_threatened_assets} />
        )}
        <AIInsightPanel insights={aiInsights} />
        <MonitoringStatus status={monitoringStatus} />
      </div>
    </div>
  );
}
