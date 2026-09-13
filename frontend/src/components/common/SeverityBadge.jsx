/**
 * Consistent Severity Badge
 * Unified severity display across the application
 */

const SEVERITY_CONFIG = {
  Critical: {
    bg: 'bg-red-500/20',
    text: 'text-red-400',
    border: 'border-red-500',
    label: 'Critical'
  },
  High: {
    bg: 'bg-orange-500/20',
    text: 'text-orange-400',
    border: 'border-orange-500',
    label: 'High'
  },
  Medium: {
    bg: 'bg-yellow-500/20',
    text: 'text-yellow-400',
    border: 'border-yellow-500',
    label: 'Medium'
  },
  Low: {
    bg: 'bg-green-500/20',
    text: 'text-green-400',
    border: 'border-green-500',
    label: 'Low'
  }
};

export default function SeverityBadge({ severity, size = 'md', showLabel = true }) {
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.Medium;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5'
  };

  return (
    <span className={`
      inline-flex items-center justify-center
      rounded-full border font-semibold
      ${config.bg} ${config.text} ${config.border} ${sizeClasses[size]}
    `}>
      {showLabel ? config.label : severity}
    </span>
  );
}

export { SEVERITY_CONFIG };
