const envApi = import.meta.env.VITE_API_URL as string | undefined;
export const API_BASE = envApi ? envApi.replace(/\/$/, '') : 'http://127.0.0.1:8000/api/v1';

const defaultWs = API_BASE.startsWith('https://') 
  ? API_BASE.replace('https://', 'wss://') + '/ws'
  : API_BASE.replace('http://', 'ws://') + '/ws';

export const WS_BASE = (import.meta.env.VITE_WS_URL as string | undefined) || defaultWs;

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (options.body && typeof options.body === 'string' && !headers.has('Content-Type')) {
      if (options.body.startsWith('{') || options.body.startsWith('[')) {
          headers.set('Content-Type', 'application/json');
      }
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem('access_token');
    window.dispatchEvent(new Event('auth-error'));
  }

  return response;
}
