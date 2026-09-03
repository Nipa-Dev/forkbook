const API_URL = 'http://127.0.0.1:8000';

export async function api(path, options = {}, svelteFetch = null) {
  const fetcher = svelteFetch || fetch;

  const headers = new Headers(options.headers);
  let body = options.body;

  if (body instanceof FormData) {
    headers.delete('content-type');
  } else if (!headers.has('content-type')) {
    headers.set('content-type', 'application/json');
  }

  const res = await fetcher(`${API_URL}${path}`, {
    ...options,
    headers,
    body
  });

  if (res.status === 401 || res.status === 403) {
    const err = new Error('401_UNAUTHORIZED');
    err.status = res.status;
    throw err;
  }

  if (!res.ok) {
    const err = new Error(`API error: ${res.status}`);
    err.status = res.status;
    throw err;
  }

  return res.json();
}
