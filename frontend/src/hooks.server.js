import { redirect } from '@sveltejs/kit';
import { createRemoteJWKSet, jwtVerify } from 'jose';
import { dev } from '$app/environment';

const FASTAPI_JWKS_URL = new URL('http://localhost:8000/.well-known/jwks.json');
const JWKS = createRemoteJWKSet(FASTAPI_JWKS_URL);

export async function handle({ event, resolve }) {
  const token = event.cookies.get('session_token');
  const { pathname, search } = event.url;

  const isAuthPage = pathname === '/login' || pathname.startsWith('/signup');
  const isApiRoute = pathname.startsWith('/api') || pathname.startsWith('/auth');

  let isAuthenticated = false;

  if (token) {
    try {
      // Verify the signature and expiration
      await jwtVerify(token, JWKS);
      isAuthenticated = true;
    } catch (err) {
      console.error('JWT Verification failed:', err?.message || err);
      event.cookies.delete('session_token', { path: '/' });
    }
  }
  event.locals.isAuthenticated = isAuthenticated;

  if (isAuthenticated && isAuthPage) {
    redirect(303, '/recipes');
  }

  if (!isAuthenticated && !isAuthPage && !isApiRoute) {
    const fromUrl = pathname + search;
    redirect(303, `/login?redirectTo=${encodeURIComponent(fromUrl)}`);
  }

  return resolve(event);
}

export async function handleError({ error, event }) {
  const status = error.status || error.response?.status;
  const msg = error.message || '';

  // Catch 401/403 errors
  if (msg.includes('401_UNAUTHORIZED') || status === 401 || status === 403) {
    event.cookies.delete('session_token', { path: '/' });
  }
  console.error('Unhandled Error:', error);
  // Fallback for other errors
  return {
    message: dev ? msg || 'No message provided' : 'An unexpected error occurred.',
    code: error?.code || 'SERVER_ERROR'
  };
}
