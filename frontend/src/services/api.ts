const envApi = import.meta.env.VITE_API_URL as string | undefined;

export const API_BASE = envApi 
  ? envApi.replace(/\/$/, '') 
  : (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      ? '/api/v1' 
      : 'http://127.0.0.1:8000/api/v1');

const defaultWs = API_BASE.startsWith('https://') 
  ? API_BASE.replace('https://', 'wss://').replace(/\/api\/v1$/, '') + '/ws'
  : API_BASE.startsWith('http://')
    ? API_BASE.replace('http://', 'ws://').replace(/\/api\/v1$/, '') + '/ws'
    : (typeof window !== 'undefined' ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws` : 'ws://127.0.0.1:8000/ws');

export const WS_BASE = (import.meta.env.VITE_WS_URL as string | undefined) || defaultWs;

// ---------------------------------------------------------------------------
// Error helper
// ---------------------------------------------------------------------------

/**
 * Extracts a human-readable message from any thrown value.
 * Works with fetch network errors, HTTP-error objects that carry a `message`
 * field, plain Error instances, and arbitrary unknown values.
 */
export function getErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === 'string') return err;
  if (
    err !== null &&
    typeof err === 'object' &&
    'message' in err &&
    typeof (err as Record<string, unknown>).message === 'string'
  ) {
    return (err as { message: string }).message;
  }
  return 'An unexpected error occurred.';
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

const RETRY_DELAY_MS = 1000;

/** Returns true for errors that are safe to retry (network-level, not HTTP). */
function isNetworkError(err: unknown): boolean {
  // fetch() rejects with a TypeError on network failures (no response at all).
  // 4xx/5xx responses resolve normally and are NOT retried.
  return err instanceof TypeError;
}

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

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

  const requestInit: RequestInit = { ...options, headers };
  const url = `${API_BASE}${endpoint}`;

  // --- attempt with one retry on network error ---
  let response: Response;
  try {
    response = await fetch(url, requestInit);
  } catch (err) {
    if (isNetworkError(err)) {
      await sleep(RETRY_DELAY_MS);
      // Second attempt — let any error propagate to the caller.
      response = await fetch(url, requestInit);
    } else {
      throw err;
    }
  }

  // --- 401: clear tokens and redirect to login ---
  if (response.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.dispatchEvent(new Event('auth-error'));
    // Hard-redirect so the user lands on the login page regardless of which
    // router state they were in, preventing any broken authenticated view.
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  return response;
}
