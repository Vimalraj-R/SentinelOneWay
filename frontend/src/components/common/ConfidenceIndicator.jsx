/**
 * Confidence Indicator
 * Shows AI model confidence (distinct from risk score)
 */
import { Brain } from 'lucide-react';

export default function ConfidenceIndicator({ confidence, size = 'md', showLabel = true }) {
  // Confidence is 0.0-1.0, display as percentage
  const percentage = Math.round(confidence * 100);

  const getConfidenceLevel = (pct) => {
    if (pct >= 90) return { label: 'Very Confident', color: 'blue' };
    if (pct >= 70) return { label: 'Confident', color: 'blue' };
    if (pct >= 50) return { label: 'Moderate', color: 'yellow' };
    return { label: 'Low Confidence', color: 'gray' };
  };

  const conf = getConfidenceLevel(percentage);

  const colorClasses = {
    blue: 'text-blue-400',
    yellow: 'text-yellow-400',
    gray: 'text-gray-400'
  };

  const sizeClasses = {
    sm: 'text-base',
    md: 'text-lg',
    lg: 'text-2xl'
  };

  return (
    <div className="inline-flex items-center gap-2">
      {size !== 'sm' && <Brain className={`w-4 h-4 ${colorClasses[conf.color]}`} />}
      <div className={`font-semibold ${colorClasses[conf.color]} ${sizeClasses[size]}`}>
        {percentage}%
      </div>
      {showLabel && (
        <div className="text-xs text-gray-500">
          AI Confidence
        </div>
      )}
    </div>
  );
}
