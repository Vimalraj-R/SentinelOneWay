/**
 * Risk Score Indicator
 * Clear visual representation of risk score (0-100)
 * Distinct from confidence scores
 */
import { AlertTriangle } from 'lucide-react';

export default function RiskIndicator({ score, size = 'md', showLabel = true }) {
  const getRiskLevel = (score) => {
    if (score >= 85) return { label: 'Critical Risk', color: 'red' };
    if (score >= 70) return { label: 'High Risk', color: 'orange' };
    if (score >= 50) return { label: 'Elevated Risk', color: 'yellow' };
    if (score >= 30) return { label: 'Moderate Risk', color: 'blue' };
    return { label: 'Low Risk', color: 'green' };
  };

  const risk = getRiskLevel(score);

  const colorClasses = {
    red: 'text-red-400 bg-red-500/20 border-red-500',
    orange: 'text-orange-400 bg-orange-500/20 border-orange-500',
    yellow: 'text-yellow-400 bg-yellow-500/20 border-yellow-500',
    blue: 'text-blue-400 bg-blue-500/20 border-blue-500',
    green: 'text-green-400 bg-green-500/20 border-green-500'
  };

  const sizeClasses = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-4xl'
  };

  return (
    <div className={`inline-flex flex-col items-center gap-2 ${colorClasses[risk.color]} border rounded-xl p-4`}>
      {size !== 'sm' && <AlertTriangle className="w-6 h-6" />}
      <div className={`font-bold ${sizeClasses[size]}`}>
        {score}<span className="text-base">/100</span>
      </div>
      {showLabel && (
        <div className="text-xs font-semibold uppercase tracking-wide">
          {risk.label}
        </div>
      )}
    </div>
  );
}
