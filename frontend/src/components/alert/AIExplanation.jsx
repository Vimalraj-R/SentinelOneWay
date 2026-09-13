import { Brain, TrendingUp } from 'lucide-react';

export default function AIExplanation({ explanation }) {
  return (
    <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-700/30 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-6 h-6 text-purple-400" />
        <h2 className="text-xl font-semibold text-white">AI Analysis & Explanation</h2>
      </div>

      {/* Model Info */}
      <div className="flex items-center gap-4 mb-4">
        <div className="flex items-center gap-2 px-3 py-1 bg-purple-500/10 rounded-full">
          <span className="text-purple-400 text-xs font-medium">Model:</span>
          <span className="text-purple-300 text-xs">{explanation.model}</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 rounded-full">
          <TrendingUp className="w-3 h-3 text-blue-400" />
          <span className="text-blue-400 text-xs font-medium">
            {(explanation.confidence * 100).toFixed(0)}% Confidence
          </span>
        </div>
      </div>

      {/* Analysis */}
      <div className="p-4 bg-gray-900/50 rounded-lg mb-4">
        <p className="text-gray-200 leading-relaxed">{explanation.analysis}</p>
      </div>

      {/* Recommendation */}
      {explanation.recommendation && (
        <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
          <div className="flex items-start gap-3">
            <TrendingUp className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-yellow-400 font-semibold mb-2">Recommendation</h3>
              <p className="text-gray-200 text-sm leading-relaxed">{explanation.recommendation}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
