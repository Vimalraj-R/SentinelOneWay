import { Shield, AlertTriangle } from 'lucide-react';

export default function RiskPanel({ risk, confidence }) {
  const getRiskColor = (score) => {
    if (score >= 80) return { bg: 'bg-red-500', text: 'text-red-400', label: 'Critical Risk' };
    if (score >= 60) return { bg: 'bg-orange-500', text: 'text-orange-400', label: 'High Risk' };
    if (score >= 40) return { bg: 'bg-yellow-500', text: 'text-yellow-400', label: 'Medium Risk' };
    return { bg: 'bg-green-500', text: 'text-green-400', label: 'Low Risk' };
  };

  const color = getRiskColor(risk.score);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Shield className="w-5 h-5 text-red-400" />
        <h2 className="text-xl font-semibold text-white">Risk Assessment</h2>
      </div>

      {/* Risk Score Circle */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative w-32 h-32">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="10"
              fill="none"
              className="text-gray-800"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="10"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 56}`}
              strokeDashoffset={`${2 * Math.PI * 56 * (1 - risk.score / 100)}`}
              className={color.text}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${color.text}`}>{risk.score}</span>
            <span className="text-gray-400 text-xs">/100</span>
          </div>
        </div>
      </div>

      {/* Risk Details */}
      <div className="space-y-3">
        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <span className="text-gray-400 text-sm">Risk Level</span>
          <span className={`font-semibold ${color.text}`}>{color.label}</span>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <span className="text-gray-400 text-sm">Category</span>
          <span className="text-white font-medium">{risk.category}</span>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <span className="text-gray-400 text-sm">Attack Vector</span>
          <span className="text-white font-medium">{risk.attackVector}</span>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <span className="text-gray-400 text-sm">Asset Criticality</span>
          <span className="text-orange-400 font-medium">{risk.targetedAsset}</span>
        </div>

        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <span className="text-gray-400 text-sm">Model Confidence</span>
          <span className="text-blue-400 font-medium">{(confidence * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
}
