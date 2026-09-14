/**
 * Threat Alerts Page
 * Comprehensive alert management and filtering
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, Search, Filter, Eye, Clock, ArrowUpDown } from 'lucide-react';
import PassiveMonitoringBanner from '../components/common/PassiveMonitoringBanner';
import SeverityBadge from '../components/common/SeverityBadge';
import EmptyState from '../components/common/EmptyState';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { fetchApi } from '../services/api';

export default function ThreatAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [sortBy, setSortBy] = useState('timestamp'); // timestamp, risk_score, severity

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const data = await fetchApi('/api/alerts/recent?limit=100');
      setAlerts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort alerts
  const filteredAlerts = alerts
    .filter(alert => {
      const matchesSearch =
        alert.threat_class?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.src_ip?.includes(searchTerm) ||
        alert.dst_ip?.includes(searchTerm);

      const matchesSeverity = severityFilter === 'all' || alert.severity === severityFilter;

      return matchesSearch && matchesSeverity;
    })
    .sort((a, b) => {
      if (sortBy === 'timestamp') {
        return new Date(b.timestamp) - new Date(a.timestamp);
      } else if (sortBy === 'risk_score') {
        return b.risk_score - a.risk_score;
      } else if (sortBy === 'severity') {
        const severityOrder = { Critical: 0, High: 1, Medium: 2, Low: 3 };
        return severityOrder[a.severity] - severityOrder[b.severity];
      }
      return 0;
    });

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    // Less than 1 minute
    if (diff < 60000) return 'Just now';
    // Less than 1 hour
    if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`;
    // Less than 24 hours
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
    // More than 24 hours
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (loading) return <LoadingSpinner message="Loading threat alerts..." />;
  if (error) return <EmptyState type="error" title="Error Loading Alerts" description={error} />;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-red-400" />
            Threat Alerts
          </h1>
          <p className="text-gray-400 mt-1">
            Comprehensive threat alert management and investigation
          </p>
        </div>
      </div>

      {/* Passive Monitoring Banner */}
      <PassiveMonitoringBanner />

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Total Alerts</div>
          <div className="text-2xl font-bold text-white mt-1">{alerts.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-500/30">
          <div className="text-gray-400 text-sm">Critical</div>
          <div className="text-2xl font-bold text-red-400 mt-1">
            {alerts.filter(a => a.severity === 'Critical').length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-orange-500/30">
          <div className="text-gray-400 text-sm">High</div>
          <div className="text-2xl font-bold text-orange-400 mt-1">
            {alerts.filter(a => a.severity === 'High').length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-500/30">
          <div className="text-gray-400 text-sm">Medium</div>
          <div className="text-2xl font-bold text-yellow-400 mt-1">
            {alerts.filter(a => a.severity === 'Medium').length}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex flex-wrap gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by threat type, IP address..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Severity Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <ArrowUpDown className="w-5 h-5 text-gray-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="timestamp">Most Recent</option>
              <option value="risk_score">Highest Risk</option>
              <option value="severity">Severity</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alert Count */}
      <div className="text-gray-400 text-sm">
        Showing {filteredAlerts.length} of {alerts.length} alerts
      </div>

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <EmptyState
          type="alerts"
          title="No Alerts Found"
          description={searchTerm || severityFilter !== 'all'
            ? "Try adjusting your filters"
            : "No threats detected. Network traffic appears normal."}
        />
      ) : (
        <div className="space-y-3">
          {filteredAlerts.map((alert) => (
            <Link
              key={alert.id}
              to={`/alert/${alert.id}`}
              className="block bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-blue-500 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                {/* Left: Severity & Details */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <SeverityBadge severity={alert.severity} size="sm" />
                    <h3 className="text-white font-semibold">{alert.threat_class || 'Unknown Threat'}</h3>
                    <span className="text-gray-500">•</span>
                    <span className="text-gray-400 text-sm flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatTimestamp(alert.timestamp)}
                    </span>
                  </div>

                  <div className="text-gray-400 text-sm mb-2">
                    Detected {alert.threat_class} threat with {Math.round(alert.confidence * 100)}% confidence
                  </div>

                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-500">
                      Source: <span className="text-gray-300">{alert.src_ip || 'N/A'}</span>
                    </span>
                    <span className="text-gray-500">→</span>
                    <span className="text-gray-500">
                      Dest: <span className="text-gray-300">{alert.dst_ip || 'N/A'}</span>
                    </span>
                  </div>
                </div>

                {/* Right: Risk Score & Action */}
                <div className="flex flex-col items-end gap-2">
                  <div className="text-right">
                    <div className="text-gray-400 text-xs">Risk Score</div>
                    <div className={`text-2xl font-bold ${
                      alert.risk_score >= 85 ? 'text-red-400' :
                      alert.risk_score >= 70 ? 'text-orange-400' :
                      alert.risk_score >= 50 ? 'text-yellow-400' :
                      'text-blue-400'
                    }`}>
                      {alert.risk_score || 0}
                    </div>
                  </div>

                  <button className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors">
                    <Eye className="w-4 h-4" />
                    View Details
                  </button>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
