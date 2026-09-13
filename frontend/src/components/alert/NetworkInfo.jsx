import { Network, ArrowRight } from 'lucide-react';

export default function NetworkInfo({ network }) {
  const InfoRow = ({ label, value }) => (
    <div className="flex items-center justify-between py-3 border-b border-gray-800 last:border-0">
      <span className="text-gray-400 text-sm">{label}</span>
      <span className="text-white font-mono text-sm">{value}</span>
    </div>
  );

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Network className="w-5 h-5 text-blue-400" />
        <h2 className="text-xl font-semibold text-white">Network Information</h2>
      </div>

      {/* Source and Destination Visual */}
      <div className="flex items-center justify-between mb-6 p-4 bg-gray-800/50 rounded-lg">
        <div className="text-center flex-1">
          <p className="text-gray-400 text-xs mb-2">SOURCE</p>
          <p className="text-white font-mono font-semibold">{network.sourceIp}</p>
          <p className="text-gray-500 text-xs mt-1">{network.sourcePort}</p>
        </div>
        <ArrowRight className="w-8 h-8 text-red-400" />
        <div className="text-center flex-1">
          <p className="text-gray-400 text-xs mb-2">DESTINATION</p>
          <p className="text-white font-mono font-semibold">{network.destinationIp}</p>
          <p className="text-gray-500 text-xs mt-1">{network.destinationPort}</p>
        </div>
      </div>

      {/* Detailed Info */}
      <div className="space-y-0">
        <InfoRow label="Protocol" value={network.protocol} />
        <InfoRow label="Flow Duration" value={network.duration} />
        <InfoRow label="Total Packets" value={network.totalPackets} />
        <InfoRow label="Total Bytes" value={network.totalBytes} />
        <InfoRow label="Flow ID" value={network.flowId} />
      </div>
    </div>
  );
}
