import { error } from '@sveltejs/kit';
import { api } from '$lib/server/api';

export async function load({ fetch, cookies }) {
  const token = cookies.get('session_token');

  try {
    const recipes = await api(
      '/recipes/saved?flag_type=made',
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
    console.error(error);
    const statusCode = error?.status || error?.response?.status || 500;
    const errororMessage = error?.message || 'Failed to load saved recipes.';

    error(statusCode, errorMessage);
  }
}
