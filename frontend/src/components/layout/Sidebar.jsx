import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Activity,
  AlertTriangle,
  Clock,
  Server,
  Microscope,
  HeartPulse
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/live-traffic', label: 'Live Traffic', icon: Activity },
  { path: '/threat-alerts', label: 'Threat Alerts', icon: AlertTriangle },
  { path: '/attack-timeline', label: 'Attack Timeline', icon: Clock },
  { path: '/assets', label: 'Assets', icon: Server },
  { path: '/simulation-lab', label: 'Simulation Lab', icon: Microscope },
  { path: '/system-health', label: 'System Health', icon: HeartPulse }
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="text-white font-semibold text-lg">SentinelOneWay</h1>
            <p className="text-gray-400 text-xs">Network Detection</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500 text-center">
          v1.0.0 - Complete MVP
        </div>
      </div>
    </aside>
  );
}
