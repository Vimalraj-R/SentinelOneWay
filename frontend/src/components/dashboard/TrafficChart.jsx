import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, ComposedChart } from 'recharts';
import { Activity, AlertTriangle, TrendingUp, Eye } from 'lucide-react';

export default function TrafficChart({ data }) {
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-xl">
          <p className="text-gray-300 text-sm font-medium mb-3">{payload[0].payload.time}</p>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-400"></div>
              <span className="text-gray-400 text-xs">Network Flows:</span>
              <span className="text-blue-400 text-sm font-bold ml-auto">
                {payload[0].value.toLocaleString()}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-400"></div>
              <span className="text-gray-400 text-xs">Threats:</span>
              <span className="text-red-400 text-sm font-bold ml-auto">
                {payload[1].value}
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  // Calculate stats from data
  const avgFlows = data.length > 0
    ? Math.round(data.reduce((sum, d) => sum + d.flows, 0) / data.length)
    : 0;
  const totalThreats = data.reduce((sum, d) => sum + d.threats, 0);
  const peakFlows = data.length > 0
    ? Math.max(...data.map(d => d.flows))
    : 0;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 h-full w-full flex flex-col">
      {/* Header with Stats */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-white font-semibold">Traffic Activity (24h)</h3>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-blue-400" />
            <span className="text-gray-400">Avg:</span>
            <span className="text-white font-medium">{avgFlows.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-gray-400">Peak:</span>
            <span className="text-white font-medium">{peakFlows.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span className="text-gray-400">Threats:</span>
            <span className="text-white font-medium">{totalThreats}</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="flex-1 min-h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <defs>
              <linearGradient id="flowsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
            <XAxis
              dataKey="time"
              stroke="#6b7280"
              style={{ fontSize: '11px' }}
              tick={{ fill: '#9ca3af' }}
            />
            <YAxis
              stroke="#6b7280"
              style={{ fontSize: '11px' }}
              tick={{ fill: '#9ca3af' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '13px', paddingTop: '16px' }}
              iconType="circle"
            />
            <Area
              type="monotone"
              dataKey="flows"
              fill="url(#flowsGradient)"
              stroke="none"
            />
            <Line
              type="monotone"
              dataKey="flows"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
              name="Network Flows"
            />
            <Line
              type="monotone"
              dataKey="threats"
              stroke="#ef4444"
              strokeWidth={3}
              dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
              name="Threats Detected"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
