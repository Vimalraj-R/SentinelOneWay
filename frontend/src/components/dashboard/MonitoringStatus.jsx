import { Activity, CheckCircle, XCircle } from 'lucide-react';

export default function MonitoringStatus({ status }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Activity className="w-5 h-5 text-green-400" />
        <h3 className="text-white font-semibold">Live Monitoring Status</h3>
      </div>

      <div className="space-y-4">
        {/* Mode and Status */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-gray-400 text-sm">Mode</span>
            <p className="text-white font-medium mt-1">{status.mode}</p>
          </div>
          <div>
            <span className="text-gray-400 text-sm">Status</span>
            <p className="text-green-400 font-medium mt-1">{status.status}</p>
          </div>
        </div>

        {/* Uptime */}
        <div>
          <span className="text-gray-400 text-sm">Uptime</span>
          <p className="text-white font-medium mt-1">{status.uptime}</p>
        </div>

        {/* Sensors */}
        <div className="pt-4 border-t border-gray-800">
          <div className="flex items-center justify-between mb-3">
            <span className="text-gray-400 text-sm">Network Sensors</span>
            <span className="text-green-400 text-sm font-medium">
              {status.sensors.active}/{status.sensors.total} Active
            </span>
          </div>

          <div className="space-y-2">
            {status.networkInterfaces.map((iface, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
              >
                <div className="flex items-center gap-2">
                  {iface.status === 'active' ? (
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-400" />
                  )}
                  <span className="text-white text-sm font-medium">{iface.name}</span>
                </div>
                <div className="text-right">
                  <span className="text-gray-400 text-xs">{iface.packets}</span>
                  {iface.drops > 0 && (
                    <span className="text-red-400 text-xs ml-2">
                      {iface.drops} drops
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
