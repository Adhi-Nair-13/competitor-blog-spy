const API_BASE = "http://127.0.0.1:8000/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  try {
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      let errorDetail = response.statusText;
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || errorJson.message || JSON.stringify(errorJson);
      } catch (e) {
        // Fallback to text
      }
      throw new Error(errorDetail || `Request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Competitors
  getCompetitors: () => request("/competitors"),
  getCompetitor: (id) => request(`/competitors/${id}`),
  createCompetitor: (data) => request("/competitors", { method: "POST", body: JSON.stringify(data) }),
  updateCompetitor: (id, data) => request(`/competitors/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteCompetitor: (id) => request(`/competitors/${id}`, { method: "DELETE" }),
  reanalyzeCompetitor: (id) => request(`/competitors/${id}/analyze`, { method: "POST" }),
  triggerCheck: (id) => request(`/competitors/${id}/check`, { method: "POST" }),

  // Articles
  getArticles: (params = {}) => {
    const query = new URLSearchParams();
    if (params.competitor_id) query.append("competitor_id", params.competitor_id);
    if (params.detection_method) query.append("detection_method", params.detection_method);
    if (params.search) query.append("search", params.search);
    if (params.limit) query.append("limit", params.limit);
    if (params.offset) query.append("offset", params.offset);
    return request(`/articles?${query.toString()}`);
  },
  getArticle: (id) => request(`/articles/${id}`),

  // Monitoring
  getMonitoringHistory: (params = {}) => {
    const query = new URLSearchParams();
    if (params.competitor_id) query.append("competitor_id", params.competitor_id);
    if (params.status) query.append("status", params.status);
    if (params.detection_method) query.append("detection_method", params.detection_method);
    if (params.limit) query.append("limit", params.limit);
    if (params.offset) query.append("offset", params.offset);
    return request(`/monitoring/history?${query.toString()}`);
  },
  runAllChecks: () => request("/monitoring/run-all", { method: "POST" }),

  // Dashboard & Analytics
  getDashboardStats: () => request("/dashboard/stats"),
  getAnalytics: () => request("/analytics"),

  // Notifications
  getNotifications: (limit = 50) => request(`/notifications?limit=${limit}`),
  getUnreadCount: () => request("/notifications/unread-count"),
  markNotificationRead: (id) => request(`/notifications/${id}/read`, { method: "PUT" }),
  markAllNotificationsRead: () => request("/notifications/read-all", { method: "POST" }),

  // Settings & System
  getSettings: () => request("/settings"),
  updateSettings: (data) => request("/settings", { method: "POST", body: JSON.stringify(data) }),
  getSystemStatus: () => request("/system/status"),

  // Scale Test
  startScaleTest: (data) => request("/scale-test/start", { method: "POST", body: JSON.stringify(data) }),
  getScaleTestStatus: () => request("/scale-test/status"),

  // Demo Helpers
  seedDemoCompetitor: () => request("/demo/seed", { method: "POST" }),
  publishTestArticle: () => request("/demo/publish-test-article", { method: "POST" }),
};
