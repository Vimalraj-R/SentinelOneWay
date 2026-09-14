/**
 * Attack Timeline page showing correlated multi-stage attacks
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { Shield, Clock, AlertTriangle, ChevronRight, Activity } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { fetchApi } from '../services/api';

export default function AttackTimeline() {
  const navigate = useNavigate();
  const [selectedIncident, setSelectedIncident] = useState(null);

  // Fetch incidents
  const { data: incidentsData, loading, error, refetch } = useApi(
    () => fetchApi('/api/incidents/?limit=50')
  );

  // Fetch incident detail when selected
  const { data: incidentDetail, loading: detailLoading } = useApi(
    selectedIncident
        ? () => fetchApi(`/api/incidents/${selectedIncident}`)
      : null,
    [selectedIncident]
  );

  if (loading && !incidentsData) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" message="Loading attack timeline..." />
      </div>
    );
  }

  if (error && !incidentsData) {
    return (
      <div className="p-6">
        <ErrorMessage message={error} onRetry={refetch} />
      </div>
    );
  }

  const incidents = incidentsData?.incidents || [];

  // Severity colors
  const getSeverityColor = (severity) => {
    const colors = {
      'Critical': 'border-red-500 bg-red-500/10',
      'High': 'border-orange-500 bg-orange-500/10',
      'Medium': 'border-yellow-500 bg-yellow-500/10',
      'Low': 'border-green-500 bg-green-500/10'
    };
    return colors[severity] || 'border-gray-500 bg-gray-500/10';
  };

  const getSeverityTextColor = (severity) => {
    const colors = {
      'Critical': 'text-red-400',
      'High': 'text-orange-400',
      'Medium': 'text-yellow-400',
      'Low': 'text-green-400'
    };
    return colors[severity] || 'text-gray-400';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Attack Timeline</h1>
        <p className="text-gray-400">
          Correlated multi-stage attacks showing the complete attack story
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <Activity className="w-8 h-8 text-blue-400" />
            <div>
              <div className="text-2xl font-bold text-white">
                {incidents.filter(i => i.status === 'Active').length}
              </div>
              <div className="text-sm text-gray-400">Active Incidents</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-red-400" />
            <div>
              <div className="text-2xl font-bold text-white">
                {incidents.filter(i => i.severity === 'Critical').length}
              </div>
              <div className="text-sm text-gray-400">Critical Incidents</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-green-400" />
            <div>
              <div className="text-2xl font-bold text-white">
                {incidents.filter(i => i.status === 'Resolved').length}
              </div>
              <div className="text-sm text-gray-400">Resolved</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <Clock className="w-8 h-8 text-yellow-400" />
            <div>
              <div className="text-2xl font-bold text-white">{incidents.length}</div>
              <div className="text-sm text-gray-400">Total Incidents</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Incident List */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xl font-semibold text-white">Recent Incidents</h2>

          {incidents.length === 0 ? (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
              <p className="text-gray-400">No incidents detected</p>
              <p className="text-sm text-gray-500 mt-2">
                Incidents are automatically created by correlating related alerts
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {incidents.map((incident) => (
                <button
                  key={incident.incident_id}
                  onClick={() => setSelectedIncident(incident.incident_id)}
                  className={`w-full text-left bg-gray-900 border-2 rounded-xl p-4 transition-all hover:border-blue-500 ${
                    selectedIncident === incident.incident_id
                      ? 'border-blue-500'
                      : getSeverityColor(incident.severity)
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-semibold text-white mb-1">
                        {incident.attack_pattern}
                      </div>
                      <div className="text-xs text-gray-500">
                        {incident.incident_id}
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-500 flex-shrink-0" />
                  </div>

                  <div className="flex items-center gap-4 text-sm">
                    <span className={`font-medium ${getSeverityTextColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                    <span className="text-gray-400">
                      {incident.alert_count} alerts
                    </span>
                    <span className="text-gray-400">
                      Risk: {incident.risk_score}/100
                    </span>
                  </div>

                  <div className="mt-2 text-xs text-gray-500">
                    {new Date(incident.start_time).toLocaleString()}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Incident Detail */}
        <div className="lg:col-span-2">
          {!selectedIncident ? (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
              <Shield className="w-16 h-16 text-gray-700 mx-auto mb-4" />
              <p className="text-gray-400">Select an incident to view details</p>
            </div>
          ) : detailLoading ? (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-12">
              <LoadingSpinner message="Loading incident details..." />
            </div>
          ) : incidentDetail ? (
            <div className="space-y-6">
              {/* Incident Header */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      {incidentDetail.attack_pattern}
                    </h2>
                    <p className="text-gray-400">{incidentDetail.incident_id}</p>
                  </div>
                  <div className="text-right">
                    <div className={`text-3xl font-bold ${getSeverityTextColor(incidentDetail.severity)}`}>
                      {incidentDetail.risk_score}/100
                    </div>
                    <div className="text-sm text-gray-400">Risk Score</div>
                  </div>
                </div>

                <div className="border-t border-gray-800 pt-4">
                  <p className="text-gray-300 leading-relaxed">{incidentDetail.summary}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-800">
                  <div>
                    <div className="text-sm text-gray-400">Started</div>
                    <div className="text-white">
                      {new Date(incidentDetail.start_time).toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Duration</div>
                    <div className="text-white">
                      {Math.round(incidentDetail.duration_minutes)} minutes
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Affected Assets</div>
                    <div className="text-white">{incidentDetail.affected_assets.length}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Related Alerts</div>
                    <div className="text-white">{incidentDetail.alert_count}</div>
                  </div>
                </div>
              </div>

              {/* Attack Timeline */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-6">Attack Stages</h3>

                <div className="space-y-4">
                  {incidentDetail.timeline.map((stage, index) => (
                    <div key={index} className="relative pl-8">
                      {/* Timeline line */}
                      {index < incidentDetail.timeline.length - 1 && (
                        <div className="absolute left-3 top-8 bottom-0 w-0.5 bg-gray-700" />
                      )}

                      {/* Timeline dot */}
                      <div className="absolute left-0 top-2 w-6 h-6 rounded-full bg-blue-500 border-4 border-gray-900 flex items-center justify-center">
                        <div className="w-2 h-2 rounded-full bg-white" />
                      </div>

                      {/* Stage content */}
                      <div className="bg-gray-800/50 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="font-semibold text-white mb-1">
                              {stage.stage}
                            </div>
                            <div className="text-sm text-gray-400 mb-2">
                              {new Date(stage.timestamp).toLocaleTimeString('en-US', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })} - {stage.description}
                            </div>
                            <div className="flex items-center gap-3 text-xs">
                              <span className="text-gray-500">
                                {stage.src_ip} → {stage.dst_ip}
                              </span>
                              <span className="text-gray-500">
                                Risk: {stage.risk_score}/100
                              </span>
                            </div>
                          </div>
                          <button
                            onClick={() => navigate(`/alerts/${stage.alert_id}`)}
                            className="text-sm text-blue-400 hover:text-blue-300"
                          >
                            View Alert →
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Affected Assets */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-4">Affected Assets</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {incidentDetail.affected_assets.map((asset, index) => (
                    <div
                      key={index}
                      className="bg-gray-800/50 rounded-lg p-3 text-center"
                    >
                      <div className="text-white font-mono text-sm">{asset}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
