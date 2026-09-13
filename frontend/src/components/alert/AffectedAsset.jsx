import { Server, MapPin, User } from 'lucide-react';

export default function AffectedAsset({ asset }) {
  const getCriticalityColor = (criticality) => {
    switch (criticality.toLowerCase()) {
      case 'critical':
        return 'text-red-400 bg-red-500/10';
      case 'high':
        return 'text-orange-400 bg-orange-500/10';
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/10';
      case 'low':
        return 'text-green-400 bg-green-500/10';
      default:
        return 'text-gray-400 bg-gray-500/10';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Server className="w-5 h-5 text-blue-400" />
        <h2 className="text-xl font-semibold text-white">Affected Asset</h2>
      </div>

      <div className="space-y-4">
        {/* Hostname and IP */}
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <div className="text-gray-400 text-xs mb-1">Hostname</div>
          <div className="text-white text-lg font-semibold">{asset.hostname}</div>
          <div className="text-gray-400 font-mono text-sm mt-1">{asset.ip}</div>
        </div>

        {/* Criticality Badge */}
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-sm">Criticality:</span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCriticalityColor(asset.criticality)}`}>
            {asset.criticality}
          </span>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 gap-3">
          <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
            <span className="text-gray-400 text-sm">Role</span>
            <span className="text-white font-medium">{asset.role}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="text-gray-400 text-sm">Location</span>
            </div>
            <span className="text-white font-medium">{asset.location}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-gray-400" />
              <span className="text-gray-400 text-sm">Owner</span>
            </div>
            <span className="text-white font-medium">{asset.owner}</span>
          </div>

          {asset.user && (
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
              <span className="text-gray-400 text-sm">Last User</span>
              <span className="text-white font-mono text-sm">{asset.user}</span>
            </div>
          )}

          {asset.lastLogin && (
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
              <span className="text-gray-400 text-sm">Last Login</span>
              <span className="text-white font-mono text-sm">{asset.lastLogin}</span>
            </div>
          )}
        </div>

        {/* Services */}
        {asset.services && asset.services.length > 0 && (
          <div className="pt-4 border-t border-gray-800">
            <div className="text-gray-400 text-sm mb-3">Running Services</div>
            <div className="flex flex-wrap gap-2">
              {asset.services.map((service, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-500/10 text-blue-400 rounded-full text-xs font-medium"
                >
                  {service}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
