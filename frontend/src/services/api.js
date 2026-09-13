/**
 * Centralized API service for SentinelOneWay backend.
 *
 * All API calls should go through this service to maintain
 * consistency and simplify error handling.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic API error class
 */
class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    // Parse response
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new ApiError(
        data.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        data
      );
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Network or other errors
    throw new ApiError(
      'Unable to connect to the backend. Please check if the server is running.',
      0,
      null
    );
  }
}

/**
 * Alert API
 */
export const alertsApi = {
  /**
   * Get list of alerts with optional filters
   */
  getAlerts: async ({ skip = 0, limit = 100, severity = null, status = null } = {}) => {
    const params = new URLSearchParams();
    params.append('skip', skip);
    params.append('limit', limit);
    if (severity) params.append('severity', severity);
    if (status) params.append('status', status);

    return fetchApi(`/api/alerts?${params.toString()}`);
  },

  /**
   * Get single alert by ID
   */
  getAlertById: async (id) => {
    return fetchApi(`/api/alerts/${id}`);
  },

  /**
   * Create new alert
   */
  createAlert: async (alertData) => {
    return fetchApi('/api/alerts', {
      method: 'POST',
      body: JSON.stringify(alertData),
    });
  },

  /**
   * Update alert status
   */
  updateAlertStatus: async (id, status) => {
    return fetchApi(`/api/alerts/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },
};

/**
 * Metrics API
 */
export const metricsApi = {
  /**
   * Get current network metrics
   */
  getCurrent: async () => {
    return fetchApi('/api/metrics/current');
  },

  /**
   * Get historical network metrics
   */
  getHistory: async ({ hours = 24, limit = 100 } = {}) => {
    const params = new URLSearchParams();
    params.append('hours', hours);
    params.append('limit', limit);

    return fetchApi(`/api/metrics/history?${params.toString()}`);
  },
};

/**
 * Assets API
 */
export const assetsApi = {
  /**
   * Get list of assets
   */
  getAssets: async ({ skip = 0, limit = 100 } = {}) => {
    const params = new URLSearchParams();
    params.append('skip', skip);
    params.append('limit', limit);

    return fetchApi(`/api/assets?${params.toString()}`);
  },

  /**
   * Get single asset by ID
   */
  getAssetById: async (id) => {
    return fetchApi(`/api/assets/${id}`);
  },
};

/**
 * Dashboard API
 */
export const dashboardApi = {
  /**
   * Get dashboard summary data
   */
  getSummary: async () => {
    return fetchApi('/api/dashboard/summary');
  },
};

/**
 * Health check
 */
export const healthApi = {
  check: async () => {
    return fetchApi('/health');
  },
};

/**
 * Export error class for component use
 */
export { ApiError };
