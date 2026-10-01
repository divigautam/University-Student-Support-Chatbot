const API_BASE = '';

const api = {
  getToken: () => localStorage.getItem('token'),
  setToken: (token) => localStorage.setItem('token', token),
  clearToken: () => localStorage.removeItem('token'),

  async apiRequest(endpoint, options = {}) {
    const headers = { ...options.headers };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      if (response.status === 401 && endpoint !== '/auth/login' && endpoint !== '/auth/register') {
        this.clearToken();
        window.location.href = '/login.html';
        return;
      }

      const isJson = response.headers.get('content-type')?.includes('application/json');
      const data = isJson ? await response.json() : null;

      if (!response.ok) {
        throw new Error(data?.detail || data?.message || `Error ${response.status}`);
      }

      return data;
    } catch (err) {
      throw err;
    }
  },

  login: (email, password) => api.apiRequest('/auth/login', { method: 'POST', body: { email, password } }),
  register: (username, email, password) => api.apiRequest('/auth/register', { method: 'POST', body: { username, email, password } }),
  getMe: () => api.apiRequest('/auth/me'),
  sendMessage: (message, conversation_id) => api.apiRequest('/chat', { method: 'POST', body: { message, conversation_id } }),
  getConversations: () => api.apiRequest('/conversations'),
  getMessages: (id) => api.apiRequest(`/conversations/${id}/messages`),
  deleteConversation: (id) => api.apiRequest(`/conversations/${id}`, { method: 'DELETE' }),
  submitFeedback: (message_id, rating, comment) => api.apiRequest('/feedback', { method: 'POST', body: { message_id, rating, comment } }),
  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.apiRequest('/admin/documents/upload', { method: 'POST', body: formData });
  },
  getDocuments: () => api.apiRequest('/admin/documents'),
  deleteDocument: (id) => api.apiRequest(`/admin/documents/${id}`, { method: 'DELETE' }),
  reindexDocument: (id) => api.apiRequest(`/admin/documents/${id}/reindex`, { method: 'POST' }),
  getDashboard: () => api.apiRequest('/analytics/dashboard'),
  getFeedbackStats: () => api.apiRequest('/feedback/stats'),
  healthCheck: () => api.apiRequest('/health')
};

window.api = api;
