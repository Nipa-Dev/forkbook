const API_URL = 'http://127.0.0.1:8000';

export async function api(path, options = {}, svelteFetch = null) {
  const fetcher = svelteFetch || fetch;

  const res = await fetcher(`${API_URL}${path}`, {
    ...options,
    headers: {
      'content-type': 'application/json',
      ...(options.headers || {})
    }
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
