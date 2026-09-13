import { Terminal } from 'lucide-react';

export default function TechnicalEvidence({ evidence }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Terminal className="w-5 h-5 text-purple-400" />
        <h2 className="text-xl font-semibold text-white">Technical Evidence</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(evidence).map(([key, value]) => (
          <div key={key} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50">
            <div className="text-gray-400 text-xs mb-1">{key}</div>
            <div className="text-white font-mono text-sm font-semibold">{value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
