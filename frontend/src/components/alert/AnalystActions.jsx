import { Eye, CheckCircle, FileText, Download, MessageSquare } from 'lucide-react';
import { useState } from 'react';
import { alertsApi } from '../../services/api';

export default function AnalystActions({ alertId, currentStatus }) {
  const [status, setStatus] = useState(currentStatus);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);

  const handleStatusChange = async (newStatus) => {
    setUpdating(true);
    setError(null);

    try {
      await alertsApi.updateAlertStatus(alertId, newStatus);
      setStatus(newStatus);
      console.log(`Status updated to: ${newStatus}`);
    } catch (err) {
      setError('Failed to update status. Please try again.');
      console.error('Status update error:', err);
    } finally {
      setUpdating(false);
    }
  };

  const handleExport = () => {
    console.log('Exporting alert...');
    // TODO: Implement export functionality
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Analyst Actions</h3>

      <div className="space-y-3">
        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Status Change Buttons - Read-only monitoring actions */}
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="text-gray-400 text-sm mb-3">Update Status</div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleStatusChange('Investigating')}
              disabled={updating}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                status === 'Investigating'
                  ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed'
              }`}
            >
              <Eye className="w-4 h-4" />
              {updating && status !== 'Investigating' ? 'Updating...' : 'Mark Investigating'}
            </button>

            <button
              onClick={() => handleStatusChange('Acknowledged')}
              disabled={updating}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                status === 'Acknowledged'
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed'
              }`}
            >
              <CheckCircle className="w-4 h-4" />
              {updating && status !== 'Acknowledged' ? 'Updating...' : 'Acknowledge'}
            </button>

            <button
              onClick={() => handleStatusChange('Resolved')}
              disabled={updating}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                status === 'Resolved'
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed'
              }`}
            >
              <CheckCircle className="w-4 h-4" />
              {updating && status !== 'Resolved' ? 'Updating...' : 'Resolve'}
            </button>
          </div>
        </div>

        {/* Export Button */}
        <button
          onClick={handleExport}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          <Download className="w-4 h-4" />
          Export Alert Report
        </button>

        {/* Note: No active mitigation actions */}
        <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <div className="flex items-start gap-2">
            <FileText className="w-4 h-4 text-blue-400 mt-0.5" />
            <p className="text-blue-300 text-xs">
              <strong>Passive Monitoring Mode:</strong> Active mitigation actions are not available.
              SentinelOneWay operates in read-only mode for critical infrastructure protection.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
