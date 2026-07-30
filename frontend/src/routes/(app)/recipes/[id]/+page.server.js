import { api } from '$lib/server/api';
import { fail } from '@sveltejs/kit';

export async function load({ cookies, params, url, fetch, locals }) {
  const tag = url.searchParams.get('tag');
  const search = url.searchParams.get('search');
  const layout = url.searchParams.get('layout') || 'A';

  const forwardParams = new URLSearchParams();
  if (tag) forwardParams.set('tag', tag);
  if (search) forwardParams.set('search', search);
  forwardParams.set('layout', layout);

  const queryString = forwardParams.toString() ? `?${forwardParams.toString()}` : '';

  const recipeData = await api(`/recipes/${params.id}${queryString}`, {}, fetch);

  let is_bookmarked = false;
  let is_made = false;

  if (locals.isAuthenticated) {
    const token = cookies.get('session_token');
    try {
      // Fetches both bookmarks and made flags
      const flags = await api(
        '/recipes/saved',
        { headers: { Authorization: `Bearer ${token}` } },
        fetch
      );

      is_bookmarked = flags.some((f) => f.recipe_id === params.id && f.flag_type === 'bookmark');
      is_made = flags.some((f) => f.recipe_id === params.id && f.flag_type === 'made');
    } catch (error) {
      console.error('Failed to fetch user flags status:', error);
    }
  }

  return {
    recipe: {
      ...recipeData,
      is_bookmarked,
      is_made
    },
    layout: layout
  };
}

export const actions = {
  rateRecipe: async ({ request, params, fetch, cookies, locals }) => {
    if (!locals.isAuthenticated) {
      return fail(401, { message: 'You must be logged in to rate recipes.' });
    }
    const data = await request.formData();
    const rating = data.get('rating');

    if (!rating || isNaN(Number(rating)) || rating < 1 || rating > 5) {
      return fail(400, { message: 'Invalid rating value.' });
    }

    const token = cookies.get('session_token');
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
    } catch {
      return fail(500, { message: 'Check server terminal logs.' });
    }
  },

  toggleBookmark: async ({ request, params, fetch, cookies, locals }) => {
    if (!locals.isAuthenticated) {
      return fail(401, { message: 'You must be logged in to bookmark recipes.' });
    }

    const data = await request.formData();
    const active = data.get('active') === 'true';

    const token = cookies.get('session_token');
    try {
      await api(
        `/recipes/${params.id}/toggle-saved`,
        {
          method: 'POST',
          body: JSON.stringify({
            active: active,
            flag_type: 'bookmark'
          }),
          headers: {
            Authorization: `Bearer ${token}`
          }
        },
        fetch
      );
      return { success: true };
    } catch {
      return fail(500, { message: 'Failed to update bookmark status.' });
    }
  },
  toggleMade: async ({ request, params, fetch, cookies, locals }) => {
    if (!locals.isAuthenticated) {
      return fail(401, { message: 'You must be logged in to track cooked recipes.' });
    }
    const data = await request.formData();
    const active = data.get('active') === 'true';

    const token = cookies.get('session_token');
    try {
      await api(
        `/recipes/${params.id}/toggle-saved`,
        {
          method: 'POST',
          body: JSON.stringify({
            active: active,
            flag_type: 'made'
          }),
          headers: {
            Authorization: `Bearer ${token}`
          }
        },
        fetch
      );
      return { success: true };
    } catch {
      return fail(500, { message: 'Failed to update recipe progress status.' });
    }
  }
};
