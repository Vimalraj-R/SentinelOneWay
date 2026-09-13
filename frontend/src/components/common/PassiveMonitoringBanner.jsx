/**
 * Passive Monitoring Banner
 * Clearly indicates read-only/passive monitoring mode
 */
import { Eye, Shield } from 'lucide-react';

export default function PassiveMonitoringBanner() {
  return (
    <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg px-4 py-2">
      <div className="flex items-center gap-2 text-sm">
        <Eye className="w-4 h-4 text-blue-400 flex-shrink-0" />
        <span className="text-blue-300 font-medium">Passive Monitoring</span>
        <span className="text-gray-400">•</span>
        <span className="text-gray-400">
          Read-only network observation. No active blocking or response.
        </span>
      </div>
    </div>
  );
}
