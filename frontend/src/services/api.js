/**
 * Centralized API Service for FraudGraph Frontend.
 */

const API_BASE_URL = '/api';

/**
 * Generic fetch wrapper with JSON error handling.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();
    if (!response.ok) {
      const errorMsg = data?.message || `Request failed with status ${response.status}`;
      throw new Error(errorMsg);
    }
    return data;
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err.message);
    throw err;
  }
}

export const apiService = {
  /** Health check */
  getHealth: () => request('/health'),

  /** Dashboard metrics & risk distributions */
  getDashboard: () => request('/dashboard'),

  /** Paginated customer list with filters */
  getCustomers: (params = {}) => {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page);
    if (params.pageSize) query.append('page_size', params.pageSize);
    if (params.riskLevel && params.riskLevel !== 'ALL') query.append('risk_level', params.riskLevel);
    if (params.ringId) query.append('ring_id', params.ringId);
    if (params.minRiskScore) query.append('minimum_risk_score', params.minRiskScore);
    if (params.search) query.append('search', params.search);

    const queryString = query.toString();
    return request(`/customers${queryString ? `?${queryString}` : ''}`);
  },

  /** Customer forensic profile */
  getCustomer: (customerId) => request(`/customers/${encodeURIComponent(customerId)}`),

  /** Transaction details */
  getTransaction: (transactionId) => request(`/transactions/${encodeURIComponent(transactionId)}`),

  /** Fraud rings directory */
  getFraudRings: (params = {}) => {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page);
    if (params.pageSize) query.append('page_size', params.pageSize);
    const queryString = query.toString();
    return request(`/fraud-rings${queryString ? `?${queryString}` : ''}`);
  },

  /** Fraud ring forensic dossier */
  getFraudRing: (ringId) => request(`/fraud-rings/${encodeURIComponent(ringId)}`),

  /** Phase 4 investigation report */
  getInvestigation: (entityType, entityId) =>
    request(`/investigation/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}`),

  /** Cytoscape network graph */
  getNetwork: (entityType, entityId) =>
    request(`/network/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}`),
};

export default apiService;
