import { AlertTriangle, RefreshCw } from 'lucide-react';

/**
 * Error message component with retry option
 */
export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-red-500/5 border border-red-500/20 rounded-xl">
      <AlertTriangle className="w-12 h-12 text-red-400 mb-4" />
      <h3 className="text-white font-semibold mb-2">Unable to Load Data</h3>
      <p className="text-gray-400 text-sm text-center mb-4 max-w-md">
        {message || 'An error occurred while fetching data from the server.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      )}
    </div>
  );
}
