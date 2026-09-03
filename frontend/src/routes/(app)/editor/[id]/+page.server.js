import { api } from '$lib/server/api';
import { fail, redirect } from '@sveltejs/kit';

export async function load({ params }) {
  const recipe = await api(`/recipes/${params.id}`);

  return {
    recipe
  };
}

export const actions = {
  save: async ({ request, params }) => {
    const form = await request.formData();

    const payload = {
      title: form.get('title'),
      description: form.get('description'),
      difficulty: form.get('difficulty'),
      image_url: form.get('image_url'),

      difficulty: data.get('difficulty')?.toString() || 'easy',

      prep_time_minutes: parseNumber(data.get('prep_time_minutes')),
      cook_time_minutes: parseNumber(data.get('cook_time_minutes')),
      servings: parseNumber(data.get('servings')),

      tags: parseArray(data.get('tags')),
      equipment: parseArray(data.get('equipment')),

      notes: parseArray(data.get('notes'), '\n'),
      storage: parseArray(data.get('storage'), '\n'),

      components: parseComponents(data.get('components'))
    };

    try {
      await api(`/recipes/${params.id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      });

      // Upload image only if one was selected
      const image = data.get('image');

      if (image instanceof File && image.size > 0) {
        const imageData = new FormData();
        imageData.append('image', image);

        await api(`/recipes/${params.id}/image`, {
          method: 'PUT',
          body: imageData
        });
      }
    } catch (err) {
      console.error('API Save Error:', err);

      return fail(err?.status ?? 500, {
        error: 'Failed to save recipe'
      });
    }

    throw redirect(303, `/recipes/${params.id}`);
  }
};
