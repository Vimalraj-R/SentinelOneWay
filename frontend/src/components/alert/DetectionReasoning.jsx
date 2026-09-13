import { Lightbulb, CheckCircle } from 'lucide-react';

export default function DetectionReasoning({ reasoning }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-6 h-6 text-yellow-400" />
        <h2 className="text-xl font-semibold text-white">Why Was This Detected?</h2>
      </div>

      <p className="text-gray-300 mb-6 leading-relaxed">{reasoning.summary}</p>

      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
          Evidence Found
        </h3>
        {reasoning.reasons.map((reason, index) => (
          <div key={index} className="flex items-start gap-3 p-4 bg-gray-800/50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
            <p className="text-gray-200 leading-relaxed">{reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
