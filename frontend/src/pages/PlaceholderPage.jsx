import { Construction } from 'lucide-react';

export default function PlaceholderPage({ title, description, icon: Icon }) {
  return (
    <div className="flex items-center justify-center h-full bg-gray-950">
      <div className="text-center max-w-md">
        <div className="inline-flex items-center justify-center w-24 h-24 bg-gray-900 border border-gray-800 rounded-2xl mb-6">
          {Icon ? (
            <Icon className="w-12 h-12 text-gray-400" />
          ) : (
            <Construction className="w-12 h-12 text-gray-400" />
          )}
        </div>
        <h2 className="text-2xl font-bold text-white mb-3">{title}</h2>
        <p className="text-gray-400 mb-6">{description}</p>
        <div className="inline-flex px-4 py-2 bg-blue-600/10 border border-blue-600/20 rounded-lg">
          <span className="text-blue-400 text-sm font-medium">Coming in Phase 3</span>
        </div>
      </div>
    </div>
  );
}
