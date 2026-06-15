const API_URL = "http://127.0.0.1:8000";

export async function api(path, options = {}, svelteFetch = null) {
    const fetcher = svelteFetch || fetch;

    const res = await fetcher(`${API_URL}${path}`, {
        ...options,
        headers: {
            'content-type': 'application/json',
            ...(options.headers || {})
        }
    });

    if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
    }

    return res.json();
}