/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
  const BACKEND_URL = "http://127.0.0.1:8000";

  const pathname = event.url.pathname;

  // Proxy API
  if (pathname.startsWith("/api")) {
    // strip "/api"
    const path = pathname.replace(/^\/api/, "");

    const url = `${BACKEND_URL}${path}${event.url.search}`;

    return fetch(url, {
      method: event.request.method,
      headers: event.request.headers,
      body: event.request.body,
      duplex: "half"
    });
  }

  // Proxy static files
  if (pathname.startsWith("/static")) {
    const url = `${BACKEND_URL}${pathname}${event.url.search}`;

    return fetch(url, {
      method: event.request.method,
      headers: event.request.headers,
      body: event.request.body,
      duplex: "half"
    });
  }

  return resolve(event);
}