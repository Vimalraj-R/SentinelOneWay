import { Clock } from 'lucide-react';

export default function EventTimeline({ timeline }) {
  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-500 border-red-500';
      case 'high':
        return 'bg-orange-500 border-orange-500';
      case 'warning':
        return 'bg-yellow-500 border-yellow-500';
      case 'low':
        return 'bg-blue-500 border-blue-500';
      default:
        return 'bg-gray-500 border-gray-500';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Clock className="w-5 h-5 text-blue-400" />
        <h2 className="text-xl font-semibold text-white">Event Timeline</h2>
      </div>

      <div className="space-y-4">
        {timeline.map((event, index) => (
          <div key={index} className="flex items-start gap-4">
            {/* Timeline dot and line */}
            <div className="flex flex-col items-center">
              <div className={`w-3 h-3 rounded-full border-2 ${getSeverityColor(event.severity)}`} />
              {index < timeline.length - 1 && (
                <div className="w-0.5 h-full min-h-[40px] bg-gray-700 mt-1" />
              )}
            </div>

            {/* Event content */}
            <div className="flex-1 pb-4">
              <div className="flex items-center gap-3 mb-1">
                <span className="text-white font-mono text-sm font-semibold">{event.time}</span>
                <span
                  className={`px-2 py-0.5 rounded text-xs font-medium ${
                    event.severity === 'critical'
                      ? 'bg-red-500/10 text-red-400'
                      : event.severity === 'high'
                      ? 'bg-orange-500/10 text-orange-400'
                      : event.severity === 'warning'
                      ? 'bg-yellow-500/10 text-yellow-400'
                      : 'bg-blue-500/10 text-blue-400'
                  }`}
                >
                  {event.severity}
                </span>
              </div>
              <p className="text-gray-300 text-sm">{event.event}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
