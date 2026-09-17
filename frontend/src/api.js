const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}, token) {
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || 'The request could not be completed.');
  return body;
}

export const api = {
  register: (email, password) => request('/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) }),
  login: (email, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  projects: (token) => request('/projects', {}, token),
  createProject: (token, project) => request('/projects', { method: 'POST', body: JSON.stringify(project) }, token),
  sites: (token, projectId) => request(`/projects/${projectId}/sites`, {}, token),
  createSite: (token, projectId, site) => request(`/projects/${projectId}/sites`, { method: 'POST', body: JSON.stringify(site) }, token),
};
