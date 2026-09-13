import { Shield, AlertTriangle, TrendingUp } from 'lucide-react';

export default function RiskGauge({ score }) {
  const getColor = (score) => {
    if (score >= 80) return {
      bg: 'bg-red-500',
      text: 'text-red-500',
      label: 'Critical',
      borderColor: 'border-red-500/30',
      bgGradient: 'from-red-500/20 to-red-500/5'
    };
    if (score >= 60) return {
      bg: 'bg-yellow-500',
      text: 'text-yellow-500',
      label: 'Elevated',
      borderColor: 'border-yellow-500/30',
      bgGradient: 'from-yellow-500/20 to-yellow-500/5'
    };
    if (score >= 40) return {
      bg: 'bg-blue-500',
      text: 'text-blue-500',
      label: 'Moderate',
      borderColor: 'border-blue-500/30',
      bgGradient: 'from-blue-500/20 to-blue-500/5'
    };
    return {
      bg: 'bg-green-500',
      text: 'text-green-500',
      label: 'Low',
      borderColor: 'border-green-500/30',
      bgGradient: 'from-green-500/20 to-green-500/5'
    };
  };

  const color = getColor(score);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 h-full w-full flex flex-col">
      <h3 className="text-white font-semibold mb-6">Network Risk Score</h3>

      {/* Main Gauge Container */}
      <div className="flex items-center justify-center flex-1">
        <div className="relative">
          {/* Larger Circular Gauge */}
          <div className="relative w-56 h-56">
            {/* Background Circle */}
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="112"
                cy="112"
                r="100"
                stroke="currentColor"
                strokeWidth="16"
                fill="none"
                className="text-gray-800"
              />
              {/* Progress Circle */}
              <circle
                cx="112"
                cy="112"
                r="100"
                stroke="currentColor"
                strokeWidth="16"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 100}`}
                strokeDashoffset={`${2 * Math.PI * 100 * (1 - score / 100)}`}
                className={color.text}
                strokeLinecap="round"
              />
            </svg>

            {/* Center Content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className={`w-12 h-12 rounded-full ${color.bg} bg-opacity-20 flex items-center justify-center mb-3`}>
                <Shield className={`w-6 h-6 ${color.text}`} />
              </div>
              <span className={`text-6xl font-bold ${color.text}`}>{score}</span>
              <span className="text-gray-400 text-base mt-1">/ 100</span>
              <span className={`text-sm font-medium ${color.text} mt-2`}>{color.label}</span>
            </div>
          </div>

          {/* Decorative Corner Indicators */}
          <div className={`absolute -top-2 -right-2 w-8 h-8 rounded-full ${color.bg} bg-opacity-20 flex items-center justify-center`}>
            <TrendingUp className={`w-4 h-4 ${color.text}`} />
          </div>
        </div>
      </div>

      {/* Bottom Stats Row */}
      <div className="grid grid-cols-3 gap-3 mt-6 pt-4 border-t border-gray-800">
        <div className="text-center">
          <div className="text-gray-400 text-xs mb-1">Threats</div>
          <div className={`text-xl font-bold ${color.text}`}>
            {score >= 80 ? '4+' : score >= 60 ? '2-3' : score >= 40 ? '1-2' : '0'}
          </div>
        </div>
        <div className="text-center border-x border-gray-800">
          <div className="text-gray-400 text-xs mb-1">Assets</div>
          <div className="text-xl font-bold text-white">8</div>
        </div>
        <div className="text-center">
          <div className="text-gray-400 text-xs mb-1">Status</div>
          <div className="flex items-center justify-center">
            <div className={`w-2 h-2 rounded-full ${color.bg} mr-1`}></div>
            <span className={`text-xs font-medium ${color.text}`}>
              {color.label}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
