import { api } from '$lib/server/api';
import { parseRecipeFormData } from '$lib/server/recipe-form';
import { fail, redirect } from '@sveltejs/kit';

export async function load({ params }) {
  const recipe = await api(`/recipes/${params.id}`);

  return { recipe };
}

export const actions = {
  save: async ({ request, params }) => {
    const data = await request.formData();
    const payload = parseRecipeFormData(data);

    try {
      await api(`/recipes/${params.id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      });

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

      return fail(500, {
        error: 'Failed to save recipe'
      });
    }

    throw redirect(303, `/recipes/${params.id}`);
  }
};
