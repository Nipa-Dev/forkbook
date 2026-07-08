import { api } from '$lib/server/api';
import { fail, redirect } from '@sveltejs/kit';

export async function load({ params, url, fetch }) {
  const tag = url.searchParams.get('tag');
  const search = url.searchParams.get('search');
  const layout = url.searchParams.get('layout') || 'A';

  const forwardParams = new URLSearchParams();
  if (tag) forwardParams.set('tag', tag);
  if (search) forwardParams.set('search', search);

  forwardParams.set('layout', layout);

  const queryString = forwardParams.toString() ? `?${forwardParams.toString()}` : '';

  const recipeData = await api(`/recipes/${params.id}${queryString}`, {}, fetch);

  return {
    recipe: recipeData,
    layout: layout
  };
}

export const actions = {
  rateRecipe: async ({ request, params, fetch, cookies }) => {
    const data = await request.formData();
    const rating = data.get('rating');

    if (!rating || isNaN(Number(rating)) || rating < 1 || rating > 5) {
      return fail(400, { message: 'Invalid rating value.' });
    }

    const token = cookies.get('session_token');
    if (!token) {
      return fail(401, { message: 'You must be logged in to rate recipes.' });
    }

    try {
      await api(
        `/rate/${params.id}`,
        {
          method: 'POST',
          body: JSON.stringify({
            rating: Number(rating)
          }),
          headers: {
            Authorization: `Bearer ${token}`
          }
        },
        fetch
      );

      return { success: true };
    } catch (error) {
      return fail(500, { message: 'Check server terminal logs.' });
    }
  }
};
