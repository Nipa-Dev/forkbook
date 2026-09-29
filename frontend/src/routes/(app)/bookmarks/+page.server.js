import { fail } from '@sveltejs/kit';
import { api } from '$lib/server/api';

export async function load({ fetch, cookies }) {
  const token = cookies.get('session_token');

  try {
    const recipes = await api(
      '/recipes/saved?flag_type=bookmark',
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`
        }
      },
      fetch
    );

    return { recipes };
  } catch (error) {
    const statusCode = err?.status || err?.response?.status || 500;
    const errorMessage = err?.message || 'Failed to load saved recipes.';

    error(statusCode, errorMessage);
  }
}
