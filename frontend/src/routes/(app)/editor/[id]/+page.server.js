import { api } from '$lib/server/api';
import { fail } from '@sveltejs/kit';

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
      notes: form.get('notes'),
      storage: form.get('storage'),
      tags: form
        .get('tags')
        ?.split(',')
        .map((x) => x.trim())
        .filter(Boolean),
      equipment: form
        .get('equipment')
        ?.split(',')
        .map((x) => x.trim())
        .filter(Boolean)
    };

    try {
      await api(`/recipes/${params.id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      });

      return { success: true };
    } catch (err) {
      return fail(500, {
        error: 'Failed to save recipe'
      });
    }
  }
};
