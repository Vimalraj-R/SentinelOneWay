import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Bell, CheckCircle, AlertTriangle, Clock, X } from 'lucide-react';

export default function TopBar() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch recent alerts for notifications
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/alerts/recent?limit=10');
        if (response.ok) {
          const data = await response.json();
          setNotifications(data);
          // Count alerts from last 5 minutes as "unread"
          const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
          const unread = data.filter(alert => new Date(alert.timestamp) > fiveMinutesAgo).length;
          setUnreadCount(unread);
        }
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
      }
    };

    fetchNotifications();
    // Refresh every 10 seconds
    const interval = setInterval(fetchNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsNotificationOpen(false);
      }
    };

    if (isNotificationOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isNotificationOpen]);

  const toggleNotifications = () => {
    setIsNotificationOpen(!isNotificationOpen);
    if (!isNotificationOpen) {
      // Mark as read when opened
      setUnreadCount(0);
    }
  };

  const handleNotificationClick = (alertId) => {
    setIsNotificationOpen(false);
    navigate(`/alert/${alertId}`);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Critical': return 'text-red-400 bg-red-500/10';
      case 'High': return 'text-orange-400 bg-orange-500/10';
      case 'Medium': return 'text-yellow-400 bg-yellow-500/10';
      case 'Low': return 'text-green-400 bg-green-500/10';
      default: return 'text-gray-400 bg-gray-500/10';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now - alertTime;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-blue-500" />
            <div>
              <h2 className="text-white font-semibold">SentinelOneWay</h2>
              <p className="text-gray-400 text-xs">Passive Network Intelligence</p>
            </div>
          </div>

          {/* Passive Monitoring Badge */}
          <div className="px-3 py-1.5 bg-blue-900/30 border border-blue-700/50 rounded-full">
            <span className="text-blue-400 text-sm font-medium">🔍 Passive Monitoring</span>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-6">
          {/* Live Status */}
          <div className="flex items-center gap-2">
            <div className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </div>
            <span className="text-green-400 font-medium text-sm">LIVE</span>
          </div>

          {/* Current Time */}
          <div className="text-gray-400 text-sm font-mono">
            {currentTime.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
            })}
          </div>

          {/* Monitoring Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 rounded-lg">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span className="text-gray-300 text-sm">8/8 Sensors Active</span>
          </div>

          {/* Notifications Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={toggleNotifications}
              className="relative p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 flex items-center justify-center min-w-[18px] h-[18px] bg-red-500 text-white text-xs font-bold rounded-full px-1">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {/* Dropdown Panel */}
            {isNotificationOpen && (
              <div className="absolute right-0 mt-2 w-96 bg-gray-800 border border-gray-700 rounded-lg shadow-2xl overflow-hidden z-50">
                {/* Header */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-900">
                  <h3 className="text-white font-semibold">Recent Alerts</h3>
                  <button
                    onClick={() => setIsNotificationOpen(false)}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Notification List */}
                <div className="max-h-[400px] overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="px-4 py-8 text-center">
                      <AlertTriangle className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                      <p className="text-gray-400">No recent alerts</p>
                      <p className="text-gray-500 text-sm mt-1">All clear!</p>
                    </div>
                  ) : (
                    notifications.map((alert) => (
                      <button
                        key={alert.id}
                        onClick={() => handleNotificationClick(alert.id)}
                        className="w-full px-4 py-3 hover:bg-gray-700/50 transition-colors border-b border-gray-700 last:border-b-0 text-left"
                      >
                        <div className="flex items-start gap-3">
                          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                          <div className="flex-1 min-w-0">
                            {/* Threat Type */}
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-white font-medium text-sm">
                                {alert.threat_class?.replace(/_/g, ' ') || 'Unknown Threat'}
                              </span>
                              <span className={`text-xs px-2 py-0.5 rounded-full ${getSeverityColor(alert.severity)}`}>
                                {alert.severity}
                              </span>
                            </div>

                            {/* Source → Destination */}
                            <p className="text-gray-400 text-xs mb-1">
                              {alert.src_ip} → {alert.dst_ip}:{alert.dst_port}
                            </p>

                            {/* Time and Risk */}
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {formatTimeAgo(alert.timestamp)}
                              </span>
                              <span>Risk: {alert.risk_score}/100</span>
                            </div>
                          </div>
                        </div>
                      </button>
                    ))
                  )}
                </div>

                {/* Footer */}
                {notifications.length > 0 && (
                  <div className="px-4 py-3 bg-gray-900 border-t border-gray-700">
                    <button
                      onClick={() => {
                        setIsNotificationOpen(false);
                        navigate('/threat-alerts');
                      }}
                      className="w-full text-center text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
                    >
                      View All Alerts →
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
