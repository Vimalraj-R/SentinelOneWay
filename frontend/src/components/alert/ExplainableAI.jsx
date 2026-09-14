/**
 * Explainable AI component for Alert Details
 *
 * Shows why SentinelOneWay detected this threat with:
 * - Human-readable explanations
 * - Expandable technical evidence
 */
import { useState } from 'react';
import { ChevronDown, ChevronUp, Brain, BarChart3, AlertCircle } from 'lucide-react';
import { useApi } from '../../hooks/useApi';
import LoadingSpinner from '../common/LoadingSpinner';
import { fetchApi } from '../../services/api';

export default function ExplainableAI({ alertId }) {
  const [showTechnical, setShowTechnical] = useState(false);

  // Fetch explanation from API
  const { data: explanation, loading, error } = useApi(
    () => fetchApi(`/api/explanations/alert/${alertId}?top_n=10`),
    [alertId]
  );

  if (loading) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-white">Why SentinelOneWay Detected This</h2>
        </div>
        <LoadingSpinner message="Generating explanation..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-white">Why SentinelOneWay Detected This</h2>
        </div>
        <div className="flex items-start gap-2 text-gray-400">
          <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
          <p className="text-sm">
            Unable to generate explanation. This may occur if the alert was created before
            explainability features were enabled, or if features were not stored with the alert.
          </p>
        </div>
      </div>
    );
  }

  if (!explanation) {
    return null;
  }

  // Determine confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-400';
    if (confidence >= 0.7) return 'text-yellow-400';
    return 'text-orange-400';
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-blue-400" />
          <div>
            <h2 className="text-xl font-semibold text-white">Why SentinelOneWay Detected This</h2>
            <p className="text-sm text-gray-400 mt-1">
              AI-powered explanation based on network behavior analysis
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-400">ML Confidence</div>
          <div className={`text-2xl font-bold ${getConfidenceColor(explanation.confidence)}`}>
            {(explanation.confidence * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Human-Readable Explanations */}
      <div>
        <h3 className="text-lg font-medium text-white mb-3">Detection Reasoning</h3>
        <div className="space-y-3">
          {explanation.human_explanation && explanation.human_explanation.length > 0 ? (
            explanation.human_explanation.map((reason, index) => (
              <div key={index} className="flex items-start gap-3 bg-gray-800/50 p-3 rounded-lg">
                <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-400 text-sm font-semibold">{index + 1}</span>
                </div>
                <p className="text-gray-300 leading-relaxed">{reason}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-400 text-sm">No explanation available</p>
          )}
        </div>
      </div>

      {/* Class Probabilities */}
      {explanation.all_class_probabilities && (
        <div>
          <h3 className="text-lg font-medium text-white mb-3">Classification Probabilities</h3>
          <div className="space-y-2">
            {Object.entries(explanation.all_class_probabilities)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 5)
              .map(([className, probability]) => (
                <div key={className} className="flex items-center gap-3">
                  <div className="w-32 text-sm text-gray-400">{className.replace(/_/g, ' ')}</div>
                  <div className="flex-1 bg-gray-800 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full ${
                        probability > 0.5 ? 'bg-red-500' :
                        probability > 0.2 ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${probability * 100}%` }}
                    />
                  </div>
                  <div className="w-16 text-right text-sm text-gray-300">
                    {(probability * 100).toFixed(1)}%
                  </div>
                </div>
              ))
            }
          </div>
        </div>
      )}

      {/* Technical Evidence (Expandable) */}
      <div>
        <button
          onClick={() => setShowTechnical(!showTechnical)}
          className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors w-full"
        >
          <BarChart3 className="w-5 h-5" />
          <span className="font-medium">Technical AI Evidence</span>
          {showTechnical ? (
            <ChevronUp className="w-5 h-5 ml-auto" />
          ) : (
            <ChevronDown className="w-5 h-5 ml-auto" />
          )}
        </button>

        {showTechnical && explanation.technical_explanation && (
          <div className="mt-4 space-y-2">
            <div className="text-sm text-gray-400 mb-2">
              Top features that influenced this classification (sorted by importance)
            </div>

            {/* Table */}
            <div className="bg-gray-800/50 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-800">
                  <tr>
                    <th className="text-left p-3 text-gray-300 font-medium">Feature</th>
                    <th className="text-right p-3 text-gray-300 font-medium">Value</th>
                    <th className="text-right p-3 text-gray-300 font-medium">Importance</th>
                    <th className="text-center p-3 text-gray-300 font-medium">Impact</th>
                  </tr>
                </thead>
                <tbody>
                  {explanation.technical_explanation.map((item, index) => (
                    <tr
                      key={index}
                      className="border-t border-gray-700 hover:bg-gray-700/30 transition-colors"
                    >
                      <td className="p-3 text-gray-300 font-mono text-xs">
                        {item.feature}
                      </td>
                      <td className="p-3 text-right text-gray-300 font-mono text-xs">
                        {typeof item.value === 'number' ? item.value.toFixed(2) : item.value}
                      </td>
                      <td className="p-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <div className="w-16 bg-gray-700 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="h-full bg-blue-500"
                              style={{ width: `${item.importance * 100}%` }}
                            />
                          </div>
                          <span className="text-gray-300 w-12 text-right">
                            {(item.importance * 100).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        {item.impact === 'positive' ? (
                          <span className="px-2 py-1 text-xs rounded-full bg-red-500/20 text-red-400">
                            Attack
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs rounded-full bg-gray-700 text-gray-400">
                            N/A
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="text-xs text-gray-500 mt-2">
              * Importance scores show how much each feature contributed to the final classification.
              Higher scores indicate stronger influence on the decision.
            </div>
          </div>
        )}
      </div>

      {/* Model Info */}
      <div className="border-t border-gray-800 pt-4">
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <div>
            <span className="text-gray-400">Model:</span> Random Forest Classifier
          </div>
          <div>
            <span className="text-gray-400">Predicted Class:</span> {explanation.predicted_class}
          </div>
          <div>
            <span className="text-gray-400">Alert Class:</span> {explanation.alert_threat_class}
          </div>
        </div>
      </div>
    </div>
  );
}
